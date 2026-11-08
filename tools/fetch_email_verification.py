#!/usr/bin/env python3
"""Universal Email Verification & OTP Retriever for Autonomous Job Applications.

Enables the autonomous browser bot to handle email verifications:
1. Retrieve OTP/verification passcodes (4-8 digits)
2. Retrieve account activation/confirmation links
3. Scans Gmail via IMAP using existing verified credentials
"""

import argparse
import email
import imaplib
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_env():
    for fn in [".env", "jobs.env", "jobs.env.txt"]:
        p = REPO_ROOT / fn
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if "PASS" in k.upper():
                        v = v.replace(" ", "")
                    if k not in os.environ:
                        os.environ[k] = v


load_env()

SMTP_USER = os.environ.get("SMTP_USER", "hsn96srhan@gmail.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", "")).replace(" ", "")


def connect_imap():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(SMTP_USER, SMTP_PASSWORD)
    mail.select("inbox")
    return mail


def get_latest_otp(sender_filter=None, max_messages=10):
    mail = connect_imap()
    try:
        status, messages = mail.search(None, "ALL")
        if not messages or not messages[0]:
            return None

        msg_ids = messages[0].split()
        target_ids = msg_ids[-max_messages:]
        target_ids.reverse()  # check newest first

        for mid in target_ids:
            _, data = mail.fetch(mid, "(RFC822)")
            raw_msg = data[0][1]
            msg = email.message_from_bytes(raw_msg)

            subject = msg.get("Subject", "")
            sender = msg.get("From", "")

            if sender_filter and sender_filter.lower() not in sender.lower() and sender_filter.lower() not in subject.lower():
                continue

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type in ["text/plain", "text/html"]:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode("utf-8", errors="ignore") + "\n"
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")

            text = f"{subject}\n{body}"

            # Check if this email is an identity/verification email
            verification_keywords = [
                "verification", "verify", "passcode", "code", "one-time", "otp",
                "identity", "confirm", "activate", "رمز التحقق", "كود", "تحقق"
            ]

            if not any(k in text.lower() for k in verification_keywords):
                continue

            # Find 4 to 8 digit codes
            codes = re.findall(r"\b\d{4,8}\b", body)
            # Filter out obvious false positives like years (2025, 2026), common port numbers (51333), or dummy numbers
            valid_codes = [
                c for c in codes
                if c not in ["2024", "2025", "2026", "2027", "333333", "100000", "111111", "123456", "000000"]
            ]

            if valid_codes:
                return valid_codes[-1]  # or the most prominent code

        return None
    finally:
        mail.close()
        mail.logout()


def get_latest_verification_link(sender_filter=None, max_messages=10):
    mail = connect_imap()
    try:
        status, messages = mail.search(None, "ALL")
        if not messages or not messages[0]:
            return None

        msg_ids = messages[0].split()
        target_ids = msg_ids[-max_messages:]
        target_ids.reverse()

        for mid in target_ids:
            _, data = mail.fetch(mid, "(RFC822)")
            raw_msg = data[0][1]
            msg = email.message_from_bytes(raw_msg)

            subject = msg.get("Subject", "")
            sender = msg.get("From", "")

            if sender_filter and sender_filter.lower() not in sender.lower() and sender_filter.lower() not in subject.lower():
                continue

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type in ["text/plain", "text/html"]:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode("utf-8", errors="ignore") + "\n"
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")

            # Look for verification or confirmation URLs
            links = re.findall(r'https?://[^\s<>\"\'\)]+', body)
            verify_links = [
                l for l in links
                if any(k in l.lower() for k in ["verify", "confirm", "activate", "activation", "token=", "auth="])
                and not any(x in l.lower() for x in ["unsubscribe", "privacy", "facebook", "twitter", "linkedin"])
            ]

            if verify_links:
                return verify_links[0]

        return None
    finally:
        mail.close()
        mail.logout()


def main():
    parser = argparse.ArgumentParser(description="Fetch email verification codes or links")
    parser.add_argument("--otp", action="store_true", help="Retrieve latest OTP/verification code")
    parser.add_argument("--link", action="store_true", help="Retrieve latest verification/activation link")
    parser.add_argument("--sender", type=str, default=None, help="Filter by sender keyword")

    args = parser.parse_args()

    if args.link:
        link = get_latest_verification_link(args.sender)
        if link:
            print(link)
            sys.exit(0)
        sys.exit(1)
    else:
        # Default to OTP
        code = get_latest_otp(args.sender)
        if code:
            print(code)
            sys.exit(0)
        sys.exit(1)


if __name__ == "__main__":
    main()


#!/usr/bin/env python3
import os
import email
import imaplib
import re
import time
from pathlib import Path

def load_env():
    for fn in [".env", "jobs.env", "jobs.env.txt"]:
        p = Path(fn)
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("\"'")
                    if "PASS" in k.upper():
                        v = v.replace(" ", "")
                    if k not in os.environ:
                        os.environ[k] = v

load_env()

user = os.environ.get("SMTP_USER", "hsn96srhan@gmail.com")
pwd = os.environ.get("SMTP_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", "")).replace(" ", "")

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(user, pwd)

for folder in ['"INBOX"', '"[Gmail]/Spam"', '"[Gmail]/All Mail"']:
    print(f"--- Checking {folder} ---")
    status, _ = mail.select(folder)
    if status != "OK":
        continue
    status, messages = mail.search(None, "ALL")
    if not messages or not messages[0]:
        continue
    ids = messages[0].split()
    print(f"Messages count: {len(ids)}")
    for mid in reversed(ids[-5:]):
        _, data = mail.fetch(mid, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        subj = msg.get("Subject", "")
        frm = msg.get("From", "")
        date = msg.get("Date", "")
        print(f"ID: {mid.decode()} | From: {frm} | Subject: {subj} | Date: {date}")
        if any(k in frm.lower() or k in subj.lower() for k in ["bayt", "بيت", "password", "reset"]):
            print(">>> POTENTIAL MATCH FOUND! <<<")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() in ["text/plain", "text/html"]:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode("utf-8", errors="ignore") + "\n"
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
            links = re.findall(r'https?://[^\s<>"\']+', body)
            for l in links:
                if "bayt.com" in l:
                    print("LINK:", l)

mail.close()
mail.logout()

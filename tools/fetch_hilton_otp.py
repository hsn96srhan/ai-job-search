#!/usr/bin/env python3
import imaplib
import email
import re
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

for fn in ['.env', 'jobs.env', 'jobs.env.txt']:
    p = REPO_ROOT / fn
    if p.exists():
        for line in p.read_text().splitlines():
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('\'\"')

user = os.environ.get('SMTP_USER', 'hsn96srhan@gmail.com')
pwd = os.environ.get('SMTP_PASSWORD', os.environ.get('GMAIL_APP_PASSWORD', '')).replace(' ', '')

try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(user, pwd)
    mail.select('inbox')
    status, messages = mail.search(None, '(FROM "HiltonRecruitment")')
    msg_ids = messages[0].split()
    if msg_ids:
        latest_id = msg_ids[-1]
        _, data = mail.fetch(latest_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                elif part.get_content_type() == 'text/html' and not body:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        mail.close()
        mail.logout()
        codes = [c for c in re.findall(r'\b\d{6}\b', body) if c != '333333']
        if codes:
            print(codes[-1])
            sys.exit(0)
    mail.close()
    mail.logout()
except Exception as e:
    pass

sys.exit(1)


#!/usr/bin/env python3
"""Read briefing file and send via email (HTML) and Feishu (text)."""
import os
import re
import json
import time
import hashlib
import base64
import hmac
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

import requests
import markdown

BRIEFING_FILE = "/workspace/briefings/2026-07-06.md"
DATE = "2026-07-06"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
FEISHU_KEYWORD = "日报"


def read_briefing():
    with open(BRIEFING_FILE, "r", encoding="utf-8") as f:
        return f.read()


def send_email(md_text, html_body, attempt=1):
    subject = f"具身智能日报 {DATE}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("具身智能日报", SMTP_USER))
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(md_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Email send failed (attempt {attempt}): {e}")
        if attempt == 1:
            time.sleep(4)
            return send_email(md_text, html_body, attempt=2)
        return False


def feishu_signature(timestamp):
    if not FEISHU_SECRET:
        return ""
    string = f"{timestamp}\n{FEISHU_SECRET}"
    hmac_code = hmac.new(string.encode("utf-8"), digestmod=hashlib.sha256).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_feishu_text(text, attempt=1):
    timestamp = str(int(time.time()))
    payload = {"msg_type": "text", "content": {"text": text}}
    sig = feishu_signature(timestamp)
    url = FEISHU_WEBHOOK
    if sig:
        url += f"?timestamp={timestamp}&sign={sig}"
    try:
        resp = requests.post(url, json=payload, timeout=30)
        print(f"Feishu response: {resp.status_code} {resp.text}")
        if resp.status_code == 200 and resp.json().get("code") == 0:
            return True
        raise RuntimeError(f"Feishu error: {resp.text}")
    except Exception as e:
        print(f"Feishu send failed (attempt {attempt}): {e}")
        if attempt == 1:
            time.sleep(4)
            return send_feishu_text(text, attempt=2)
        return False


def split_feishu_messages(md_text):
    # Split by markdown H2 sections (## ) preserving the header with content.
    parts = re.split(r"(?=^## )", md_text, flags=re.MULTILINE)
    # First part is the title block before any ##.
    chunks = []
    current = parts[0].strip() if parts else ""
    for part in parts[1:]:
        if not current:
            current = part
        elif len(current) + len(part) + 2 > 15000:
            chunks.append(current)
            current = part
        else:
            current += "\n\n" + part
    if current:
        chunks.append(current)
    # Ensure keyword and prefix in every chunk.
    total = len(chunks)
    messages = []
    for i, chunk in enumerate(chunks, 1):
        prefix = f"具身智能日报 {DATE}"
        if total > 1:
            prefix += f" ({i}/{total})"
        if FEISHU_KEYWORD not in prefix:
            prefix = f"具身智能日报 {DATE}"
        # Ensure keyword appears in the body as well.
        if FEISHU_KEYWORD not in chunk:
            chunk = f"【日报】\n{chunk}"
        messages.append(f"{prefix}\n\n{chunk}")
    return messages


def main():
    md_text = read_briefing()
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    # Wrap in basic HTML body.
    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>具身智能日报 {DATE}</title></head>
<body style="font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto;">
{html_body}
</body>
</html>"""
    email_ok = send_email(md_text, html_body)
    messages = split_feishu_messages(md_text)
    feishu_ok = True
    for msg in messages:
        if not send_feishu_text(msg):
            feishu_ok = False
    print(f"Email OK: {email_ok}, Feishu OK: {feishu_ok}")
    return 0 if email_ok and feishu_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

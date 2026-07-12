#!/usr/bin/env python3
"""Send the full briefing via email (HTML) and Feishu (text).

Constants are taken from the automation prompt each run. The Feishu bot's
configured keyword is "简报" (not "日报"); titles still include "日报" per
user requirement, while the message body contains "简报" to pass the filter.
"""
import os
import re
import json
import time
import base64
import hmac
import hashlib
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import markdown

DATE = "2026-07-12"
BRIEFING_PATH = f"/workspace/briefings/{DATE}.md"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
# Feishu bot's configured keyword is "简报"; keep "日报" in titles.
FEISHU_KEYWORD = "简报"


def read_briefing():
    with open(BRIEFING_PATH, "r", encoding="utf-8") as f:
        return f.read()


def send_email(content_md):
    html = markdown.markdown(
        content_md,
        extensions=["extra", "nl2br", "tables"],
    )
    html = f"""<html>
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; color: #222; }}
h1 {{ color: #111; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
h2 {{ color: #333; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 6px; }}
h3 {{ color: #444; margin-top: 20px; }}
a {{ color: #0366d6; text-decoration: none; }}
blockquote {{ border-left: 4px solid #dfe2e5; padding-left: 16px; color: #6a737d; margin: 0; }}
ul {{ padding-left: 24px; }}
li {{ margin: 6px 0; }}
hr {{ border: none; border-top: 1px solid #e1e4e8; margin: 24px 0; }}
</style>
</head>
<body>
{html}
</body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"具身智能日报 {DATE}"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(content_md, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    for attempt in range(2):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            print("Email sent successfully")
            return True
        except Exception as e:
            print(f"Email attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                time.sleep(5)
    return False


def split_by_h2_sections(text):
    lines = text.splitlines()
    sections = []
    current = []
    for line in lines:
        if line.startswith("## "):
            if current:
                sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append("\n".join(current))
    # Prepend the header (before first ##) to the first section if it exists
    if not text.lstrip().startswith("## "):
        header_end = text.find("\n## ")
        if header_end > 0:
            header = text[:header_end].strip()
            if sections:
                sections[0] = header + "\n\n" + sections[0]
    return sections


def feishu_sign(timestamp):
    if not FEISHU_SECRET:
        return ""
    string_to_sign = f"{timestamp}\n{FEISHU_SECRET}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_feishu_text(text, title_suffix=""):
    title = f"简报 | 具身智能日报 {DATE}{title_suffix}"
    if FEISHU_KEYWORD and FEISHU_KEYWORD not in title:
        title = f"{FEISHU_KEYWORD} {title}"
    body = f"{title}\n\n{text}"
    if FEISHU_KEYWORD and FEISHU_KEYWORD not in body:
        body = f"{FEISHU_KEYWORD}\n{body}"
    timestamp = str(int(time.time()))
    payload = {
        "msg_type": "text",
        "content": {"text": body},
    }
    if FEISHU_SECRET:
        payload["timestamp"] = timestamp
        payload["sign"] = feishu_sign(timestamp)

    for attempt in range(2):
        try:
            resp = requests.post(
                FEISHU_WEBHOOK,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            print(f"Feishu response: {resp.status_code} {resp.text}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 0:
                    return True
                print(f"Feishu API error: {data}")
            if attempt == 0:
                time.sleep(5)
        except Exception as e:
            print(f"Feishu attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                time.sleep(5)
    return False


def send_feishu(content_md):
    MAX_LEN = 15000

    if len(content_md) <= MAX_LEN:
        return send_feishu_text(content_md)

    sections = split_by_h2_sections(content_md)
    total = len(sections)
    results = []
    for idx, section in enumerate(sections, start=1):
        suffix = f" {idx}/{total}"
        text = section
        if FEISHU_KEYWORD and FEISHU_KEYWORD not in text:
            text = f"{FEISHU_KEYWORD}\n{text}"
        if len(text) > MAX_LEN:
            sub_sections = re.split(r"\n(?=### )", text)
            for sub_idx, sub in enumerate(sub_sections, start=1):
                sub_suffix = f" {idx}.{sub_idx}/{total}"
                if len(sub) > MAX_LEN:
                    sub = sub[:MAX_LEN - 100] + "\n\n[内容过长，已截断]"
                results.append(send_feishu_text(sub, sub_suffix))
        else:
            results.append(send_feishu_text(text, suffix))
    return all(results)


if __name__ == "__main__":
    content = read_briefing()
    email_ok = send_email(content)
    feishu_ok = send_feishu(content)
    print(f"Email OK: {email_ok}, Feishu OK: {feishu_ok}")
    if not email_ok or not feishu_ok:
        raise SystemExit(1)

#!/usr/bin/env python3
"""Send the daily embodied AI briefing via email and Feishu."""
import sys
import os
import re
import time
import base64
import hmac
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import json
import urllib.request
import urllib.error
import markdown

DATE = "2026-07-30"
BRIEFING_PATH = f"/workspace/briefings/{DATE}.md"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
# Note: the user-provided constant is "日报", but the actual Feishu bot keyword is "简报".
FEISHU_KEYWORD = "简报"


def send_email(html_body, retries=1):
    subject = f"具身智能日报 {DATE}"
    msg = MIMEText(html_body, "html", "utf-8")
    msg["From"] = Header(f"{SMTP_USER} <{SMTP_USER}>", "utf-8")
    msg["To"] = Header(MAIL_TO, "utf-8")
    msg["Subject"] = Header(subject, "utf-8")

    last_err = None
    for attempt in range(retries + 1):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            print("Email sent successfully")
            return True
        except Exception as e:
            last_err = e
            print(f"Email attempt {attempt + 1} failed: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    print(f"Email failed after {retries + 1} attempts: {last_err}")
    return False


def feishu_sign(timestamp):
    if not FEISHU_SECRET:
        return None
    string = f"{timestamp}\n{FEISHU_SECRET}"
    hmac_code = hmac.new(
        FEISHU_SECRET.encode("utf-8"), string.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_feishu_text(text, title=None, retries=1):
    keyword = FEISHU_KEYWORD
    content = text
    if title:
        content = f"{title}\n\n{content}"
    # Ensure keyword appears prominently in the text body
    if keyword not in content:
        content = f"{keyword}\n\n{content}"
    else:
        # Add standalone keyword at the top to satisfy keyword filter robustly
        content = f"{keyword}\n\n{content}"

    timestamp = str(int(time.time()))
    payload = {
        "msg_type": "text",
        "content": {"text": content},
    }
    if FEISHU_SECRET:
        payload["timestamp"] = timestamp
        payload["sign"] = feishu_sign(timestamp)

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_err = None
    last_resp = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                FEISHU_WEBHOOK,
                data=data,
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_text = resp.read().decode("utf-8")
                print(f"Feishu response: {resp_text}")
                last_resp = resp_text
            try:
                resp_json = json.loads(last_resp)
                if resp_json.get("code") == 0:
                    print("Feishu message sent successfully")
                    return True
            except json.JSONDecodeError:
                pass
            last_err = Exception(f"Feishu returned non-zero code: {last_resp}")
            print(f"Feishu attempt {attempt + 1} failed: {last_err}")
            if attempt < retries:
                time.sleep(2 ** attempt)
        except Exception as e:
            last_err = e
            print(f"Feishu attempt {attempt + 1} failed: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    print(f"Feishu failed after {retries + 1} attempts: {last_err}")
    return False


def split_by_chapters(text, max_len=15000):
    # Split by lines starting with "## " (Markdown H2)
    pattern = re.compile(r"^(## .+)$", re.MULTILINE)
    parts = pattern.split(text)
    if len(parts) <= 1:
        return [text]

    chunks = []
    current = parts[0]
    for i in range(1, len(parts), 2):
        section = parts[i] + "\n" + parts[i + 1]
        if len(current) + len(section) + 1 > max_len:
            chunks.append(current)
            current = section
        else:
            current = current + "\n" + section
    if current:
        chunks.append(current)
    return chunks


def main():
    if not os.path.exists(BRIEFING_PATH):
        print(f"Briefing not found: {BRIEFING_PATH}")
        sys.exit(1)

    with open(BRIEFING_PATH, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Email: full markdown -> HTML
    html_body = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc", "nl2br"],
    )
    email_ok = send_email(html_body, retries=1)

    # Feishu: split if too long
    chunks = split_by_chapters(md_content, max_len=15000)
    feishu_ok = True
    total = len(chunks)
    for idx, chunk in enumerate(chunks, 1):
        title = f"简报 | 具身智能日报 {DATE} ({idx}/{total})"
        ok = send_feishu_text(chunk, title=title, retries=1)
        if not ok:
            feishu_ok = False
        time.sleep(1)

    if not email_ok or not feishu_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

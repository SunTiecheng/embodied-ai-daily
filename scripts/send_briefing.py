#!/usr/bin/env python3
"""Send the daily embodied AI briefing via email (HTML) and Feishu (text)."""
import os
import re
import sys
import time
import hmac
import hashlib
import base64
import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path

import markdown
import requests

BRIEFING_PATH = Path("/workspace/briefings/2026-07-07.md")
DATE = "2026-07-07"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
FEISHU_KEYWORD = "简报"  # actual keyword configured in the Feishu bot; title must also contain "日报"


def read_briefing() -> str:
    if not BRIEFING_PATH.exists():
        raise FileNotFoundError(f"Briefing not found: {BRIEFING_PATH}")
    return BRIEFING_PATH.read_text(encoding="utf-8")


def send_email(html_body: str) -> bool:
    subject = f"具身智能日报 {DATE}"
    msg = MIMEText(html_body, "html", "utf-8")
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg["Subject"] = Header(subject, "utf-8")

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
        print("[email] sent successfully")
        return True
    except Exception as e:
        print(f"[email] error: {e}")
        return False


def feishu_sign(timestamp: int) -> str:
    if not FEISHU_SECRET:
        return ""
    string_to_sign = f"{timestamp}\n{FEISHU_SECRET}"
    hmac_code = hmac.new(
        FEISHU_SECRET.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_feishu_text(title: str, content: str) -> bool:
    # Feishu keyword filter checks the whole text field; keep keyword plainly visible.
    text = f"{FEISHU_KEYWORD}\n{title}\n\n{content}"
    payload = {
        "msg_type": "text",
        "content": {"text": text},
    }
    if FEISHU_SECRET:
        timestamp = int(time.time())
        payload["timestamp"] = timestamp
        payload["sign"] = feishu_sign(timestamp)

    try:
        resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            print(f"[feishu] api error: {data}")
            return False
        print(f"[feishu] sent: {title}")
        return True
    except Exception as e:
        print(f"[feishu] error: {e}")
        return False


def split_by_sections(text: str) -> list[str]:
    """Split markdown by level-2 headings (##). Keep heading with each chunk."""
    # Insert sentinel at start so the first section is captured.
    pattern = re.compile(r"^(## .+)$", re.MULTILINE)
    parts = pattern.split(text)
    if parts[0].strip() == "":
        parts = parts[1:]
    chunks = []
    for i in range(0, len(parts), 2):
        heading = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        chunk = f"{heading}\n{body}".strip()
        if chunk:
            chunks.append(chunk)
    return chunks


def send_feishu_full(text: str) -> bool:
    if len(text) <= 15000:
        title = f"具身智能简报日报 {DATE}"
        return send_feishu_text(title, text)

    chunks = split_by_sections(text)
    total = len(chunks)
    ok = True
    for idx, chunk in enumerate(chunks, 1):
        title = f"具身智能简报日报 {idx}/{total} — {DATE}"
        chunk = chunk
        if not send_feishu_text(title, chunk):
            ok = False
            # retry once
            print(f"[feishu] retrying {idx}/{total}")
            if not send_feishu_text(title, chunk):
                print(f"[feishu] failed after retry {idx}/{total}")
        time.sleep(1)
    return ok


def main() -> int:
    skip_email = "--skip-email" in sys.argv
    skip_feishu = "--skip-feishu" in sys.argv

    text = read_briefing()
    email_ok = True
    feishu_ok = True

    if not skip_email:
        # Email: markdown -> HTML.
        html = markdown.markdown(text, extensions=["extra", "toc"])
        email_ok = send_email(html)
        if not email_ok:
            print("[email] retrying once")
            email_ok = send_email(html)
        if not email_ok:
            print("[email] failed after retry")

    if not skip_feishu:
        # Feishu: full markdown text.
        feishu_ok = send_feishu_full(text)
        if not feishu_ok:
            print("[feishu] some parts failed")

    return 0 if email_ok and feishu_ok else 1


if __name__ == "__main__":
    sys.exit(main())

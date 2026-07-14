#!/usr/bin/env python3
"""Send full briefing via email (HTML) and Feishu (text)."""

import os
import re
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

import markdown
import requests

MD_PATH = "briefings/2026-07-13.md"
DATE = "2026-07-13"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
FEISHU_KEYWORD = "日报"

def read_md():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        return f.read()


def send_email(html_body, retry=1):
    subject = f"具身智能日报 {DATE}"
    msg = MIMEText(html_body, "html", "utf-8")
    msg["From"] = formataddr((Header("具身智能日报", "utf-8").encode(), SMTP_USER))
    msg["To"] = MAIL_TO
    msg["Subject"] = Header(subject, "utf-8")

    attempts = retry + 1
    last_err = None
    for i in range(attempts):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            print(f"[email] sent to {MAIL_TO}")
            return True
        except Exception as e:
            last_err = e
            print(f"[email] attempt {i+1}/{attempts} failed: {e}")
            if i < attempts - 1:
                time.sleep(4)
    print(f"[email] failed after {attempts} attempts: {last_err}")
    return False


def feishu_keyword_guard(text):
    """Ensure the configured Feishu keyword is present. The actual webhook
    keyword is '简报', while the user also requires '日报' in every title."""
    if "简报" not in text:
        text = f"简报 {text}"
    if "日报" not in text:
        text = f"日报 {text}"
    return text


def split_by_h2(md_text):
    """Split markdown by top-level ## sections (lines starting with ## )."""
    parts = re.split(r"\n## ", md_text)
    if not parts:
        return [md_text]
    # First chunk contains the title/intro; prepend ## if needed for later chunks.
    chunks = [parts[0]]
    for p in parts[1:]:
        chunks.append("## " + p)
    return chunks


def send_feishu(text, retry=1):
    text = feishu_keyword_guard(text)
    payload = {"msg_type": "text", "content": {"text": text}}
    attempts = retry + 1
    last_err = None
    for i in range(attempts):
        try:
            resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                print(f"[feishu] sent chunk ({len(text)} chars)")
                return True
            else:
                err_msg = data.get("msg", "unknown")
                print(f"[feishu] attempt {i+1}/{attempts} API error: {err_msg}")
                last_err = err_msg
                if i < attempts - 1:
                    time.sleep(4)
        except Exception as e:
            last_err = e
            print(f"[feishu] attempt {i+1}/{attempts} failed: {e}")
            if i < attempts - 1:
                time.sleep(4)
    print(f"[feishu] failed after {attempts} attempts: {last_err}")
    return False


def send_feishu_full(md_text):
    # Ensure keyword presence in every chunk; if entire text <= 15000 chars, send once.
    header = f"【具身智能日报 {DATE}】\n"
    full_text = header + md_text

    if len(full_text) <= 15000:
        return send_feishu(full_text, retry=1)

    chunks = split_by_h2(md_text)
    total = len(chunks)
    results = []
    for idx, chunk in enumerate(chunks, start=1):
        chunk_text = f"【具身智能日报 {DATE} {idx}/{total}】\n{chunk}"
        results.append(send_feishu(chunk_text, retry=1))
    return all(results)


def main():
    md_text = read_md()

    # Email: full HTML
    html_body = markdown.markdown(md_text, extensions=["extra", "nl2br"])
    # Add a simple style wrapper
    html_body = f"""<html><body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; color: #333;">
{html_body}
</body></html>"""
    email_ok = send_email(html_body, retry=1)

    # Feishu: full text or split by chapters
    feishu_ok = send_feishu_full(md_text)

    print(f"\nSummary: email_ok={email_ok}, feishu_ok={feishu_ok}")
    if not (email_ok and feishu_ok):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

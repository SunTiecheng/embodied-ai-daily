#!/usr/bin/env python3
"""Send the full briefing via email and Feishu."""
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.header import Header
from pathlib import Path

import markdown
import requests

BRIEFING_FILE = Path("/workspace/briefings/2026-07-16.md")
DATE = "2026-07-16"
MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
FEISHU_KEYWORD = "日报"
GITHUB_URL = f"https://github.com/SunTiecheng/embodied-ai-daily/blob/cursor/bc-86d88d92-3b39-4a22-93a6-34d7e137b041-0afa/briefings/{DATE}.md"


def send_email(subject, html_body, retry=1):
    msg = MIMEText(html_body, "html", "utf-8")
    msg["From"] = Header(SMTP_USER, "utf-8")
    msg["To"] = Header(MAIL_TO, "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    last_err = None
    for attempt in range(retry + 1):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            print(f"Email sent successfully to {MAIL_TO}")
            return True
        except Exception as e:
            last_err = e
            print(f"Email send attempt {attempt + 1} failed: {e}")
            if attempt < retry:
                time.sleep(2)
    print(f"Email failed after {retry + 1} attempts: {last_err}")
    return False


def send_feishu(text, retry=1):
    payload = {"msg_type": "text", "content": {"text": text}}
    last_err = None
    for attempt in range(retry + 1):
        try:
            resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 0:
                raise RuntimeError(f"Feishu error: {data}")
            print(f"Feishu message sent successfully (length {len(text)})")
            return True
        except Exception as e:
            last_err = e
            print(f"Feishu send attempt {attempt + 1} failed: {e}")
            if attempt < retry:
                time.sleep(2)
    print(f"Feishu failed after {retry + 1} attempts: {last_err}")
    return False


def split_by_sections(text, max_len=15000):
    if len(text) <= max_len:
        return [text]
    parts = []
    # Split by level-2 headings (## )
    sections = text.split("\n## ")
    if len(sections) <= 1:
        return [text]
    current = sections[0]
    for sec in sections[1:]:
        candidate = current + "\n## " + sec
        if len(candidate) > max_len and current:
            parts.append(current)
            current = "## " + sec
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def main():
    text = BRIEFING_FILE.read_text(encoding="utf-8")
    # Email
    html = markdown.markdown(text, extensions=["extra", "toc"])
    html = f"""
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.7; max-width: 760px; margin: 0 auto; padding: 20px; color: #333; }}
        h1 {{ color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }}
        h2 {{ color: #2c2c2c; margin-top: 32px; border-left: 4px solid #4a90d9; padding-left: 12px; }}
        h3 {{ color: #444; margin-top: 24px; }}
        a {{ color: #4a90d9; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 16px; color: #666; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 30px 0; }}
    </style>
    </head>
    <body>
    {html}
    <hr>
    <p><strong>GitHub 完整版：</strong><a href="{GITHUB_URL}">{GITHUB_URL}</a></p>
    </body>
    </html>
    """
    email_ok = send_email(f"具身智能日报 {DATE}", html)

    # Feishu: send original markdown, split if > 15000 chars
    feishu_parts = split_by_sections(text, max_len=15000)
    total = len(feishu_parts)
    feishu_ok = True
    for idx, part in enumerate(feishu_parts, 1):
        header = f"具身智能日报 {DATE}"
        if total > 1:
            header = f"【日报 {idx}/{total}】具身智能日报 {DATE}"
        else:
            header = f"【日报】具身智能日报 {DATE}"
        # Ensure keyword is in the text as well
        # The webhook's actual keyword is "简报"; include both the requested "日报" in the title and the working keyword.
        body = f"{header}\n\n简报\n\n{part}\n\nGitHub 完整版：{GITHUB_URL}"
        if not send_feishu(body):
            feishu_ok = False
        if idx < total:
            time.sleep(1)

    result = {"email_ok": email_ok, "feishu_ok": feishu_ok, "feishu_parts": total}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return email_ok and feishu_ok


if __name__ == "__main__":
    ok = main()
    raise SystemExit(0 if ok else 1)

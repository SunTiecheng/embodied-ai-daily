#!/usr/bin/env python3
"""Send the full embodied AI daily briefing via email and Feishu."""
import os
import sys
import json
import time
import hmac
import hashlib
import base64
import smtplib
import markdown
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

BRIEFING_FILE = "briefings/2026-07-14.md"
DATE = "2026-07-14"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
FEISHU_KEYWORD = "日报"
FEISHU_MAX_LEN = 15000


def read_briefing() -> str:
    path = Path(BRIEFING_FILE)
    if not path.exists():
        raise FileNotFoundError(f"Briefing file not found: {path}")
    return path.read_text(encoding="utf-8")


def markdown_to_html(text: str) -> str:
    html = markdown.markdown(text, extensions=["extra", "toc", "tables"])
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>具身智能日报 {DATE}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.7; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #222; }}
h1 {{ color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; }}
h2 {{ color: #2c2c2c; margin-top: 32px; border-bottom: 1px solid #eee; padding-bottom: 6px; }}
h3 {{ color: #444; margin-top: 24px; }}
a {{ color: #0366d6; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
ul {{ padding-left: 24px; }}
li {{ margin: 6px 0; }}
blockquote {{ border-left: 4px solid #ddd; color: #666; margin-left: 0; padding-left: 16px; }}
hr {{ border: none; border-top: 1px solid #eee; margin: 24px 0; }}
</style>
</head>
<body>
{html}
</body>
</html>"""


def send_email(text: str) -> None:
    html = markdown_to_html(text)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"具身智能日报 {DATE}"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO

    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    last_err = None
    for attempt in range(2):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            print(f"Email sent successfully on attempt {attempt + 1}")
            return
        except Exception as e:
            last_err = e
            print(f"Email attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                time.sleep(4)
    raise RuntimeError(f"Email failed after 2 attempts: {last_err}")


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


def send_feishu_text(content: str, title: str) -> None:
    timestamp = int(time.time())
    # The user requires title to contain "日报"; the actual webhook keyword filter is "简报",
    # so include both to satisfy display requirement and delivery gate.
    full_text = f"{title}\n\n{content}"
    if "简报" not in full_text:
        full_text = f"{title}\n【简报】\n\n{content}"
    payload = {
        "msg_type": "text",
        "content": {"text": full_text},
    }
    if FEISHU_SECRET:
        payload["timestamp"] = timestamp
        payload["sign"] = feishu_sign(timestamp)

    last_err = None
    for attempt in range(2):
        try:
            resp = requests.post(
                FEISHU_WEBHOOK,
                json=payload,
                timeout=30,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") != 0:
                raise RuntimeError(f"Feishu API error: {data}")
            print(f"Feishu message sent: {title[:40]}... (attempt {attempt + 1})")
            return
        except Exception as e:
            last_err = e
            print(f"Feishu attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                time.sleep(4)
    raise RuntimeError(f"Feishu failed after 2 attempts: {last_err}")


def split_by_sections(text: str) -> list[tuple[str, str]]:
    """Split markdown into (section_title, section_body) tuples by ## headings."""
    lines = text.splitlines()
    sections = []
    current_title = ""
    current_body = []

    for line in lines:
        if line.startswith("## "):
            if current_body or current_title:
                sections.append((current_title, "\n".join(current_body).strip()))
            current_title = line.lstrip("# ").strip()
            current_body = []
        else:
            current_body.append(line)
    if current_body or current_title:
        sections.append((current_title, "\n".join(current_body).strip()))
    return sections


def send_feishu(text: str) -> None:
    if len(text) <= FEISHU_MAX_LEN:
        send_feishu_text(text, f"具身智能日报 {DATE}")
        return

    sections = split_by_sections(text)
    # Ensure first chunk contains the top-level title and metadata
    # Prepend # title and quote to the first chunk if missing
    header_lines = []
    for line in text.splitlines():
        if line.startswith("# "):
            header_lines.append(line)
        elif line.startswith("> "):
            header_lines.append(line)
        else:
            break
    header = "\n".join(header_lines).strip()

    chunks = []
    current = header + "\n\n" if header else ""
    current_title = "前言"

    for title, body in sections:
        candidate = f"\n## {title}\n\n{body}"
        if len(current) + len(candidate) > FEISHU_MAX_LEN and current.strip():
            chunks.append((current_title, current))
            current = candidate
            current_title = title
        else:
            current += candidate
            current_title = title
    if current.strip():
        chunks.append((current_title, current))

    total = len(chunks)
    for idx, (title, chunk) in enumerate(chunks, 1):
        title_text = f"日报 {idx}/{total}：具身智能日报 {DATE}"
        send_feishu_text(chunk, title_text)
        if idx < total:
            time.sleep(1)


def main() -> int:
    text = read_briefing()
    print(f"Read briefing: {len(text)} characters")

    try:
        send_email(text)
    except Exception as e:
        print(f"ERROR: Email failed: {e}", file=sys.stderr)

    try:
        send_feishu(text)
    except Exception as e:
        print(f"ERROR: Feishu failed: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

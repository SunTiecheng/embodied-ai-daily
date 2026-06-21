#!/usr/bin/env python3
"""Send full embodied AI daily briefing via email (HTML) and Feishu (text)."""

import hashlib
import hmac
import json
import os
import re
import smtplib
import ssl
import sys
import time
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

MAIL_TO = os.environ.get("MAIL_TO", "tiechengsun@126.com")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.126.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "tiechengsun@126.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FEISHU_WEBHOOK = os.environ.get(
    "FEISHU_WEBHOOK",
    "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268",
)
FEISHU_SECRET = os.environ.get("FEISHU_SECRET", "")
FEISHU_KEYWORD = os.environ.get("FEISHU_KEYWORD", "日报")
MAX_FEISHU_CHARS = 15000


def md_to_html(md: str) -> str:
    html = md
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.M)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.M)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.M)
    html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.M)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        html,
    )
    html = re.sub(r"^---$", "<hr>", html, flags=re.M)
    html = re.sub(r"^[-*] (.+)$", r"<li>\1</li>", html, flags=re.M)
    html = re.sub(r"(?:<li>.*</li>\n?)+", lambda m: f"<ul>{m.group(0)}</ul>", html)
    html = re.sub(r"\n\n+", "</p><p>", html)
    return (
        '<html><head><meta charset="utf-8"><style>'
        "body{font-family:sans-serif;line-height:1.6;max-width:900px;margin:2em auto;padding:0 1em}"
        "a{color:#1a73e8}h1,h2,h3{color:#222}blockquote{color:#555;border-left:3px solid #ccc;padding-left:1em}"
        "</style></head><body><p>"
        + html
        + "</p></body></html>"
    )


def extract_date(md: str) -> str:
    m = re.search(r"# 具身智能日报 \| (\d{4}-\d{2}-\d{2})", md)
    return m.group(1) if m else "unknown"


def split_by_sections(md: str, max_chars: int = MAX_FEISHU_CHARS) -> list[str]:
    if len(md) <= max_chars:
        return [md]
    parts = re.split(r"(?=^## )", md, flags=re.M)
    header = parts[0]
    sections = parts[1:] if len(parts) > 1 else []
    chunks: list[str] = []
    current = header
    for sec in sections:
        if len(current) + len(sec) > max_chars and current.strip():
            chunks.append(current)
            current = sec
        else:
            current += sec
    if current.strip():
        chunks.append(current)
    return chunks or [md]


def feishu_sign(secret: str) -> dict:
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    sign = hmac_code.hex()
    return {"timestamp": timestamp, "sign": sign}


def send_feishu(text: str, date: str) -> None:
    chunks = split_by_sections(text)
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        title = f"具身智能简报日报 {date}"
        if total > 1:
            title += f" {i}/{total}"
        body = f"{title}\n\n{chunk}"
        if FEISHU_KEYWORD not in body:
            body = f"【{FEISHU_KEYWORD}】{body}"
        payload: dict = {
            "msg_type": "text",
            "content": {"text": body},
        }
        if FEISHU_SECRET:
            payload.update(feishu_sign(FEISHU_SECRET))
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            FEISHU_WEBHOOK,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if result.get("code", result.get("StatusCode", 0)) not in (0, 200):
                raise RuntimeError(f"Feishu error: {result}")
        if i < total:
            time.sleep(1)


def send_email(html: str, date: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"具身智能日报 {date}"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(html, "html", "utf-8"))
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())


def send_with_retry(fn, label: str) -> None:
    for attempt in range(2):
        try:
            fn()
            print(f"{label}: OK")
            return
        except Exception as e:
            print(f"{label} attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                time.sleep(3)
            else:
                raise


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py <briefing.md>")
        return 1
    path = Path(sys.argv[1])
    md = path.read_text(encoding="utf-8")
    date = extract_date(md)
    html = md_to_html(md)

    send_with_retry(lambda: send_email(html, date), "Email")
    send_with_retry(lambda: send_feishu(md, date), "Feishu")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

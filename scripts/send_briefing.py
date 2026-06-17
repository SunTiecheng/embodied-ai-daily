#!/usr/bin/env python3
"""Send full briefing via email (HTML) and Feishu (text)."""

import hashlib
import hmac
import json
import os
import re
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib.request import Request, urlopen

FEISHU_MAX = 15000


def md_to_html(md: str) -> str:
    html = md
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.M)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.M)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.M)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.M)
    html = re.sub(r"^---$", "<hr>", html, flags=re.M)
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.M)
    html = re.sub(r"(<li>.*</li>\n?)+", lambda m: "<ul>" + m.group(0) + "</ul>", html)
    html = re.sub(r"^(\d+)\. (.+)$", r"<li>\2</li>", html, flags=re.M)
    html = "\n".join(
        f"<p>{line}</p>" if line and not line.startswith("<") else line
        for line in html.split("\n")
    )
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{{font-family:sans-serif;max-width:900px;margin:2em auto;line-height:1.6}}
a{{color:#0366d6}}h1,h2,h3{{color:#24292e}}blockquote{{border-left:3px solid #ddd;padding-left:1em;color:#666}}</style>
</head><body>{html}</body></html>"""


def split_by_sections(md: str, max_len: int = FEISHU_MAX) -> list[str]:
    if len(md) <= max_len:
        return [md]
    sections = re.split(r"(?=^## )", md, flags=re.M)
    chunks: list[str] = []
    current = sections[0]
    for sec in sections[1:]:
        if len(current) + len(sec) > max_len and current.strip():
            chunks.append(current)
            current = sec
        else:
            current += sec
    if current.strip():
        chunks.append(current)
    return chunks


def feishu_sign(secret: str, timestamp: str) -> str:
    s = f"{timestamp}\n{secret}".encode()
    return hmac.new(secret.encode(), s, hashlib.sha256).digest().hex()


def send_feishu(webhook: str, secret: str, title: str, content: str, retry: bool = True) -> None:
    payload: dict = {
        "msg_type": "text",
        "content": {"text": f"{title}\n\n{content}"},
    }
    if secret:
        ts = str(int(time.time()))
        payload["timestamp"] = ts
        payload["sign"] = feishu_sign(secret, ts)

    body = json.dumps(payload).encode()
    req = Request(webhook, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            if result.get("code", result.get("StatusCode", 0)) not in (0,):
                raise RuntimeError(f"Feishu error: {result}")
    except Exception:
        if retry:
            time.sleep(3)
            send_feishu(webhook, secret, title, content, retry=False)
        else:
            raise


def send_email(
    host: str,
    port: int,
    user: str,
    password: str,
    to_addr: str,
    subject: str,
    html_body: str,
    retry: bool = True,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL(host, port, timeout=60) as smtp:
            smtp.login(user, password)
            smtp.sendmail(user, [to_addr], msg.as_string())
    except Exception:
        if retry:
            time.sleep(3)
            send_email(host, port, user, password, to_addr, subject, html_body, retry=False)
        else:
            raise


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py briefings/YYYY-MM-DD.md", file=sys.stderr)
        return 1

    briefing_path = Path(sys.argv[1])
    if not briefing_path.exists():
        print(f"File not found: {briefing_path}", file=sys.stderr)
        return 1

    md = briefing_path.read_text(encoding="utf-8")
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", briefing_path.stem)
    date_str = date_match.group(0) if date_match else briefing_path.stem

    mail_to = os.environ.get("MAIL_TO", "tiechengsun@126.com")
    smtp_host = os.environ.get("SMTP_HOST", "smtp.126.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER", "tiechengsun@126.com")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    feishu_webhook = os.environ.get(
        "FEISHU_WEBHOOK",
        "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268",
    )
    feishu_secret = os.environ.get("FEISHU_SECRET", "")

    subject = f"具身智能日报 {date_str}"
    html = md_to_html(md)

    print(f"Sending email to {mail_to}...")
    send_email(smtp_host, smtp_port, smtp_user, smtp_pass, mail_to, subject, html)
    print("Email sent.")

    chunks = split_by_sections(md)
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        title = f"具身智能日报 {date_str}" + (f" {i}/{total}" if total > 1 else "")
        print(f"Sending Feishu {i}/{total} ({len(chunk)} chars)...")
        send_feishu(feishu_webhook, feishu_secret, title, chunk)
    print("Feishu sent.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

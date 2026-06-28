#!/usr/bin/env python3
"""Send full briefing via email (HTML) and Feishu webhook (text)."""

import hashlib
import hmac
import json
import os
import re
import smtplib
import sys
import time
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def md_to_html(md: str) -> str:
    html = md
    html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.M)
    html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.M)
    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.M)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.M)
    html = re.sub(r"^---$", r"<hr>", html, flags=re.M)
    html = re.sub(r"^(\d+)\. (.+)$", r"<p>\1. \2</p>", html, flags=re.M)
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.M)
    html = re.sub(r"(<li>.*</li>\n?)+", lambda m: "<ul>" + m.group(0) + "</ul>", html)
    html = re.sub(r"\n\n+", "<br><br>", html)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>body{{font-family:sans-serif;max-width:900px;margin:20px auto;line-height:1.6}}
a{{color:#1a73e8}}h1,h2,h3{{color:#333}}blockquote{{border-left:3px solid #ccc;padding-left:12px;color:#555}}</style>
</head><body>{html}</body></html>"""


def send_email(subject: str, md_content: str) -> None:
    host = os.environ.get("SMTP_HOST", "smtp.126.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")
    to_addr = os.environ.get("MAIL_TO", "")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(md_content, "plain", "utf-8"))
    msg.attach(MIMEText(md_to_html(md_content), "html", "utf-8"))

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())


def feishu_sign(secret: str, timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return hmac_code.hex()


def split_by_sections(md: str, max_len: int = 15000) -> list[str]:
    if len(md) <= max_len:
        return [md]
    parts = re.split(r"(?=^## )", md, flags=re.M)
    header = parts[0] if parts else ""
    sections = parts[1:] if len(parts) > 1 else []
    chunks: list[str] = []
    current = header
    for sec in sections:
        if len(current) + len(sec) > max_len and current.strip():
            chunks.append(current)
            current = sec
        else:
            current += sec
    if current.strip():
        chunks.append(current)
    return chunks


def send_feishu(md_content: str, date_str: str) -> None:
    webhook = os.environ.get("FEISHU_WEBHOOK", "")
    secret = os.environ.get("FEISHU_SECRET", "")
    keyword = os.environ.get("FEISHU_KEYWORD", "日报")

    chunks = split_by_sections(md_content)
    total = len(chunks)

    for i, chunk in enumerate(chunks, 1):
        title = f"具身智能简报日报 {date_str}"
        if total > 1:
            title += f" {i}/{total}"
        body = f"{title}\n\n{chunk}"
        if keyword not in body:
            body = f"【{keyword}】\n{body}"
        if "简报" not in body:
            body = f"【简报】\n{body}"

        payload: dict = {"msg_type": "text", "content": {"text": body}}
        if secret:
            ts = str(int(time.time()))
            payload["timestamp"] = ts
            payload["sign"] = feishu_sign(secret, ts)

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            if result.get("code", result.get("StatusCode", 0)) not in (0,):
                if "StatusCode" in result and result["StatusCode"] == 0:
                    continue
                raise RuntimeError(f"Feishu error: {result}")


def retry_once(fn, label: str) -> None:
    try:
        fn()
        print(f"{label}: OK")
    except Exception as e:
        print(f"{label}: failed ({e}), retrying...")
        time.sleep(3)
        fn()
        print(f"{label}: OK (retry)")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py briefings/YYYY-MM-DD.md")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        content = f.read()

    m = re.search(r"(\d{4}-\d{2}-\d{2})", path)
    date_str = m.group(1) if m else "unknown"
    subject = f"具身智能日报 {date_str}"

    retry_once(lambda: send_email(subject, content), "Email")
    retry_once(lambda: send_feishu(content, date_str), "Feishu")


if __name__ == "__main__":
    main()

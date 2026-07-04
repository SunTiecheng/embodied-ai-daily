#!/usr/bin/env python3
"""Send full embodied AI daily briefing via email (SMTP) and Feishu webhook."""

import hashlib
import hmac
import base64
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
from urllib.error import URLError, HTTPError

# Defaults from automation config
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
FEISHU_MAX_CHARS = 15000


def md_to_html(md: str) -> str:
    """Minimal Markdown to HTML converter for briefing content."""
    lines = md.split("\n")
    html_parts = [
        '<!DOCTYPE html><html><head><meta charset="utf-8">',
        "<style>body{font-family:sans-serif;line-height:1.6;max-width:900px;margin:2em auto;padding:0 1em;}"
        "h1,h2,h3{color:#1a1a2e;}a{color:#0066cc;}blockquote{border-left:4px solid #ccc;padding-left:1em;color:#555;}"
        "hr{border:none;border-top:1px solid #ddd;margin:2em 0;}</style></head><body>",
    ]
    in_list = False
    in_para = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_parts.append("</ul>")
            in_list = False

    def close_para():
        nonlocal in_para
        if in_para:
            html_parts.append("</p>")
            in_para = False

    def inline(text: str) -> str:
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        return text

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("# "):
            close_para()
            close_list()
            html_parts.append(f"<h1>{inline(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            close_para()
            close_list()
            html_parts.append(f"<h2>{inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            close_para()
            close_list()
            html_parts.append(f"<h3>{inline(stripped[4:])}</h3>")
        elif stripped.startswith("> "):
            close_para()
            close_list()
            html_parts.append(f"<blockquote>{inline(stripped[2:])}</blockquote>")
        elif stripped == "---":
            close_para()
            close_list()
            html_parts.append("<hr>")
        elif stripped.startswith("- "):
            close_para()
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{inline(stripped[2:])}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            close_para()
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{inline(re.sub(r'^\\d+\\.\\s', '', stripped))}</li>")
        elif stripped == "":
            close_para()
            close_list()
        else:
            close_list()
            if not in_para:
                html_parts.append("<p>")
                in_para = True
            else:
                html_parts.append("<br>")
            html_parts.append(inline(stripped))

    close_para()
    close_list()
    html_parts.append("</body></html>")
    return "".join(html_parts)


def extract_date(md: str) -> str:
    m = re.search(r"具身智能日报\s*\|\s*(\d{4}-\d{2}-\d{2})", md)
    if m:
        return m.group(1)
    m = re.search(r"(\d{4}-\d{2}-\d{2})", md)
    return m.group(1) if m else "unknown"


def send_email(subject: str, html_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
    print(f"Email sent to {MAIL_TO}")


def feishu_sign(timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{FEISHU_SECRET}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def split_by_sections(md: str, max_chars: int) -> list[str]:
    """Split markdown by ## sections if total length exceeds max_chars."""
    if len(md) <= max_chars:
        return [md]

    header_match = re.match(r"(^#[^\n]*\n(?:>[^\n]*\n)?)", md, re.MULTILINE)
    header = header_match.group(1) if header_match else ""
    rest = md[len(header) :]

    sections = re.split(r"(?=^## )", rest, flags=re.MULTILINE)
    chunks: list[str] = []
    current = header

    for sec in sections:
        if not sec.strip():
            continue
        if len(current) + len(sec) > max_chars and current.strip() != header.strip():
            chunks.append(current.rstrip())
            current = header + sec
        else:
            current += sec

    if current.strip():
        chunks.append(current.rstrip())

    if len(chunks) == 1 and len(chunks[0]) > max_chars:
        # Fallback: hard split
        text = chunks[0]
        chunks = []
        for i in range(0, len(text), max_chars - 200):
            chunks.append(text[i : i + max_chars - 200])

    return chunks


def send_feishu_message(text: str) -> None:
    payload: dict = {"msg_type": "text", "content": {"text": text}}
    if FEISHU_SECRET:
        ts = str(int(time.time()))
        payload["timestamp"] = ts
        payload["sign"] = feishu_sign(ts)

    data = json.dumps(payload).encode("utf-8")
    req = Request(
        FEISHU_WEBHOOK,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
    if result.get("code", result.get("StatusCode", 0)) not in (0, 200):
        raise RuntimeError(f"Feishu error: {result}")
    print("Feishu message sent OK")


def send_feishu(md: str, date: str) -> None:
    # Include both keywords for webhook filter compatibility
    chunks = split_by_sections(md, FEISHU_MAX_CHARS)
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        title = f"具身智能简报日报 {date}"
        if total > 1:
            title += f" {i}/{total}"
        body = f"{title}\n\n{chunk}"
        if "简报" not in body:
            body = f"简报\n{body}"
        if FEISHU_KEYWORD and FEISHU_KEYWORD not in body:
            body = f"{FEISHU_KEYWORD}\n{body}"
        send_feishu_message(body)
        if i < total:
            time.sleep(1)


def retry_once(fn, label: str) -> None:
    try:
        fn()
    except Exception as e:
        print(f"{label} failed ({e}), retrying once...")
        time.sleep(2)
        fn()


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py <briefing.md>", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    md = path.read_text(encoding="utf-8")
    date = extract_date(md)
    subject = f"具身智能日报 {date}"
    html = md_to_html(md)

    retry_once(lambda: send_email(subject, html), "Email")
    retry_once(lambda: send_feishu(md, date), "Feishu")

    print("All notifications sent successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

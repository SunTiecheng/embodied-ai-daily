#!/usr/bin/env python3
"""Send full embodied AI daily briefing via email and Feishu."""

import hashlib
import hmac
import html
import os
import re
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import urllib.request
import json

# Configuration from environment or defaults
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
    """Convert Markdown briefing to HTML for email."""
    lines = md.split("\n")
    out = []
    in_list = False

    for line in lines:
        if line.startswith("# "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("> "):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append(f"<blockquote>{inline_md(line[2:])}</blockquote>")
        elif line.startswith("---"):
            if in_list:
                out.append("</ul>")
                in_list = False
            out.append("<hr>")
        elif re.match(r"^\d+\.\s", line):
            if not in_list:
                out.append("<ol>")
                in_list = "ol"
            content = re.sub(r"^\d+\.\s", "", line)
            out.append(f"<li>{inline_md(content)}</li>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = "ul"
            out.append(f"<li>{inline_md(line[2:])}</li>")
        elif line.strip() == "":
            if in_list:
                out.append(f"</{in_list}>")
                in_list = False
            out.append("<br>")
        else:
            if in_list:
                out.append(f"</{in_list}>")
                in_list = False
            out.append(f"<p>{inline_md(line)}</p>")

    if in_list:
        out.append(f"</{in_list}>")

    body = "\n".join(out)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #1a1a2e; border-bottom: 2px solid #4a90d9; padding-bottom: 8px; }}
h2 {{ color: #2c3e50; margin-top: 24px; }}
h3 {{ color: #34495e; }}
a {{ color: #2980b9; }}
blockquote {{ border-left: 4px solid #4a90d9; margin: 12px 0; padding: 8px 16px; background: #f8f9fa; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
</style></head><body>{body}</body></html>"""


def inline_md(text: str) -> str:
    """Handle inline markdown: links, bold."""
    text = html.escape(text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def send_email(subject: str, md_content: str) -> None:
    html_body = md_to_html(md_content)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(md_content, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
    print(f"Email sent to {MAIL_TO}")


def feishu_sign(timestamp: str) -> dict:
    if not FEISHU_SECRET:
        return {}
    string_to_sign = f"{timestamp}\n{FEISHU_SECRET}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    import base64

    sign = base64.b64encode(hmac_code).decode("utf-8")
    return {"timestamp": timestamp, "sign": sign}


def split_by_sections(md: str, max_chars: int = MAX_FEISHU_CHARS) -> list[str]:
    """Split briefing by ## sections if too long."""
    if len(md) <= max_chars:
        return [md]

    sections = re.split(r"(?=^## )", md, flags=re.MULTILINE)
    header = sections[0]
    chunks = []
    current = header

    for section in sections[1:]:
        if len(current) + len(section) > max_chars and current.strip():
            chunks.append(current)
            current = header + section
        else:
            current += section

    if current.strip():
        chunks.append(current)

    return chunks if chunks else [md]


def send_feishu_message(text: str, part_label: str = "") -> None:
    title_prefix = f"具身智能简报日报"
    if part_label:
        title = f"{title_prefix} {part_label}"
    else:
        title = title_prefix

    full_text = f"{title}\n\n{text}"
    if FEISHU_KEYWORD not in full_text:
        full_text = f"【{FEISHU_KEYWORD}】{full_text}"

    payload = {"msg_type": "text", "content": {"text": full_text}}
    timestamp = str(int(time.time()))
    extra = feishu_sign(timestamp)
    if extra:
        payload.update(extra)

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
    print(f"Feishu sent: {part_label or 'single message'}")


def send_feishu(md: str, date_str: str) -> None:
    chunks = split_by_sections(md)
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        label = f"{date_str} {i}/{total}" if total > 1 else date_str
        send_feishu_message(chunk, label)
        if i < total:
            time.sleep(1)


def retry_once(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"First attempt failed: {e}, retrying...")
        time.sleep(2)
        func(*args, **kwargs)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 send_briefing.py briefings/YYYY-MM-DD.md")
        sys.exit(1)

    briefing_path = Path(sys.argv[1])
    if not briefing_path.exists():
        print(f"File not found: {briefing_path}")
        sys.exit(1)

    md_content = briefing_path.read_text(encoding="utf-8")
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", briefing_path.name)
    date_str = date_match.group(1) if date_match else "unknown"
    subject = f"具身智能日报 {date_str}"

    retry_once(send_email, subject, md_content)
    retry_once(send_feishu, md_content, date_str)
    print("All notifications sent successfully.")


if __name__ == "__main__":
    main()

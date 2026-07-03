#!/usr/bin/env python3
"""Send full briefing via email (SMTP) and Feishu webhook."""

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

import urllib.request
import urllib.error

FEISHU_MAX_CHARS = 15000


def markdown_to_html(md: str) -> str:
    """Simple Markdown to HTML converter for briefing content."""
    lines = md.split("\n")
    html_parts = []
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

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# "):
            close_list()
            close_para()
            html_parts.append(f"<h1>{inline_format(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            close_list()
            close_para()
            html_parts.append(f"<h2>{inline_format(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            close_list()
            close_para()
            html_parts.append(f"<h3>{inline_format(stripped[4:])}</h3>")
        elif stripped.startswith("> "):
            close_list()
            close_para()
            html_parts.append(f"<blockquote>{inline_format(stripped[2:])}</blockquote>")
        elif stripped.startswith("---"):
            close_list()
            close_para()
            html_parts.append("<hr>")
        elif stripped.startswith("- "):
            close_para()
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{inline_format(stripped[2:])}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            close_para()
            if not in_list:
                html_parts.append("<ol>")
                in_list = True
            content = re.sub(r"^\d+\.\s", "", stripped)
            html_parts.append(f"<li>{inline_format(content)}</li>")
        elif stripped == "":
            close_list()
            close_para()
        else:
            close_list()
            if not in_para:
                html_parts.append("<p>")
                in_para = True
            else:
                html_parts.append("<br>")
            html_parts.append(inline_format(stripped))

    close_list()
    close_para()
    body = "\n".join(html_parts)
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #333; }}
h1 {{ color: #1a1a2e; border-bottom: 2px solid #4a90d9; padding-bottom: 8px; }}
h2 {{ color: #2c3e50; margin-top: 24px; }}
h3 {{ color: #34495e; }}
a {{ color: #2980b9; }}
blockquote {{ border-left: 4px solid #4a90d9; margin: 12px 0; padding: 8px 16px; background: #f8f9fa; }}
hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
li {{ margin-bottom: 4px; }}
</style></head><body>{body}</body></html>"""


def inline_format(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def split_by_sections(content: str, max_chars: int = FEISHU_MAX_CHARS) -> list[str]:
    """Split briefing by ## sections for Feishu message limits."""
    if len(content) <= max_chars:
        return [content]

    sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    if len(sections) <= 1:
        chunks = []
        for i in range(0, len(content), max_chars - 100):
            chunks.append(content[i : i + max_chars - 100])
        return chunks

    chunks = []
    current = sections[0]
    for section in sections[1:]:
        if len(current) + len(section) > max_chars and current.strip():
            chunks.append(current)
            current = section
        else:
            current += section
    if current.strip():
        chunks.append(current)
    return chunks


def feishu_sign(secret: str) -> tuple[int, str]:
    timestamp = int(time.time())
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), b"", digestmod=hashlib.sha256
    ).digest()
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return timestamp, sign


def send_feishu(webhook: str, secret: str, title: str, content: str, retry: bool = True) -> bool:
    chunks = split_by_sections(content)
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        part_title = f"{title} {i}/{total}" if total > 1 else title
        text = f"{part_title}\n\n{chunk}"
        payload = {"msg_type": "text", "content": {"text": text}}
        if secret:
            ts, sign = feishu_sign(secret)
            payload["timestamp"] = str(ts)
            payload["sign"] = sign

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                if result.get("code", result.get("StatusCode", 0)) not in (0, 200):
                    print(f"Feishu error: {result}", file=sys.stderr)
                    if retry:
                        time.sleep(2)
                        return send_feishu(webhook, secret, title, content, retry=False)
                    return False
        except Exception as e:
            print(f"Feishu send failed: {e}", file=sys.stderr)
            if retry:
                time.sleep(2)
                return send_feishu(webhook, secret, title, content, retry=False)
            return False
        if i < total:
            time.sleep(1)
    return True


def send_email(
    host: str,
    port: int,
    user: str,
    password: str,
    to_addr: str,
    subject: str,
    html_body: str,
    retry: bool = True,
) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(host, port, timeout=30) as server:
            server.login(user, password)
            server.sendmail(user, [to_addr], msg.as_string())
        return True
    except Exception as e:
        print(f"Email send failed: {e}", file=sys.stderr)
        if retry:
            time.sleep(2)
            return send_email(host, port, user, password, to_addr, subject, html_body, retry=False)
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py briefings/YYYY-MM-DD.md", file=sys.stderr)
        sys.exit(1)

    briefing_path = Path(sys.argv[1])
    if not briefing_path.exists():
        print(f"File not found: {briefing_path}", file=sys.stderr)
        sys.exit(1)

    content = briefing_path.read_text(encoding="utf-8")
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", briefing_path.stem)
    date_str = date_match.group(0) if date_match else briefing_path.stem

    mail_to = os.environ.get("MAIL_TO", "tiechengsun@126.com")
    smtp_host = os.environ.get("SMTP_HOST", "smtp.126.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER", "tiechengsun@126.com")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    feishu_webhook = os.environ.get("FEISHU_WEBHOOK", "")
    feishu_secret = os.environ.get("FEISHU_SECRET", "")

    subject = f"具身智能日报 {date_str}"
    feishu_title = f"具身智能简报日报 {date_str}"

    html_body = markdown_to_html(content)

    print("Sending email...")
    email_ok = send_email(smtp_host, smtp_port, smtp_user, smtp_pass, mail_to, subject, html_body)
    print(f"Email: {'OK' if email_ok else 'FAILED'}")

    if feishu_webhook:
        print("Sending Feishu...")
        feishu_ok = send_feishu(feishu_webhook, feishu_secret, feishu_title, content)
        print(f"Feishu: {'OK' if feishu_ok else 'FAILED'}")
    else:
        feishu_ok = True
        print("Feishu webhook not set, skipping.")

    if not email_ok or not feishu_ok:
        sys.exit(1)
    print("All notifications sent successfully.")


if __name__ == "__main__":
    main()

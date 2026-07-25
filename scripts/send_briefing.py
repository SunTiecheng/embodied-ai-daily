#!/usr/bin/env python3
"""Send the full embodied AI briefing via email (HTML) and Feishu (text)."""
import os
import re
import smtplib
import time
from email.mime.text import MIMEText
from email.utils import formatdate
from urllib.parse import urlencode
import requests

DATE = "2026-07-25"
BRIEFING_PATH = f"/workspace/briefings/{DATE}.md"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"

FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
FEISHU_KEYWORD = "日报"


def md_to_html(md: str) -> str:
    """Convert a subset of Markdown to HTML."""
    # Escape HTML entities
    text = md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Convert links: [text](url)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r'<a href="\2">\1</a>', text)

    # Bold: **text**
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)

    # Italic: *text* (avoid matching ** already handled)
    text = re.sub(r"(?<!\*)\*([^\*]+)\*(?!\*)", r"<em>\1</em>", text)

    # Headings
    lines = text.split("\n")
    out = []
    in_list = False
    list_type = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                out.append(f"</{list_type}>")
                in_list = False
                list_type = None
            out.append("")
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            if in_list:
                out.append(f"</{list_type}>")
                in_list = False
                list_type = None
            level = len(m.group(1))
            out.append(f"<h{level}>{m.group(2)}</h{level}>")
            continue

        # List item
        m = re.match(r"^[-*]\s+(.*)$", stripped)
        if m:
            if not in_list:
                list_type = "ul"
                out.append("<ul>")
                in_list = True
            item = m.group(1)
            # Numbered sub-list inside item is handled as plain text here
            out.append(f"<li>{item}</li>")
            continue

        # Numbered list item
        m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m:
            if not in_list:
                list_type = "ol"
                out.append("<ol>")
                in_list = True
            out.append(f"<li>{m.group(2)}</li>")
            continue

        # Blockquote
        m = re.match(r"^>\s*(.*)$", stripped)
        if m:
            if in_list:
                out.append(f"</{list_type}>")
                in_list = False
                list_type = None
            out.append(f"<blockquote>{m.group(1)}</blockquote>")
            continue

        # Plain paragraph
        if in_list:
            out.append(f"</{list_type}>")
            in_list = False
            list_type = None
        out.append(f"<p>{stripped}</p>")

    if in_list:
        out.append(f"</{list_type}>")

    body = "\n".join(out)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>具身智能日报 {DATE}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #222; max-width: 720px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #1a1a1a; border-bottom: 2px solid #333; padding-bottom: 8px; }}
h2 {{ color: #2c2c2c; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-top: 32px; }}
h3 {{ color: #444; margin-top: 24px; }}
a {{ color: #0366d6; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
ul, ol {{ padding-left: 24px; }}
li {{ margin-bottom: 8px; }}
blockquote {{ background: #f6f8fa; border-left: 4px solid #ccc; padding: 10px 14px; margin: 0; color: #555; }}
strong {{ color: #111; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def send_email(html: str, retries: int = 1):
    subject = f"具身智能日报 {DATE}"
    msg = MIMEText(html, "html", "utf-8")
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    for attempt in range(retries + 1):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            print(f"Email sent successfully to {MAIL_TO}")
            return True
        except Exception as e:
            print(f"Email attempt {attempt + 1} failed: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                print("Email delivery failed after retries")
                return False


def split_feishu(text: str, max_len: int = 15000):
    """Split text by ## sections so each part is <= max_len and contains keyword."""
    if len(text) <= max_len:
        return [text]

    # Split by top-level sections (##)
    sections = re.split(r"\n(?=##\s+)", text)
    if len(sections) <= 1:
        # Hard split if no sections
        return [text[i:i + max_len] for i in range(0, len(text), max_len)]

    parts = []
    current = ""
    for section in sections:
        if len(section) > max_len:
            # Section itself too long; flush current then split section
            if current:
                parts.append(current)
                current = ""
            parts.extend([section[i:i + max_len] for i in range(0, len(section), max_len)])
            continue
        if len(current) + len(section) + 1 > max_len:
            parts.append(current)
            current = section
        else:
            current = current + "\n" + section if current else section
    if current:
        parts.append(current)
    return parts


def send_feishu(text: str, retries: int = 1):
    parts = split_feishu(text, 15000)
    total = len(parts)
    for idx, part in enumerate(parts, start=1):
        title = f"具身智能日报 {DATE}"
        if total > 1:
            title = f"{title} {idx}/{total}"
        # The bot's keyword filter is "简报", while the user also requires "日报" in titles.
        # Ensure both appear in the message text so the keyword check passes and the title rule is met.
        body = f"{FEISHU_KEYWORD} 简报\n\n{part.strip()}"
        payload = {
            "msg_type": "text",
            "content": {
                "text": f"{title} 简报\n\n{body}"
            }
        }
        for attempt in range(retries + 1):
            try:
                resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                if data.get("code") != 0:
                    raise RuntimeError(f"Feishu error: {data}")
                print(f"Feishu part {idx}/{total} sent successfully")
                break
            except Exception as e:
                print(f"Feishu part {idx}/{total} attempt {attempt + 1} failed: {e}")
                if attempt < retries:
                    time.sleep(2 ** attempt)
                else:
                    print(f"Feishu part {idx}/{total} failed after retries")


def main():
    with open(BRIEFING_PATH, "r", encoding="utf-8") as f:
        md = f.read()

    html = md_to_html(md)
    send_email(html)
    send_feishu(md)


if __name__ == "__main__":
    main()

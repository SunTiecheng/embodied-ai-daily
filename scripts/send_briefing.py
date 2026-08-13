#!/usr/bin/env python3
"""Send the daily embodied AI briefing via email and Feishu."""
import os
import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import markdown
import requests


# Constants from the automation prompt
BRIEFING_DATE = "2026-08-13"
BRIEFING_PATH = Path("/workspace/briefings") / f"{BRIEFING_DATE}.md"
MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""
FEISHU_KEYWORD = "日报"
FEISHU_MAX_LENGTH = 15000


def read_briefing() -> str:
    return BRIEFING_PATH.read_text(encoding="utf-8")


def markdown_to_html(md_text: str) -> str:
    html_body = markdown.markdown(
        md_text,
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
            "markdown.extensions.nl2br",
        ],
    )
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>具身智能日报 {BRIEFING_DATE}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; line-height: 1.6; color: #222; max-width: 720px; margin: 40px auto; padding: 0 20px; }}
h1 {{ color: #111; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }}
h2 {{ color: #222; margin-top: 28px; border-bottom: 1px solid #eee; padding-bottom: 6px; }}
h3 {{ color: #333; margin-top: 20px; }}
a {{ color: #0066cc; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
blockquote {{ border-left: 4px solid #ddd; padding-left: 12px; color: #555; margin: 0; }}
ul, ol {{ padding-left: 24px; }}
li {{ margin-bottom: 6px; }}
hr {{ border: none; border-top: 1px solid #eee; margin: 24px 0; }}
strong {{ color: #000; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""


def send_email(html_content: str) -> None:
    subject = f"具身智能日报 {BRIEFING_DATE}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, MAIL_TO, msg.as_string())


def split_for_feishu(text: str) -> list[str]:
    """Split briefing by top-level ## sections if total length exceeds FEISHU_MAX_LENGTH."""
    if len(text) <= FEISHU_MAX_LENGTH:
        return [text]

    # Split by lines that start with ## followed by a space
    parts = re.split(r'(?m)^## ', text)
    # The first part may be empty or the preamble before the first ##
    chunks = []
    current = ""
    for part in parts:
        if not part.strip():
            continue
        section = "## " + part
        if len(current) + len(section) > FEISHU_MAX_LENGTH and current:
            chunks.append(current)
            current = section
        else:
            current += section
    if current:
        chunks.append(current)
    return chunks


def send_feishu(text: str) -> None:
    chunks = split_for_feishu(text)
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        if total > 1:
            header = f"具身智能日报 {BRIEFING_DATE} ({i}/{total})"
        else:
            header = f"具身智能日报 {BRIEFING_DATE}"
        # Ensure the keyword is present
        content = f"{header}\n\n{chunk}"
        if FEISHU_KEYWORD not in content:
            content = content.replace(header, f"{FEISHU_KEYWORD} {header}")

        payload = {
            "msg_type": "text",
            "content": {
                "text": content,
            },
        }
        resp = requests.post(FEISHU_WEBHOOK, json=payload, timeout=30)
        resp.raise_for_status()


def retry_once(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"First attempt failed for {func.__name__}: {e}")
        func(*args, **kwargs)


def main():
    md_text = read_briefing()
    html_content = markdown_to_html(md_text)

    retry_once(send_email, html_content)
    print("Email sent successfully.")

    retry_once(send_feishu, md_text)
    print("Feishu sent successfully.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Send full embodied AI daily briefing via email (HTML) and Feishu (text)."""

import hashlib
import hmac
import json
import os
import re
import smtplib
import sys
import time
import urllib.error
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    import markdown
except ImportError:
    markdown = None


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def md_to_html(text: str) -> str:
    if markdown:
        return markdown.markdown(
            text,
            extensions=["extra", "sane_lists", "tables", "nl2br"],
        )
    # Minimal fallback: escape and wrap paragraphs
    import html

    escaped = html.escape(text)
    return f"<pre style='font-family:sans-serif;white-space:pre-wrap'>{escaped}</pre>"


def split_feishu_messages(content: str, max_len: int = 15000) -> list[str]:
    if len(content) <= max_len:
        return [content]

    sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    if sections and not sections[0].startswith("## "):
        header = sections[0]
        sections = [header + s if i > 0 else s for i, s in enumerate(sections)]
    else:
        header = ""

    chunks: list[str] = []
    current = header if header else ""

    for section in sections:
        if section == header:
            continue
        if len(current) + len(section) <= max_len:
            current += section
        else:
            if current.strip():
                chunks.append(current.rstrip())
            if len(section) <= max_len:
                current = (header if not chunks else "") + section
            else:
                # Hard split long section
                part = section
                while len(part) > max_len:
                    chunks.append(part[:max_len])
                    part = part[max_len:]
                current = part
    if current.strip():
        chunks.append(current.rstrip())
    return chunks


def feishu_sign(secret: str, timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    import base64

    return base64.b64encode(hmac_code).decode("utf-8")


def post_feishu(webhook: str, secret: str, body_text: str) -> None:
    payload: dict = {"msg_type": "text", "content": {"text": body_text}}
    if secret:
        ts = str(int(time.time()))
        payload["timestamp"] = ts
        payload["sign"] = feishu_sign(secret, ts)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        code = result.get("code")
        if code is None:
            code = result.get("StatusCode", 0)
        if code != 0:
            raise RuntimeError(f"Feishu error: {result}")


def send_feishu(text: str, title: str, retry: bool = True) -> None:
    webhook = env("FEISHU_WEBHOOK")
    secret = env("FEISHU_SECRET")
    keyword = env("FEISHU_KEYWORD", "简报")
    if not webhook:
        raise RuntimeError("FEISHU_WEBHOOK not set")

    chunks = split_feishu_messages(text)
    total = len(chunks)

    for i, chunk in enumerate(chunks, 1):
        part_title = f"日报 {i}/{total}" if total > 1 else "日报"
        body_text = f"具身智能简报日报 | {part_title}\n\n{chunk}"
        for kw in ("简报", keyword):
            if kw and kw not in body_text:
                body_text = f"{kw}\n\n{body_text}"

        try:
            post_feishu(webhook, secret, body_text)
        except Exception:
            if retry:
                time.sleep(2)
                post_feishu(webhook, secret, body_text)
            else:
                raise


def send_email(subject: str, html_body: str, retry: bool = True) -> None:
    mail_to = env("MAIL_TO", "tiechengsun@126.com")
    smtp_host = env("SMTP_HOST", "smtp.126.com")
    smtp_port = int(env("SMTP_PORT", "465"))
    smtp_user = env("SMTP_USER", "tiechengsun@126.com")
    smtp_pass = env("SMTP_PASS")
    if not smtp_pass:
        raise RuntimeError("SMTP_PASS not set")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = mail_to
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [mail_to], msg.as_string())
    except Exception:
        if retry:
            time.sleep(2)
            send_email(subject, html_body, retry=False)
        else:
            raise


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py briefings/YYYY-MM-DD.md", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    content = path.read_text(encoding="utf-8")
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    date_str = date_match.group(1) if date_match else path.stem

    subject = f"具身智能日报 {date_str}"
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.6; max-width: 900px; margin: 2em auto; padding: 0 1em; color: #222; }}
h1,h2,h3 {{ color: #111; }}
a {{ color: #0366d6; }}
blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 1em; color: #555; }}
code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
</style></head><body>
{md_to_html(content)}
</body></html>"""

    errors = []
    try:
        send_email(subject, html)
        print("Email sent successfully")
    except Exception as e:
        errors.append(f"Email failed: {e}")
        print(errors[-1], file=sys.stderr)

    try:
        send_feishu(content, "日报")
        print("Feishu sent successfully")
    except Exception as e:
        errors.append(f"Feishu failed: {e}")
        print(errors[-1], file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Send the daily embodied AI briefing via email (HTML) and Feishu (text)."""
import argparse
import base64
import hmac
import hashlib
import os
import re
import sys
import time
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from urllib import request, error
import smtplib


def md_to_html(md: str) -> str:
    lines = md.splitlines()
    blocks = []
    current = []
    for line in lines:
        if line.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    def inline(text: str) -> str:
        text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)
        return text

    out = []
    for block in blocks:
        first = block[0]
        if first.startswith("# "):
            out.append(f"<h1>{inline(first[2:])}</h1>")
        elif first.startswith("## "):
            out.append(f"<h2>{inline(first[3:])}</h2>")
        elif first.startswith("### "):
            out.append(f"<h3>{inline(first[4:])}</h3>")
        elif first.startswith("---"):
            out.append("<hr>")
        elif re.match(r"^\d+\.\s", first):
            items = []
            for line in block:
                m = re.match(r"^\d+\.\s+(.*)", line)
                if m:
                    items.append(f"<li>{inline(m.group(1))}</li>")
                else:
                    items.append(f"<li>{inline(line)}</li>")
            out.append(f"<ol>{''.join(items)}</ol>")
        elif first.startswith("- "):
            items = []
            for line in block:
                if line.startswith("- "):
                    items.append(f"<li>{inline(line[2:])}</li>")
                else:
                    items.append(f"<li>{inline(line)}</li>")
            out.append(f"<ul>{''.join(items)}</ul>")
        else:
            para = " ".join(block)
            out.append(f"<p>{inline(para)}</p>")

    body = "\n".join(out)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #222; max-width: 800px; margin: 0 auto; padding: 20px; }}
h1, h2, h3 {{ color: #111; margin-top: 1.4em; }}
a {{ color: #0366d6; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
ul, ol {{ padding-left: 1.4em; }}
hr {{ border: none; border-top: 1px solid #e1e4e8; margin: 2em 0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


def send_email(html: str, date_str: str) -> None:
    to = os.environ["MAIL_TO"]
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASS"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"具身智能日报 {date_str}"
    msg["From"] = user
    msg["To"] = to
    msg.attach(MIMEText(html, "html", _charset="utf-8"))

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(user, password)
        server.sendmail(user, [to], msg.as_string())


def feishu_sign(secret: str) -> tuple[str, str]:
    timestamp = str(int(time.time()))
    string_to_sign = f"{timestamp}\n{secret}"
    sign = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
    ).decode("utf-8")
    return timestamp, sign


def send_feishu(text: str, date_str: str) -> None:
    webhook = os.environ["FEISHU_WEBHOOK"]
    secret = os.environ.get("FEISHU_SECRET", "")
    keyword = os.environ.get("FEISHU_KEYWORD", "日报")

    # split by top-level sections if too long
    threshold = 15000
    if len(text) <= threshold:
        chunks = [text]
    else:
        chunks = []
        pattern = re.compile(r"^(##\s+.*)$", re.MULTILINE)
        parts = pattern.split(text)
        if parts[0].strip() == "":
            parts = parts[1:]
        # parts alternate: heading, body
        for i in range(0, len(parts), 2):
            heading = parts[i]
            body = parts[i + 1] if i + 1 < len(parts) else ""
            chunk = f"{heading}\n{body}".strip()
            if chunk:
                chunks.append(chunk)
        if not chunks:
            chunks = [text]

    total = len(chunks)
    for idx, chunk in enumerate(chunks, start=1):
        title = f"{keyword} {idx}/{total}" if total > 1 else keyword
        body = f"{title}\n\n{chunk}"
        payload = {
            "msg_type": "text",
            "content": {"text": body},
        }
        if secret:
            ts, sig = feishu_sign(secret)
            payload["timestamp"] = ts
            payload["sign"] = sig

        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            webhook,
            data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                resp.read()
        except error.HTTPError as e:
            raise RuntimeError(f"Feishu HTTP {e.code}: {e.read().decode('utf-8')}") from e


def retry_once(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"First attempt failed: {e}", file=sys.stderr)
        time.sleep(2)
        func(*args, **kwargs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("date", help="Briefing date in YYYY-MM-DD")
    parser.add_argument("--skip-email", action="store_true")
    parser.add_argument("--skip-feishu", action="store_true")
    args = parser.parse_args()

    file_path = Path(f"briefings/{args.date}.md")
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    md = file_path.read_text(encoding="utf-8")
    print(f"Sending briefing for {args.date} ({len(md)} chars)")

    if not args.skip_email:
        html = md_to_html(md)
        retry_once(send_email, html, args.date)
        print("Email sent.")

    if not args.skip_feishu:
        retry_once(send_feishu, md, args.date)
        print("Feishu sent.")


if __name__ == "__main__":
    main()

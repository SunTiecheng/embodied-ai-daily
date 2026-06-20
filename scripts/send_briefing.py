#!/usr/bin/env python3
"""Send full briefing via email (SMTP) and Feishu webhook."""

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
from urllib import error, request


def markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in lines:
        if line.startswith("### "):
            close_list()
            out.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            close_list()
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            close_list()
            out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("> "):
            close_list()
            out.append(f"<blockquote>{inline_md(line[2:])}</blockquote>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline_md(line[2:])}</li>")
        elif re.match(r"^\d+\.\s", line):
            close_list()
            text = re.sub(r"^\d+\.\s", "", line)
            out.append(f"<p>{inline_md(text)}</p>")
        elif line.strip() == "---":
            close_list()
            out.append("<hr>")
        elif line.strip() == "":
            close_list()
        else:
            close_list()
            out.append(f"<p>{inline_md(line)}</p>")

    close_list()
    body = "\n".join(out)
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<style>body{font-family:sans-serif;line-height:1.6;max-width:900px;margin:2em auto;padding:0 1em}"
        "a{color:#0366d6}blockquote{border-left:4px solid #ddd;margin:1em 0;padding-left:1em;color:#555}"
        "h1,h2,h3{margin-top:1.2em}</style></head><body>"
        f"{body}</body></html>"
    )


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def feishu_sign(secret: str, timestamp: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return hmac_code.hex()


def split_by_sections(content: str, max_len: int = 15000) -> list[str]:
    if len(content) <= max_len:
        return [content]

    sections = re.split(r"(?=^## )", content, flags=re.MULTILINE)
    if len(sections) == 1:
        chunks: list[str] = []
        start = 0
        while start < len(content):
            chunks.append(content[start : start + max_len])
            start += max_len
        return chunks

    chunks: list[str] = []
    current = sections[0]
    for sec in sections[1:]:
        if len(current) + len(sec) <= max_len:
            current += sec
        else:
            if current.strip():
                chunks.append(current)
            current = sec
    if current.strip():
        chunks.append(current)
    return chunks


def send_feishu(webhook: str, secret: str, title: str, content: str) -> None:
    payload: dict = {
        "msg_type": "text",
        "content": {"text": f"{title}\n\n{content}"},
    }
    if secret:
        timestamp = str(int(time.time()))
        payload["timestamp"] = timestamp
        payload["sign"] = feishu_sign(secret, timestamp)

    data = json_dumps(payload).encode("utf-8")
    req = request.Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")
        if '"StatusCode":0' not in body and '"code":0' not in body:
            raise RuntimeError(f"Feishu error: {body}")


def json_dumps(obj: dict) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


def send_email(
    host: str,
    port: int,
    user: str,
    password: str,
    to_addr: str,
    subject: str,
    html_body: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(host, port, timeout=60) as server:
        server.login(user, password)
        server.sendmail(user, [to_addr], msg.as_string())


def retry_once(fn, label: str) -> None:
    try:
        fn()
        print(f"{label}: OK")
    except Exception as exc:
        print(f"{label}: failed ({exc}), retrying...")
        time.sleep(2)
        fn()
        print(f"{label}: OK (retry)")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: send_briefing.py briefings/YYYY-MM-DD.md", file=sys.stderr)
        return 1

    briefing_path = Path(sys.argv[1])
    content = briefing_path.read_text(encoding="utf-8")
    date_match = re.search(r"(\d{4}-\d{2}-\d{2})", briefing_path.name)
    date_str = date_match.group(1) if date_match else briefing_path.stem

    mail_to = os.environ.get("MAIL_TO", "tiechengsun@126.com")
    smtp_host = os.environ.get("SMTP_HOST", "smtp.126.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "465"))
    smtp_user = os.environ.get("SMTP_USER", "tiechengsun@126.com")
    smtp_pass = os.environ.get("SMTP_PASS", "")
    feishu_webhook = os.environ.get("FEISHU_WEBHOOK", "")
    feishu_secret = os.environ.get("FEISHU_SECRET", "")

    subject = f"具身智能日报 {date_str}"
    html_body = markdown_to_html(content)

    retry_once(
        lambda: send_email(
            smtp_host, smtp_port, smtp_user, smtp_pass, mail_to, subject, html_body
        ),
        "Email",
    )

    if feishu_webhook:
        chunks = split_by_sections(content)
        total = len(chunks)

        def send_all():
            for i, chunk in enumerate(chunks, 1):
                title = (
                    f"具身智能简报日报 {date_str} {i}/{total}"
                    if total > 1
                    else f"具身智能简报日报 {date_str}"
                )
                send_feishu(feishu_webhook, feishu_secret, title, chunk)
                if i < total:
                    time.sleep(0.5)

        retry_once(send_all, "Feishu")
    else:
        print("Feishu: skipped (no webhook)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

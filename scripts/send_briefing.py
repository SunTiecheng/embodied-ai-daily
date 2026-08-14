#!/usr/bin/env python3
"""Send the full embodied AI daily briefing via email and Feishu.

Usage:
    python scripts/send_briefing.py briefings/YYYY-MM-DD.md

Environment variables required:
    MAIL_TO, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    FEISHU_WEBHOOK, FEISHU_KEYWORD
Optional:
    FEISHU_SECRET (for signature)
"""

import os
import sys
import re
import time
import hmac
import hashlib
import base64
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime, timezone, timedelta

import requests


def get_briefing_date(filepath):
    """Extract YYYY-MM-DD from filename or markdown heading."""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', os.path.basename(filepath))
    if m:
        return m.group(1)
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            m = re.search(r'(\d{4}-\d{2}-\d{2})', line)
            if m:
                return m.group(1)
    return datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')


def markdown_to_html(md):
    """Convert a subset of Markdown to HTML."""
    html = md
    # Escape HTML entities
    html = html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Headings
    html = re.sub(r'^###### (.*?)$', r'<h6>\1</h6>', html, flags=re.M)
    html = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', html, flags=re.M)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.M)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.M)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.M)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.M)
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    # Italic
    html = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'<em>\1</em>', html)
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    # Horizontal rule
    html = re.sub(r'^---+$', r'<hr>', html, flags=re.M)
    # Paragraphs / line breaks
    lines = html.split('\n')
    out = []
    in_list = False
    for line in lines:
        if line.startswith('- ') or re.match(r'^\d+\. ', line):
            if not in_list:
                out.append('<ul>' if line.startswith('- ') else '<ol>')
                in_list = True
            item = re.sub(r'^(- |\d+\. )', '', line)
            out.append(f'<li>{item}</li>')
        else:
            if in_list:
                out.append('</ul>' if out[-2] == '<ul>' else '</ol>')
                in_list = False
            if line.strip():
                out.append(f'<p>{line}</p>')
    if in_list:
        out.append('</ul>' if out[-2] == '<ul>' else '</ol>')
    return '\n'.join(out)


def send_email(subject, html_body, text_body):
    """Send email via SMTP with one retry."""
    mail_to = os.environ['MAIL_TO']
    smtp_host = os.environ['SMTP_HOST']
    smtp_port = int(os.environ['SMTP_PORT'])
    smtp_user = os.environ['SMTP_USER']
    smtp_pass = os.environ['SMTP_PASS']

    for attempt in range(2):
        try:
            msg = MIMEText(html_body, 'html', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = formataddr(('具身智能日报', smtp_user))
            msg['To'] = mail_to

            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [mail_to], msg.as_string())
            print(f"[OK] Email sent to {mail_to}")
            return True
        except Exception as e:
            print(f"[ERR] Email attempt {attempt + 1} failed: {e}")
            if attempt == 0:
                time.sleep(5)
    print("[FAIL] Email failed after retry.")
    return False


def feishu_sign(timestamp, secret):
    """Generate Feishu webhook signature."""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    return base64.b64encode(hmac_code).decode('utf-8')


def send_feishu_chunks(title_prefix, full_text):
    """Send full briefing to Feishu, splitting by ## if > 15000 chars."""
    keyword = os.environ.get('FEISHU_KEYWORD', '日报')
    webhook = os.environ['FEISHU_WEBHOOK']
    secret = os.environ.get('FEISHU_SECRET', '')

    # Split by level-2 headings
    sections = re.split(r'\n(?=## )', full_text)
    sections = [s.strip() for s in sections if s.strip()]

    chunks = []
    current = f"{keyword} {title_prefix}\n\n"
    for sec in sections:
        if len(current) + len(sec) + 2 > 15000:
            chunks.append(current.rstrip())
            current = f"{keyword} {title_prefix} (续)\n\n{sec}\n\n"
        else:
            current += sec + "\n\n"
    if current.strip():
        chunks.append(current.rstrip())

    # If still only one chunk and total length <= 15000, keep it
    if len(chunks) == 1 and len(chunks[0]) <= 15000:
        chunks = [chunks[0]]

    total = len(chunks)
    for idx, chunk in enumerate(chunks, 1):
        # Title must contain "日报" per user requirement; keyword must match Feishu bot security setting.
        header = f"{keyword} {title_prefix}"
        if total > 1:
            header = f"{keyword} {title_prefix} {idx}/{total}"
        # Ensure both keyword and "日报" appear in the body text.
        body = f"{header}\n\n{chunk.replace(title_prefix, '').strip()}\n\n{keyword} 日报"

        payload = {"msg_type": "text", "content": {"text": body}}
        headers = {}
        if secret:
            timestamp = str(int(datetime.now().timestamp()))
            payload['timestamp'] = timestamp
            payload['sign'] = feishu_sign(timestamp, secret)

        for attempt in range(2):
            try:
                resp = requests.post(webhook, json=payload, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                if data.get('code') != 0:
                    raise RuntimeError(f"Feishu API error: {data}")
                print(f"[OK] Feishu chunk {idx}/{total} sent")
                break
            except Exception as e:
                print(f"[ERR] Feishu chunk {idx}/{total} attempt {attempt + 1} failed: {e}")
                if attempt == 0:
                    time.sleep(5)
                else:
                    print(f"[FAIL] Feishu chunk {idx}/{total} failed after retry.")
                    return False
        else:
            continue
        time.sleep(1)  # avoid rate limit between chunks
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/send_briefing.py briefings/YYYY-MM-DD.md")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        md_text = f.read()

    date_str = get_briefing_date(filepath)
    subject = f"具身智能日报 {date_str}"

    html_body = markdown_to_html(md_text)
    text_body = md_text  # fallback plain text

    email_ok = send_email(subject, html_body, text_body)
    feishu_ok = send_feishu_chunks(subject, md_text)

    if not email_ok or not feishu_ok:
        sys.exit(1)


if __name__ == '__main__':
    main()

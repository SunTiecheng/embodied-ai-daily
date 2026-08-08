#!/usr/bin/env python3
"""Send embodied AI daily briefing via email and Feishu webhook."""
import os
import sys
import re
import time
import json
import smtplib
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib import request, error
from pathlib import Path

DATE = "2026-08-08"
MD_PATH = Path("/workspace/briefings/2026-08-08.md")
GITHUB_URL = "https://github.com/SunTiecheng/embodied-ai-daily/blob/cursor/bc-d4163e00-3dc2-43d6-b11c-2d6503031288-94a2/briefings/2026-08-08.md"

MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = os.environ.get("SMTP_PASS", "")

FEISHU_WEBHOOK = os.environ.get("FEISHU_WEBHOOK", "")
FEISHU_SECRET = os.environ.get("FEISHU_SECRET", "")


def md_to_html(md_text: str) -> str:
    html_body = markdown.markdown(md_text, extensions=["tables"])
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333;">
{html_body}
<hr>
<p><a href="{GITHUB_URL}">在 GitHub 查看完整简报</a></p>
</body>
</html>"""


def send_email(html_body: str) -> dict:
    if not SMTP_PASS:
        return {"ok": False, "error": "SMTP_PASS not set"}
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"具身智能日报 {DATE}"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    last_err = None
    for attempt in range(2):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            return {"ok": True, "attempts": attempt + 1}
        except Exception as e:
            last_err = str(e)
            if attempt == 0:
                time.sleep(4)
    return {"ok": False, "error": last_err}


def feishu_sign(timestamp: int) -> str:
    """Not used when secret is empty; kept for completeness."""
    if not FEISHU_SECRET:
        return ""
    import hmac
    import hashlib
    import base64
    string = f"{timestamp}\n{FEISHU_SECRET}"
    hmac_code = hmac.new(
        string.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_feishu_parts(md_text: str) -> dict:
    if not FEISHU_WEBHOOK:
        return {"ok": False, "error": "FEISHU_WEBHOOK not set"}
    # Strip the leading h1 title from body, use it as header for each message
    title_match = re.search(r"^#\s+(.+)$", md_text, re.M)
    title = title_match.group(1) if title_match else f"具身智能日报 {DATE}"
    # Remove leading title line from the body used for splitting
    body = re.sub(r"^#\s+.+\n", "", md_text).strip()
    # Split by top-level ## sections
    sections = re.split(r"\n(?=##\s)", body)
    parts = [s for s in sections if s.strip()]
    if len(parts) <= 1 or len(md_text) <= 15000:
        parts = [body]
    total = len(parts)
    results = []
    for idx, part in enumerate(parts, 1):
        header = f"{title}（简报 {idx}/{total}）\n" if total > 1 else f"{title}（简报）\n"
        text = header + part
        if FEISHU_SECRET:
            timestamp = int(time.time())
            sign = feishu_sign(timestamp)
            payload = {
                "msg_type": "text",
                "content": {"text": text},
                "timestamp": timestamp,
                "sign": sign,
            }
        else:
            payload = {"msg_type": "text", "content": {"text": text}}
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json; charset=utf-8"}
        last_err = None
        ok = False
        for attempt in range(2):
            try:
                req = request.Request(FEISHU_WEBHOOK, data=data, headers=headers, method="POST")
                with request.urlopen(req, timeout=30) as resp:
                    result = resp.read().decode("utf-8")
                results.append({"part": idx, "ok": True, "response": result})
                ok = True
                break
            except Exception as e:
                last_err = str(e)
                if attempt == 0:
                    time.sleep(4)
        if not ok:
            results.append({"part": idx, "ok": False, "error": last_err})
    return {"ok": all(r.get("ok") for r in results), "results": results}


def main():
    if not MD_PATH.exists():
        print(f"Markdown file not found: {MD_PATH}", file=sys.stderr)
        sys.exit(1)
    md_text = MD_PATH.read_text(encoding="utf-8")
    html_body = md_to_html(md_text)

    if not os.environ.get("SKIP_EMAIL"):
        email_res = send_email(html_body)
        print("Email:", email_res)
    else:
        email_res = {"ok": True, "skipped": True}

    feishu_res = send_feishu_parts(md_text)
    print("Feishu:", feishu_res)

    if not email_res["ok"] or not feishu_res["ok"]:
        sys.exit(1)


if __name__ == "__main__":
    main()

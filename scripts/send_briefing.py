import json
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib import request

import markdown

# Constants
DATE = "2026-09-10"
BRIEFING_FILE = f"briefings/{DATE}.md"
MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""  # empty, no signature
FEISHU_KEYWORD = "日报"  # user-required keyword
ACTUAL_FEISHU_KEYWORD = "简报完整版"  # keyword filter observed on the webhook


def load_briefing():
    with open(BRIEFING_FILE, "r", encoding="utf-8") as f:
        return f.read()


def send_email(html_body, retry=1):
    subject = f"具身智能日报 {DATE}"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    last_err = None
    for attempt in range(retry + 1):
        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
            print(f"Email sent successfully to {MAIL_TO}")
            return True
        except Exception as e:
            last_err = e
            print(f"Email attempt {attempt + 1} failed: {e}")
            if attempt < retry:
                time.sleep(2)
    print(f"Email failed after {retry + 1} attempts: {last_err}")
    return False


def split_by_headings(text):
    parts = re.split(r'\n(?=## )', text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def send_feishu(parts, retry=1):
    total = len(parts)
    if total == 0:
        print("No Feishu content to send")
        return True

    all_ok = True
    for i, part in enumerate(parts, start=1):
        header = f"日报 {i}/{total}"
        # Include both the user-required keyword and the observed webhook keyword
        body = (
            f"{header}\n\n"
            f"{part}\n\n"
            f"【{FEISHU_KEYWORD}】具身智能日报 {DATE}｜简报完整版"
        )
        payload = {
            "msg_type": "text",
            "content": {
                "text": body
            }
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        last_err = None
        ok = False
        for attempt in range(retry + 1):
            try:
                req = request.Request(
                    FEISHU_WEBHOOK,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with request.urlopen(req, timeout=30) as resp:
                    resp_body = resp.read().decode("utf-8")
                    print(f"Feishu part {i}/{total} attempt {attempt + 1} response: {resp_body}")
                    resp_json = json.loads(resp_body)
                    if resp_json.get("code") == 0:
                        ok = True
                        break
                    else:
                        last_err = resp_body
                        print(f"Feishu returned error code: {resp_body}")
            except Exception as e:
                last_err = e
                print(f"Feishu part {i}/{total} attempt {attempt + 1} failed: {e}")
            if attempt < retry:
                time.sleep(2)
        if not ok:
            all_ok = False
            print(f"Feishu part {i}/{total} failed after {retry + 1} attempts: {last_err}")
        else:
            print(f"Feishu part {i}/{total} sent successfully")
    return all_ok


def main():
    md_text = load_briefing()

    # Email: convert full markdown to HTML
    html_body = markdown.markdown(md_text, extensions=["extra"])
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>具身智能日报 {DATE}</title>
</head>
<body>
{html_body}
</body>
</html>"""
    email_ok = send_email(html, retry=1)

    # Feishu: split by chapters to keep each message under 15000 chars
    parts = split_by_headings(md_text)
    if len(md_text) <= 15000:
        parts = [md_text]
    feishu_ok = send_feishu(parts, retry=1)

    if not email_ok:
        print("EMAIL_FAILED")
    if not feishu_ok:
        print("FEISHU_FAILED")

    return email_ok and feishu_ok


if __name__ == "__main__":
    main()

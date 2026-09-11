import json
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib import request

import markdown

# Constants
DATE = "2026-09-11"
BRIEFING_FILE = f"briefings/{DATE}.md"
MAIL_TO = "tiechengsun@126.com"
SMTP_HOST = "smtp.126.com"
SMTP_PORT = 465
SMTP_USER = "tiechengsun@126.com"
SMTP_PASS = "AXwS4p3Avd2C2KFy"
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268"
FEISHU_SECRET = ""  # empty, no signature
FEISHU_KEYWORD = "日报"
FEISHU_EXTRA_KEYWORD = "简报"  # webhook keyword filter
FEISHU_MAX_CHARS = 2000


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
    parts = re.split(r"\n(?=## )", text)
    return [p.strip() for p in parts if p.strip()]


def _strip_md_links(line: str) -> str:
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)


def build_feishu_condensed(md_text: str) -> str:
    """Compress briefing to <= FEISHU_MAX_CHARS for Feishu; email stays full."""
    lines = md_text.splitlines()
    out = [f"【{FEISHU_EXTRA_KEYWORD}】具身智能日报 {DATE}（飞书精编，完整版见邮件）\n"]

    def add_block(text: str):
        nonlocal out
        if not text.strip():
            return
        candidate = "\n".join(out) + "\n" + text.strip() + "\n"
        if len(candidate) <= FEISHU_MAX_CHARS - 80:
            out.append(text.strip())

    # Title line + meta
    for line in lines[:3]:
        if line.startswith("#") or line.startswith(">"):
            add_block(_strip_md_links(line))

    sections = split_by_headings(md_text)
    priority_headers = (
        "今日必看",
        "行业要闻",
        "专题：行业公司",
        "专题：具身世界",
        "论文速递",
        "开源",
        "今日关键词",
    )

    for sec in sections:
        header = sec.split("\n", 1)[0]
        if not any(p in header for p in priority_headers):
            continue
        body = sec
        if "今日必看" in header:
            # Top 5: keep ### headings + first paragraph each
            chunks = re.split(r"\n(?=### )", sec)
            condensed = [chunks[0].strip()]
            for c in chunks[1:6]:
                sub = c.strip().split("\n\n", 1)
                title = _strip_md_links(sub[0].replace("### ", "").strip())
                para = ""
                if len(sub) > 1:
                    para = sub[1].split("\n\n")[0].strip()
                    para = _strip_md_links(para)
                    if len(para) > 220:
                        para = para[:217] + "..."
                condensed.append(f"### {title}\n{para}")
            body = "\n\n".join(condensed)
        elif "论文速递" in header:
            bullets = [
                _strip_md_links(ln)
                for ln in sec.splitlines()
                if ln.strip().startswith("- **")
            ]
            body = header + "\n" + "\n".join(bullets[:10])
        elif "行业要闻" in header:
            items = [
                _strip_md_links(ln)
                for ln in sec.splitlines()
                if re.match(r"^\d+\.\s", ln.strip())
            ]
            body = header + "\n" + "\n".join(items[:8])
        else:
            # Other sections: first ~600 chars of prose
            prose = "\n".join(
                _strip_md_links(ln)
                for ln in sec.splitlines()[1:]
                if ln.strip() and not ln.strip().startswith("---")
            )
            if len(prose) > 650:
                prose = prose[:647] + "..."
            body = header + "\n" + prose

        add_block(body)

    footer = f"\n> 完整 Markdown 已邮件推送｜关键词：{FEISHU_KEYWORD}、{FEISHU_EXTRA_KEYWORD}"
    text = "\n\n".join(out) + footer
    if len(text) > FEISHU_MAX_CHARS:
        text = text[: FEISHU_MAX_CHARS - 3] + "..."
    return text


def send_feishu_text(body: str, retry=1):
    payload = {
        "msg_type": "text",
        "content": {"text": body},
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_err = None
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
                print(f"Feishu attempt {attempt + 1} response: {resp_body}")
                resp_json = json.loads(resp_body)
                if resp_json.get("code") == 0:
                    print("Feishu sent successfully")
                    return True
                last_err = resp_body
        except Exception as e:
            last_err = e
            print(f"Feishu attempt {attempt + 1} failed: {e}")
        if attempt < retry:
            time.sleep(2)
    print(f"Feishu failed after {retry + 1} attempts: {last_err}")
    return False


def main():
    md_text = load_briefing()

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

    feishu_body = build_feishu_condensed(md_text)
    print(f"Feishu body length: {len(feishu_body)} chars")
    feishu_ok = send_feishu_text(feishu_body, retry=1)

    if not email_ok:
        print("EMAIL_FAILED")
    if not feishu_ok:
        print("FEISHU_FAILED")

    return email_ok and feishu_ok


if __name__ == "__main__":
    main()

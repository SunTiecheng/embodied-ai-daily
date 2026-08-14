# 具身智能每日简报运行手册

本仓库为 Cursor Automation 自动运行，每日抓取、整理、提交并推送具身智能日报。

## 环境常量（请在 Cursor Dashboard > Secrets 中配置）

| 变量 | 说明 |
|------|------|
| `MAIL_TO` | 邮件收件人，默认 `tiechengsun@126.com` |
| `SMTP_HOST` | SMTP 服务器，默认 `smtp.126.com` |
| `SMTP_PORT` | SMTP 端口，默认 `465` |
| `SMTP_USER` | SMTP 用户名，默认 `tiechengsun@126.com` |
| `SMTP_PASS` | SMTP 密码/授权码 |
| `FEISHU_WEBHOOK` | 飞书机器人 Webhook URL |
| `FEISHU_SECRET` | 飞书签名密钥（可选） |
| `FEISHU_KEYWORD` | 飞书关键词，默认 `日报` |

**注意：** 以上凭据仅通过环境变量读取，禁止写入仓库任何文件。

## 运行流程

1. **读取模板**：打开 `docs/BRIEFING_TEMPLATE.md` 确认当日简报结构。
2. **抓取信息**：搜索近 24–48 小时（以北京时间当天为准）的具身智能新闻、论文、开源/产品动态、公司发布会与 demo 视频。
3. **生成简报**：写入 `briefings/YYYY-MM-DD.md`（YYYY-MM-DD 为北京时间当天）。
4. **提交推送**：
   ```bash
   git config user.email SunTiecheng@users.noreply.github.com
   git config user.name SunTiecheng
   git add briefings/YYYY-MM-DD.md
   git commit -m "briefing: YYYY-MM-DD embodied AI daily"
   git push -u origin cursor/bc-f163a0c6-728c-420a-a8b0-29d72d20db93-c2ae
   ```
5. **推送简报**：运行 `scripts/send_briefing.py briefings/YYYY-MM-DD.md`，发送完整简报到邮件和飞书。
   - 邮件主题：`具身智能日报 YYYY-MM-DD`，正文为 Markdown 转 HTML 的完整简报。
   - 飞书：发送完整简报原文；单条超过 15000 字按 `##` 章节拆分为多条，标题含 `日报` 与 `1/N`、`2/N` 等序号。
6. **失败重试**：邮件或飞书失败时重试一次。

## 简报内容要求

- 论文控制在 **20 篇以内**，每篇仅需「标题 + 一句话摘要 + 链接」。
- 必须包含：
  - 今日必看 Top 5
  - 行业要闻 8–12 条
  - 行业公司发布会 / demo 视频专题
  - 具身世界模型 / 仿真专题
  - 论文速递（按主题分类）
  - 开源 & 产品动态
  - 今日关键词
- 使用中文，论文标题保留英文原名。
- 禁止虚构，禁止只发摘要。

## 质量检查

- [ ] 简报文件已写入并推送成功。
- [ ] 邮件已发送且未报错。
- [ ] 飞书已发送且未报错。
- [ ] 日期为北京时间当天。
- [ ] 论文数量 ≤ 20 篇。

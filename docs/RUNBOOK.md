# 具身智能每日简报运行手册

## 运行目标

每次运行需完成：**信息抓取 → 生成完整简报 → 提交 GitHub → 邮件与飞书推送完整简报**。

## 环境常量

- 仓库：`SunTiecheng/embodied-ai-daily`，分支 `main`
- 简报文件：`briefings/YYYY-MM-DD.md`（日期为北京时间当天）
- 邮件收件人：`MAIL_TO=tiechengsun@126.com`
- SMTP 服务器：`SMTP_HOST=smtp.126.com`，端口 `SMTP_PORT=465`，用户 `SMTP_USER=tiechengsun@126.com`
- 飞书 Webhook：`FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- 飞书关键词：`FEISHU_KEYWORD=日报`
- 提交前配置：
  - `git config user.email SunTiecheng@users.noreply.github.com`
  - `git config user.name SunTiecheng`

## 运行顺序

1. **读取模板**：`docs/RUNBOOK.md` 和 `docs/BRIEFING_TEMPLATE.md`。
2. **信息抓取**：近 24-48 小时具身智能新闻、论文、开源动态、专题事件（发布会 / demo / 世界模型 / 仿真）。
3. **生成简报**：写入 `briefings/YYYY-MM-DD.md`，按模板结构展开，论文控制在 20 篇以内，简短摘要。
4. **提交推送**：
   - `git add briefings/YYYY-MM-DD.md`
   - `git commit -m "briefing: YYYY-MM-DD embodied AI daily"`
   - `git push -u origin <branch>`
5. **邮件推送**：主题「具身智能日报 YYYY-MM-DD」，正文为完整简报（Markdown 转 HTML）。
6. **飞书推送**：将完整简报原文推送至 `FEISHU_WEBHOOK`。
   - 每条消息标题须含「日报」。
   - 单条超过 15000 字按 `##` 章节拆分（如 日报 1/3、2/3…）。
   - 每条正文均含「日报」。
   - `msg_type` 可用 `text`。
   - 若 `FEISHU_SECRET` 非空则加签名。

## 重试规则

- 飞书或邮件失败时重试一次。
- git push 若因网络失败，按 4s / 8s / 16s / 32s 指数退避重试最多 4 次。

## 质量与合规要求

- 禁止虚构内容。
- 禁止只发送摘要，必须推送完整简报。
- 论文篇数控制在 20 篇以内，每篇一句话摘要。
- 补充行业公司发布会、demo 视频、具身世界模型、仿真等专题。
- 日期为北京时间当天。

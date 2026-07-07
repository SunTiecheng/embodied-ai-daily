# 具身智能每日简报运行手册

## 1. 触发条件

- 自动化 Cron 触发（UTC 00:00，对应北京时间 08:00）。
- 手动运行：以当前工作区为基准，按本手册执行。

## 2. 运行顺序

1. 读取 `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时（优先当日）具身智能新闻、论文、开源、产品、发布会、demo 视频。
3. 写入 `briefings/YYYY-MM-DD.md`，日期使用**北京时间当天**。
4. `git add` / `git commit` / `git push` 到当前分支。
5. 推送完整简报：邮件（HTML）+ 飞书（Markdown 原文）。

## 3. 环境常量

| 变量 | 值 |
|------|-----|
| `MAIL_TO` | `tiechengsun@126.com` |
| `SMTP_HOST` | `smtp.126.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `tiechengsun@126.com` |
| `SMTP_PASS` | `AXwS4p3Avd2C2KFy` |
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268` |
| `FEISHU_SECRET` | （空） |
| `FEISHU_KEYWORD` | `日报` |
| 简报文件 | `briefings/YYYY-MM-DD.md` |

## 4. Git 提交规范

提交前必须执行：

```bash
git config user.email "SunTiecheng@users.noreply.github.com"
git config user.name "SunTiecheng"
```

提交消息格式：

```
briefing: YYYY-MM-DD embodied AI daily
```

## 5. 邮件推送

- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：完整简报 Markdown 转 HTML，含全部章节与链接，**不设字数上限**。
- 使用 `SMTP_HOST:smtp.126.com:465` SSL 发送。

## 6. 飞书推送

- 将完整简报原文推送至 `FEISHU_WEBHOOK`。
- 每条消息标题必须包含 `日报`（关键词过滤）。
- 单条超过 15,000 字时按 `##` 章节拆分为多条顺序发送（如 `日报 1/3`、`2/3`…）。
- 每条正文均需包含 `日报`。
- `msg_type` 可用 `text`。
- `FEISHU_SECRET` 非空时加签名；当前为空，无需签名。

## 7. 内容要求

- 论文控制在 **20 篇**左右，每篇简短摘要（一句话即可）。
- 补充行业公司发布会、demo 视频等专题。
- 补充具身世界模型、仿真专题。
- 禁止虚构内容；禁止只发送摘要；禁止过度夸张的标题党。
- 所有外部链接必须可追溯到来源。

## 8. 重试策略

- 邮件或飞书失败时重试一次。
- 若仍失败，在运行日志或 commit message 中注明错误。

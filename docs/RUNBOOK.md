# 具身智能每日简报运行手册

## 触发

本仓库由 Cursor Cloud Agent 每日自动运行（北京时间 cron 0 0 * * *）。

## 运行顺序

1. 读取 `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时具身智能新闻、论文、产品/发布会/demo 视频，并补充：
   - 行业公司发布会、demo 视频等专题；
   - 具身世界模型、仿真专题。
3. 写入 `briefings/YYYY-MM-DD.md`（北京日期当天）。
4. 提交并推送至当前开发分支。
5. 读取简报全文，推送完整简报（非摘要）至飞书 + 邮件。

## 常量

| 常量 | 值 |
|------|-----|
| `MAIL_TO` | `tiechengsun@126.com` |
| `SMTP_HOST` | `smtp.126.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `tiechengsun@126.com` |
| `SMTP_PASS` | `AXwS4p3Avd2C2KFy` |
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268` |
| `FEISHU_SECRET` | ``（空） |
| `FEISHU_KEYWORD` | `日报` |
| 简报文件 | `briefings/YYYY-MM-DD.md` |

## 提交配置

提交前执行：

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 推送规则

- 使用 `git push -u origin <当前开发分支>`。
- 仅当失败原因为网络错误时重试，最多 4 次，退避 4s/8s/16s/32s。
- 飞书或邮件推送失败时重试一次。

## 质量约束

- 禁止虚构内容；每条新闻/论文必须附带真实来源链接。
- 飞书/邮件必须推送完整简报，**禁止只发摘要**。
- 论文控制在 20 篇左右，每篇简短摘要。
- 每条飞书消息标题必须包含关键词 `日报`；超过 15000 字按 `##` 章节拆分，标题形如 `日报 1/3`、`日报 2/3` 等。

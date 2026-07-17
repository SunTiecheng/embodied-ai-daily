# 具身智能每日简报运行手册

本仓库为 `SunTiecheng/embodied-ai-daily`，分支 `main`（实际提交请使用 Cursor 分配的开发分支）。

## 每次运行顺序

1. 读取 `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时具身智能新闻、论文、发布会/Demo 视频、世界模型与仿真专题。
3. 写入 `briefings/YYYY-MM-DD.md`（日期为北京时间当天）。
4. 提交并推送分支。
5. 推送完整简报（非摘要）：
   - 邮件：主题「具身智能日报 YYYY-MM-DD」，正文为 Markdown 转 HTML 的完整简报。
   - 飞书：将完整简报原文推送至 `FEISHU_WEBHOOK`；每条消息标题含「日报」；单条超 15,000 字按 `##` 章节拆分；`msg_type` 用 `text`；`FEISHU_SECRET` 非空时加签名。
6. 失败重试一次。

## 环境常量

- `MAIL_TO=tiechengsun@126.com`
- `SMTP_HOST=smtp.126.com`
- `SMTP_PORT=465`
- `SMTP_USER=tiechengsun@126.com`
- `SMTP_PASS=AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET=`（空，不加签名）
- `FEISHU_KEYWORD=日报`
- 简报文件：`briefings/YYYY-MM-DD.md`

## 提交前必须执行

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 质量约束

- 禁止虚构。
- 禁止只发摘要。
- 论文篇数控制在 20 篇左右，简短摘要即可。
- 所有外部信息必须标注来源链接。

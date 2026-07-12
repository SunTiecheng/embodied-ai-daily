# 具身智能每日简报运行手册

## 每次运行顺序

1. 读取本文件 `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`
2. 抓取近 24–48 小时具身智能新闻与论文
3. 写入 `briefings/YYYY-MM-DD.md`（北京时间当天）
4. git 提交并推送
5. 飞书 + 邮件推送完整简报（非摘要）

## 常量

- `MAIL_TO`: `tiechengsun@126.com`
- `SMTP_HOST`: `smtp.126.com`
- `SMTP_PORT`: `465`
- `SMTP_USER`: `tiechengsun@126.com`
- `SMTP_PASS`: `AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK`: `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET`: 空（为空时不加签名）
- `FEISHU_KEYWORD`: `日报`
- 简报文件: `briefings/YYYY-MM-DD.md`

## 提交前执行

```bash
git config user.email "SunTiecheng@users.noreply.github.com"
git config user.name "SunTiecheng"
```

## 简报内容要求

- 补充行业公司发布会、demo 视频等专题
- 补充具身世界模型、仿真专题
- 论文控制在 20 篇以内，每篇简短摘要即可
- 禁止虚构
- 禁止只发摘要

## 推送要求

push 成功后，读取 `briefings/YYYY-MM-DD.md` 全文推送：

1. **邮件**：主题「具身智能日报 YYYY-MM-DD」，正文为完整简报（Markdown 转 HTML，含全部章节与链接），不设字数上限。
2. **飞书**：将完整简报原文推送至 `FEISHU_WEBHOOK`。每条消息标题须含「日报」（关键词过滤）。单条超 15000 字则按 `##` 章节拆成多条顺序发送（如 日报 1/3、2/3…），每条正文均含「日报」。`msg_type` 可用 `text`。
   - 若 `FEISHU_SECRET` 非空则加签名。

## 重试

飞书或邮件失败重试一次。

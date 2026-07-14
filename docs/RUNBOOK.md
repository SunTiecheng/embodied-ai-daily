# 具身智能每日简报运行手册

## 运行顺序

每次运行顺序：读取 `docs/RUNBOOK.md` 和 `docs/BRIEFING_TEMPLATE.md` → 抓取近 24-48 小时具身智能新闻与论文 → 写入 `briefings/YYYY-MM-DD.md`（北京时间当天） → git 提交推送 → 飞书 + 邮件推送完整简报（非摘要）。

## 环境常量

- `MAIL_TO`: `tiechengsun@126.com`
- `SMTP_HOST`: `smtp.126.com`
- `SMTP_PORT`: `465`
- `SMTP_USER`: `tiechengsun@126.com`
- `SMTP_PASS`: `AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK`: `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET`: ``（空）
- `FEISHU_KEYWORD`: `日报`
- 简报文件: `briefings/YYYY-MM-DD.md`（北京日期）
- GitHub 仓库: `SunTiecheng/embodied-ai-daily`
- 开发分支: `cursor/bc-9ef28120-7810-428a-88c1-bb69c8ec1719-65bc`（base `main`）

## 提交前配置

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 提交与推送

```bash
git add briefings/YYYY-MM-DD.md
git commit -m "briefing: YYYY-MM-DD embodied AI daily"
git push -u origin cursor/bc-9ef28120-7810-428a-88c1-bb69c8ec1719-65bc
```

## 推送内容

push 成功后，读取 `briefings/YYYY-MM-DD.md` 全文推送：

1. **邮件**：主题「具身智能日报 YYYY-MM-DD」，正文为完整简报（Markdown 转 HTML，含全部章节与链接），不设字数上限。
2. **飞书**：将完整简报原文推送至 `FEISHU_WEBHOOK`。每条消息标题须含「日报」（关键词过滤）。单条超 15000 字则按 `##` 章节拆成多条顺序发送（如 日报 1/3、2/3…），每条正文均含「日报」。`msg_type` 可用 `text`。`FEISHU_SECRET` 非空时加签名。控制论文篇数约 20 篇，论文简短摘要即可。

## 质量规则

- 禁止虚构。
- 禁止只发摘要。
- 飞书或邮件失败重试一次。
- 优先抓取 24-48 小时内内容。
- 论文标题保留英文，其余内容全中文。
- 补充行业公司发布会、demo 视频等专题。
- 补充具身世界模型、仿真专题。

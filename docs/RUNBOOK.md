# 具身智能每日简报运行手册

## 运行顺序

每次 Agent 触发后严格按以下顺序执行：

1. **读取本文档** `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`。
2. **抓取**：采集近 24–48 小时具身智能新闻、论文、开源/产品动态，补充：
   - 行业公司发布会、Demo 视频等专题；
   - 具身世界模型、仿真专题。
3. **撰写**：按模板写入 `briefings/YYYY-MM-DD.md`（日期为**北京时间当天**）。
4. **提交**：`git add` → `git commit` → `git push` 到指定分支。
5. **推送**：push 成功后，读取完整简报全文，依次发送邮件与飞书。

## 常量

| 常量 | 值 |
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

## 提交前配置

提交前必须执行：

```bash
git config user.email "SunTiecheng@users.noreply.github.com"
git config user.name "SunTiecheng"
```

## 推送规则

- `git push -u origin <branch-name>`。
- push 失败若因网络错误，按 4s / 8s / 16s / 32s 指数退避重试，最多 4 次。

## 简报内容规范

- 论文总量控制在 **20 篇以内**，每篇仅一句话简短摘要。
- 全文推送邮件与飞书，**禁止只发摘要**。
- 飞书每条消息标题必须含「日报」；单条超过 15000 字按 `##` 章节拆分多条顺序发送（如「日报 1/3」、「日报 2/3」）。
- `msg_type` 可用 `text`；`FEISHU_SECRET` 非空时加签名。
- 邮件主题「具身智能日报 YYYY-MM-DD」，正文 Markdown 转 HTML，无字数上限。
- 飞书或邮件失败时重试一次。
- **禁止虚构**：所有新闻、论文、链接必须真实可验证。

# 具身智能每日简报运行手册

> 本文件由 Cursor Automation 每次运行时首先读取，用于规范工作流与质量检查。

## 运行环境常量

| 常量 | 值 |
|------|-----|
| `MAIL_TO` | `tiechengsun@126.com` |
| `SMTP_HOST` | `smtp.126.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | `tiechengsun@126.com` |
| `SMTP_PASS` | `<在 Cursor Automation Secrets 中配置，勿提交到 GitHub>` |
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268` |
| `FEISHU_SECRET` | `<空则不签名>` |
| `FEISHU_KEYWORD` | `日报` |
| 简报存档 | `briefings/YYYY-MM-DD.md`（日期为北京时间当天） |
| 目标分支 | `main` |

## 每次运行顺序

1. 读取本文件与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时具身智能新闻、论文、发布会/demo、世界模型/仿真动态。
3. 按模板生成 `briefings/YYYY-MM-DD.md`（北京时间当天）。
4. 执行 `git config user.email SunTiecheng@users.noreply.github.com` 与 `git config user.name SunTiecheng`。
5. `git add` → `git commit` → `git push -u origin <当前分支>`。
6. 读取生成的完整简报，分别推送：
   - **邮件**：主题「具身智能日报 YYYY-MM-DD」，正文 Markdown 转 HTML（完整版，无字数上限）。
   - **飞书**：完整简报原文推送至 `FEISHU_WEBHOOK`，每条标题含「日报」；单条超过 15000 字则按 `##` 章节拆成多条顺序发送（如 日报 1/3、2/3…）。`FEISHU_SECRET` 非空时加签名。`msg_type` 可用 `text`。
7. 推送失败时各自重试一次。

## 内容规范

- 全中文，论文标题保留英文原名。
- **禁止虚构**；所有条目必须附来源链接。
- **禁止只发摘要**；邮件和飞书必须发送完整简报。
- 论文数量控制在 **20 篇以内**，每篇简短摘要（标题 + 一句话 + 链接）。
- 必须包含：
  - 今日必看 Top 5
  - 行业要闻 8–12 条
  - 专题：行业公司发布会 / demo 视频等
  - 专题：具身世界模型 / 仿真
  - 论文速递（分类）
  - 开源 & 产品动态
  - 今日关键词

## 质量检查（完成前自检）

- [ ] 简报文件已写入 `briefings/YYYY-MM-DD.md` 且 push 成功。
- [ ] 邮件已发送完整简报，主题为「具身日报 YYYY-MM-DD」。
- [ ] 飞书已发送完整简报，每条含关键词「日报」。
- [ ] 日期为北京时间当天。
- [ ] 无虚构条目，所有链接真实可访问。

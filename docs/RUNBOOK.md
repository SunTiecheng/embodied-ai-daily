# 具身智能每日简报运行手册

## 目标
作为「具身智能每日简报」编辑，每次运行完成：信息抓取 → 生成 Markdown 简报 → 提交 GitHub → 推送完整简报（邮件 + 飞书）。

## 常量

- `MAIL_TO=tiechengsun@126.com`
- `SMTP_HOST=smtp.126.com`
- `SMTP_PORT=465`
- `SMTP_USER=tiechengsun@126.com`
- `SMTP_PASS=AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET=`（空）
- `FEISHU_KEYWORD=日报`
- 简报文件：`briefings/YYYY-MM-DD.md`（日期为北京时间当天）
- 仓库：`SunTiecheng/embodied-ai-daily`，分支：`main`
- 提交身份：`git config user.email SunTiecheng@users.noreply.github.com`、`git config user.name SunTiecheng`

## 运行顺序

1. 读取本文件 `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时具身智能新闻、论文、开源与产品动态（优先 24 小时内）。
3. 按模板写入 `briefings/YYYY-MM-DD.md`（北京当天）。
4. 执行 `git add` / `git commit` / `git push -u origin main`（按分支要求实际也可使用 `cursor/bc-86d88d92-3b39-4a22-93a6-34d7e137b041-0afa` 分支，但自动化上下文默认 `main`）。
5. 简报推送成功且文件生成后，读取完整简报并推送：
   - 邮件：主题「具身智能日报 YYYY-MM-DD」，正文为完整简报（Markdown 转 HTML）。
   - 飞书：将完整简报原文推送至 `FEISHU_WEBHOOK`，标题含「日报」；若单条超 15000 字则按 `##` 章节拆分多条顺序发送（如「日报 1/3」）。
6. 邮件或飞书失败时，整体重试一次。

## 信息源

### 论文
- arXiv: cs.RO, cs.AI, cs.LG, cs.CV
- Papers with Code、Semantic Scholar
- 关键词：embodied AI, VLA, vision-language-action, robot manipulation, humanoid, sim2real, world model, dexterous, teleoperation, mobile manipulation, loco-manipulation, 具身世界模型, 仿真

### 新闻
- 英文：The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics
- 中文：机器之心、量子位、36氪、极客公园（机器人/AI 相关）

### 开源 / 产品
- GitHub Trending（robotics / embodied / VLA）
- 头部公司：Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, Physical Intelligence 等
- 补充：行业公司发布会、demo 视频、世界模型、仿真专题

## 质量要求

- 禁止虚构，必须基于真实抓取结果。
- 简报推送完整内容，禁止只发摘要。
- 论文总数控制在 20 篇左右，每篇简短摘要即可。
- 去重：同一论文/新闻不重复。
- 全中文，论文标题保留英文原名。

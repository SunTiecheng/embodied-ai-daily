# 具身智能每日简报运行手册

## 每次运行顺序

1. 读取本文件 `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时具身智能新闻、论文、开源与产品动态。
3. 按模板写入 `briefings/YYYY-MM-DD.md`（北京日期）。
4. 执行 `git add / commit / push` 到本仓库指定分支。
5. 从 GitHub 读取已 push 的简报文件，邮件 + 飞书推送**完整简报**（非摘要）。
6. 邮件或飞书失败时重试一次。

## 环境常量（运行时从环境变量读取，禁止提交到仓库）

- `MAIL_TO`: `tiechengsun@126.com`
- `SMTP_HOST`: `smtp.126.com`
- `SMTP_PORT`: `465`
- `SMTP_USER`: `tiechengsun@126.com`
- `SMTP_PASS`: 从环境变量读取
- `FEISHU_WEBHOOK`: `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET`: 从环境变量读取（可为空）
- `FEISHU_KEYWORD`: `日报`
- 简报文件: `briefings/YYYY-MM-DD.md`
- 仓库分支: `cursor/bc-ce0d0afc-d2d9-4e28-ba6f-f28b474474b0-7746`（base: `main`）

## 信息抓取范围

### 论文源
- arXiv: cs.RO, cs.AI, cs.LG, cs.CV
- Papers with Code、Semantic Scholar
- 关键词：embodied AI, VLA, vision-language-action, robot manipulation, humanoid, sim2real, world model, dexterous, teleoperation, mobile manipulation, loco-manipulation, 具身世界模型, 仿真

### 新闻源
- 英文：The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics, Wired Robotics
- 中文：机器之心、量子位、36 氪、极客公园（机器人/AI 相关）

### 开源 / 产品 / 专题
- GitHub Trending（robotics / embodied / VLA）
- 头部公司动态：Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, Physical Intelligence, Boston Dynamics, Agility, NVIDIA, Google DeepMind 等
- 补充行业公司发布会、demo 视频等专题
- 补充具身世界模型、仿真专题

## 简报内容要求

- 论文篇数控制在 **20 篇**，每条「标题 + 一句简短摘要 + 链接」。
- 行业要闻 8–12 条，每条 50–80 字 + 来源链接。
- 今日必看 Top 5，每篇 150–200 字：核心贡献 + 为何重要 + 链接。
- 开源 & 产品 5–8 条。
- 今日关键词 5–10 个 + 一句趋势概括。
- 补充世界模型、仿真专题小节。
- 全中文，论文标题保留英文原名。
- 禁止虚构；禁止只发摘要。

## 提交前检查

- 日期为北京日期当天。
- 文件已写入 `briefings/YYYY-MM-DD.md`。
- 提交前执行：
  ```bash
  git config user.email SunTiecheng@users.noreply.github.com
  git config user.name SunTiecheng
  ```
- 提交信息：`briefing: YYYY-MM-DD embodied AI daily`
- Push 命令：`git push -u origin <branch-name>`
- Push 失败（网络原因）时最多重试 4 次，间隔 4s / 8s / 16s / 32s。

## 推送检查

- 邮件主题：`具身智能日报 YYYY-MM-DD`，正文为完整简报（Markdown 转 HTML，含全部章节与链接），不设字数上限。
- 飞书：将完整简报原文推送至 `FEISHU_WEBHOOK`。每条消息标题须含「日报」（关键词过滤）。单条超 15000 字则按 `##` 章节拆成多条顺序发送（如 `日报 1/3`、`2/3`…），每条正文均含「日报」。`msg_type` 可用 `text`。`FEISHU_SECRET` 非空时加签名。
- 邮件或飞书失败时重试一次。

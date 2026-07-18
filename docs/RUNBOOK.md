# 具身智能每日简报运行手册

## 运行时机

Cron：每日 UTC 00:00（对应北京时间 08:00）。

## 每次运行顺序

1. 读取本运行手册（`docs/RUNBOOK.md`）和简报模板（`docs/BRIEFING_TEMPLATE.md`）。
2. 抓取近 24–48 小时具身智能新闻、论文、产品发布、Demo 视频、世界模型与仿真进展。
3. 按模板写入 `briefings/YYYY-MM-DD.md`（日期为北京时间当天）。
4. 执行 `git add` / `git commit` / `git push`。
5. 读取简报全文，邮件 + 飞书推送完整简报（非摘要）。

## 环境常量

```bash
MAIL_TO=tiechengsun@126.com
SMTP_HOST=smtp.126.com
SMTP_PORT=465
SMTP_USER=tiechengsun@126.com
SMTP_PASS=AXwS4p3Avd2C2KFy
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268
FEISHU_SECRET=""
FEISHU_KEYWORD=日报
```

提交前执行：

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 信息源

### 论文
- arXiv: cs.RO, cs.AI, cs.LG, cs.CV
- Papers with Code / Semantic Scholar
- 关键词：embodied AI, VLA, vision-language-action, robot manipulation, humanoid, sim2real, world model, dexterous, teleoperation, mobile manipulation, loco-manipulation

### 新闻
- 英文：The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics
- 中文：机器之心、量子位、36氪、极客公园（机器人/AI 相关）

### 开源/产品
- GitHub Trending（robotics / embodied / VLA）
- 头部公司：Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, Physical Intelligence 等

### 专题补充
- 行业公司发布会、Demo 视频
- 具身世界模型、仿真专题

## 质量控制

- 禁止虚构信息。
- 简报需推送完整内容，禁止只发摘要。
- 论文数量控制在 20 篇左右，每篇仅一句话简短摘要。
- 去重：同一论文/新闻不重复出现。
- 飞书/邮件推送失败时重试一次。

## 提交规范

```bash
git add briefings/YYYY-MM-DD.md
git commit -m "briefing: YYYY-MM-DD embodied AI daily"
git push -u origin <branch-name>
```

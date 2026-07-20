# 具身智能每日简报运行手册

## 触发条件
- 每日 cron 运行，自动生成并推送当天具身智能日报
- 日期使用北京时间当天（UTC 0 点后仍为北京时间当天）

## 运行顺序
1. 读取本运行手册与 `docs/BRIEFING_TEMPLATE.md`
2. 抓取近 24–48 小时具身智能新闻、论文、开源动态、产品发布与 demo 视频
3. 按模板写入 `briefings/YYYY-MM-DD.md`（北京日期）
4. 配置 Git 提交者并提交、推送到指定分支
5. 邮件 + 飞书推送完整简报（非摘要）

## 信息源

### 论文
- arXiv: cs.RO, cs.AI, cs.LG, cs.CV
- Papers with Code / Semantic Scholar
- 关键词：embodied AI, VLA, vision-language-action, robot manipulation, humanoid, sim2real, world model, dexterous, teleoperation, mobile manipulation, loco-manipulation, world model, simulation

### 新闻
- 英文：The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics, NVIDIA Blog
- 中文：机器之心、量子位、36氪、极客公园、新浪财经

### 开源 / 产品 / Demo
- GitHub Trending（robotics / embodied / VLA）
- Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, Physical Intelligence, Agility, Boston Dynamics, Google DeepMind, Stanford 等
- 行业发布会、demo 视频、产品量产动态

## 简报要求
- 全中文，论文标题保留英文原名
- 论文数量控制在 **20 篇以内**，每篇简短摘要
- 必含专题：世界模型、具身仿真、产品发布会 / demo 视频
- 禁止虚构；禁止只发摘要

## 常量
- 简报文件：`briefings/YYYY-MM-DD.md`
- 邮件收件人：`tiechengsun@126.com`
- SMTP：`smtp.126.com:465`
- SMTP 用户：`tiechengsun@126.com`
- 飞书 Webhook：`https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- 飞书关键词：`日报`

## 提交前配置
```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 提交与推送
```bash
git add briefings/YYYY-MM-DD.md
git commit -m "briefing: YYYY-MM-DD embodied AI daily"
git push -u origin <branch>
```

## 推送完整简报

### 邮件
- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：Markdown 转 HTML 的完整简报（含全部章节与链接），无字数上限
- 失败重试一次

### 飞书
- 将完整简报原文推送至 Webhook
- 每条消息标题必须包含关键词 `日报`
- 单条超过 15000 字则按 `##` 章节拆成多条顺序发送（例如 `日报 1/3`、`2/3`…），每条正文均含 `日报`
- `msg_type` 可用 `text`
- `FEISHU_SECRET` 非空时加签名（当前为空，无需签名）
- 失败重试一次

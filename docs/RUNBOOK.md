# 具身智能每日简报运行手册

## 目标

每日自动生成具身智能（Embodied AI）行业简报，存档 GitHub，并推送完整简报至邮件与飞书。

## 运行顺序

1. 读取本运行手册与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时具身智能新闻、论文、发布会与 Demo 视频。
3. 写入 `briefings/YYYY-MM-DD.md`（日期为北京时间当天）。
4. 执行 Git 提交并推送到 `main` 分支。
5. 读取生成的简报文件，完整推送邮件与飞书（失败重试一次）。

## 环境常量

- 简报文件：`briefings/YYYY-MM-DD.md`
- 邮件收件人：`tiechengsun@126.com`
- SMTP 主机：`smtp.126.com`
- SMTP 端口：`465`
- SMTP 用户：`tiechengsun@126.com`
- SMTP 密码：`AXwS4p3Avd2C2KFy`
- 飞书 Webhook：`https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- 飞书 Secret：（空，不启用签名）
- 飞书关键词：`日报`（标题与正文均需包含）
- Git 仓库：`SunTiecheng/embodied-ai-daily`，分支 `main`
- Git 提交前配置：
  - `user.email = SunTiecheng@users.noreply.github.com`
  - `user.name = SunTiecheng`

## 信息抓取源

### 论文源

- arXiv: cs.RO, cs.AI, cs.LG, cs.CV
- Papers with Code、Semantic Scholar
- 关键词：embodied AI, VLA, vision-language-action, robot manipulation, humanoid, sim2real, world model, dexterous, teleoperation, mobile manipulation, loco-manipulation, tactile

### 新闻源

- 英文：The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics, Benzinga, DEPLOY, The Robot Report, IIoT World
- 中文：机器之心、量子位、36 氪、极客公园、新浪财经、网易订阅、OFweek、金融界、钛媒体、证券时报、新华日报、新华网

### 开源/产品/公司

- GitHub Trending（robotics / embodied / VLA）
- 头部公司：Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, 千寻智能, 星尘智能, 智平方, 加速进化, 傅利叶, 优必选, 北京人形, Physical Intelligence, Boston Dynamics, Agility Robotics, Apptronik, Galileo Robotics, XPENG Robotics 等

## 内容要求

- 全中文，论文标题保留英文原名。
- 控制论文篇数在 20 篇左右，每篇仅“标题 + 一句话摘要 + 链接”。
- 必含两个专题：
  - 行业公司发布会、Demo 视频与硬件形态创新
  - 具身世界模型与仿真
- 禁止虚构；禁止只发摘要；使用真实来源链接。
- 去重：同一论文/新闻不重复出现。

## 提交命令

```bash
git config user.email "SunTiecheng@users.noreply.github.com"
git config user.name "SunTiecheng"
git add briefings/YYYY-MM-DD.md
git commit -m "briefing: YYYY-MM-DD embodied AI daily"
git push origin main
```

## 推送要求

### 邮件

- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：将完整 Markdown 转为 HTML，包含全部章节与链接。
- 不设字数上限。

### 飞书

- 使用 `msg_type = text`。
- 标题与正文均包含关键词“日报”。
- 推送完整简报原文。
- 单条超过 15,000 字时按 `##` 章节拆成多条顺序发送（如“日报 1/3、2/3…”）。
- 每条正文均含“日报”。
- FEISHU_SECRET 非空时加签名；当前为空，无需签名。

## 重试策略

邮件或飞书失败时，自动重试一次。若两次均失败，在输出中记录错误原因。

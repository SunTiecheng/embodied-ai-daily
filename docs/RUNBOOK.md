# 具身智能每日简报运行手册

## 运行顺序

1. 读取本运行手册与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时具身智能新闻与论文（论文控制在 20 篇以内，简短摘要）。
3. 按模板写入 `briefings/YYYY-MM-DD.md`（日期为北京时间当天）。
4. Git 提交并推送。
5. 推送成功后，读取完整简报并通过**邮件 + 飞书**推送全文（非摘要）。
6. 飞书或邮件失败时重试一次；若仍失败在日志中注明。

## 环境常量

- `MAIL_TO`: `tiechengsun@126.com`
- `SMTP_HOST`: `smtp.126.com`
- `SMTP_PORT`: `465`
- `SMTP_USER`: `tiechengsun@126.com`
- `SMTP_PASS`: `AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK`: `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET`: 空（若未来配置则启用签名）
- `FEISHU_KEYWORD`: `日报`
- 简报文件: `briefings/YYYY-MM-DD.md`

## 信息源

### 论文源

- arXiv: cs.RO, cs.AI, cs.LG, cs.CV
- Papers with Code / Semantic Scholar
- 关键词：embodied AI, VLA, vision-language-action, robot manipulation, humanoid, sim2real, world model, dexterous, teleoperation, mobile manipulation, loco-manipulation, embodied world model, simulation

### 新闻源

- 英文：The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics, Reuters, Bloomberg, NVIDIA Blog
- 中文：机器之心、量子位、36氪、极客公园、新浪财经、腾讯科技、网易科技

### 专题补充

- 行业公司发布会、demo 视频
- 具身世界模型、仿真专题（Isaac Sim / Isaac Lab, MuJoCo, Genesis, SAPIEN, RoboTwin, Habitat 等）
- 人形公司动态：Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, Physical Intelligence, Agility, Boston Dynamics, 小鹏, 赛力斯, 傅利叶等

## 简报要求

- 全中文，论文标题保留英文原名。
- 禁止虚构；每个链接必须可验证。
- 论文总数控制在 20 篇以内，每篇仅「标题 + 一句话摘要 + 链接」。
- 行业要闻 8–12 条，每条 50–80 字 + 来源链接。
- 今日必看 Top 5，每篇 150–200 字：核心贡献 + 为何重要 + 链接。
- 必须包含：行业公司发布会、demo 视频专题；具身世界模型、仿真专题。
- 日期为北京时间当天。

## Git 操作

提交前执行：

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

然后：

```bash
git add briefings/YYYY-MM-DD.md
git commit -m "briefing: YYYY-MM-DD embodied AI daily"
git push -u origin cursor/bc-620d83dd-63cc-4959-b4a9-39bb8749d939-4a34
```

## 邮件推送

- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：完整简报 Markdown 转 HTML，含全部章节与链接，无字数上限。
- SMTP 使用 SSL 端口 465。
- 失败重试一次。

## 飞书推送

- 完整简报原文推送至 `FEISHU_WEBHOOK`。
- 每条消息标题必须包含 `日报`（关键词过滤）。
- 单条超过 15000 字符时按 `##` 章节拆成多条顺序发送，例如 `日报 1/3`、`2/3`。
- 每条正文均含 `日报`。
- `msg_type` 可用 `text`。
- `FEISHU_SECRET` 非空时加签名。
- 失败重试一次。

## 质量检查

- [ ] 简报已写入 `briefings/YYYY-MM-DD.md`
- [ ] 已提交并推送成功
- [ ] 邮件已发送成功（或已记录失败）
- [ ] 飞书已发送成功（或已记录失败）
- [ ] 日期为北京时间当天
- [ ] 论文数量 ≤ 20 篇且均真实可验证
- [ ] 无虚构内容

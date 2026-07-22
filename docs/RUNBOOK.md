# 具身智能每日简报运行手册

## 每次运行顺序

1. **读取** `docs/RUNBOOK.md` 和 `docs/BRIEFING_TEMPLATE.md`
2. **抓取** 近 24–48 小时具身智能新闻与论文
3. **写入** `briefings/YYYY-MM-DD.md`（北京时间为当天）
4. **Git 提交推送** 到当前开发分支
5. **飞书 + 邮件推送完整简报**（非摘要）

## 环境常量

| 常量 | 值 |
|------|-----|
| MAIL_TO | `tiechengsun@126.com` |
| SMTP_HOST | `smtp.126.com` |
| SMTP_PORT | `465` |
| SMTP_USER | `tiechengsun@126.com` |
| SMTP_PASS | `AXwS4p3Avd2C2KFy` |
| FEISHU_WEBHOOK | `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268` |
| FEISHU_SECRET | （空） |
| FEISHU_KEYWORD | `日报` |
| 简报文件 | `briefings/YYYY-MM-DD.md` |

## 信息源

### 论文
- arXiv: cs.RO, cs.AI, cs.LG, cs.CV
- Papers with Code、Semantic Scholar
- 关键词：embodied AI, VLA, vision-language-action, robot manipulation, humanoid, sim2real, world model, dexterous, teleoperation, mobile manipulation, loco-manipulation

### 新闻
- 英文：The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics
- 中文：机器之心、量子位、36氪、极客公园

### 公司与开源
- 头部公司：Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, Physical Intelligence
- GitHub Trending（robotics / embodied / VLA）

### 专题补充
- 行业公司发布会、demo 视频
- 具身世界模型、仿真专题

## 简报结构

详见 `docs/BRIEFING_TEMPLATE.md`。

论文控制在 **20 篇以内**，每篇简短摘要即可。

## 提交与推送

提交前执行：

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

然后：

```bash
git add briefings/YYYY-MM-DD.md
git commit -m "briefing: YYYY-MM-DD embodied AI daily"
git push -u origin <branch-name>
```

## 推送规则

- 邮件主题：`具身智能日报 YYYY-MM-DD`
- 正文为完整简报（Markdown 转 HTML，含全部章节与链接）
- 飞书推送完整简报原文，每条标题含 `日报` 关键词
- 单条超过 15000 字则按 `##` 章节拆分，每条标题含 `日报`
- `msg_type` 可用 `text`
- `FEISHU_SECRET` 非空时加签名
- 失败重试一次

## 质量红线

- 禁止虚构
- 禁止只发摘要
- 论文篇数控制在 20 篇以内
- 简报日期为北京时间当天

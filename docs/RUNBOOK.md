# 具身智能每日简报 — 运行手册

## 每次运行顺序

1. 读取 `docs/RUNBOOK.md` 和 `docs/BRIEFING_TEMPLATE.md`
2. 抓取近 24–48 小时具身智能新闻与论文（含世界模型、仿真专题）
3. 写入 `briefings/YYYY-MM-DD.md`（北京时间当天）
4. Git 提交推送
5. 飞书 + 邮件推送**完整简报**（非摘要）

## 环境常量

| 变量 | 值 |
|------|-----|
| MAIL_TO | tiechengsun@126.com |
| SMTP_HOST | smtp.126.com |
| SMTP_PORT | 465 |
| SMTP_USER | tiechengsun@126.com |
| SMTP_PASS | （Automation Secrets 中配置） |
| FEISHU_WEBHOOK | （Automation Secrets 中配置） |
| FEISHU_SECRET | 空则不加签名 |
| FEISHU_KEYWORD | 简报（飞书机器人安全设置中的自定义关键词） |

## 信息源

### 论文
- arXiv: `cat:cs.RO` + `cat:cs.CV` / `cat:cs.LG` 关键词过滤，近 48h
- 关键词: embodied AI, VLA, world model, humanoid, sim2real, manipulation, navigation

### 新闻
- 英文: The Robot Report, IEEE Spectrum, NVIDIA Blog
- 中文: 机器之心、量子位、36氪、新华网

## Git 提交

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
git add briefings/YYYY-MM-DD.md
git commit -m "briefing: YYYY-MM-DD embodied AI daily"
git push -u origin <branch>
```

## 推送

push 成功后执行：

```bash
python3 scripts/send_briefing.py briefings/YYYY-MM-DD.md
```

### 邮件
- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：完整简报 Markdown 转 HTML，含全部章节与链接

### 飞书
- 完整简报原文推送至 FEISHU_WEBHOOK
- 每条消息须含飞书机器人配置的关键词（当前为「简报」）
- 单条超 15000 字按 `##` 章节拆成多条（简报 1/N、2/N…）
- `msg_type`: text
- FEISHU_SECRET 非空时加签名

## 质量要求

- 禁止虚构
- 禁止只发摘要
- 飞书或邮件失败重试一次
- 简报须含「世界模型专题」「具身仿真专题」独立章节

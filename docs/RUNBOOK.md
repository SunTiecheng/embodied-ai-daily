# 具身智能每日简报 — 运行手册

## 流程

1. 读取 `docs/RUNBOOK.md` 和 `docs/BRIEFING_TEMPLATE.md`
2. 日期：北京时间 `TZ=Asia/Shanghai date '+%Y-%m-%d'`
3. 抓取近 24–48 小时具身智能新闻与 arXiv 论文（cs.RO + cs.AI/LG/CV 具身相关）
4. 写入 `briefings/YYYY-MM-DD.md`（须含「世界模型专题」「具身仿真专题」独立章节）
5. Git 提交推送前执行：
   ```bash
   git config user.email SunTiecheng@users.noreply.github.com
   git config user.name SunTiecheng
   ```
6. Push 成功后推送完整简报：
   ```bash
   python3 scripts/send_briefing.py briefings/YYYY-MM-DD.md
   ```

## 推送配置

| 变量 | 说明 |
|------|------|
| MAIL_TO | tiechengsun@126.com |
| SMTP_HOST | smtp.126.com |
| SMTP_PORT | 465 |
| SMTP_USER | tiechengsun@126.com |
| SMTP_PASS | 环境变量或 Automation 常量 |
| FEISHU_WEBHOOK | 飞书机器人 Webhook |
| FEISHU_SECRET | 非空时启用签名 |
| FEISHU_KEYWORD | 日报（标题须含此关键词） |

## 飞书注意事项

- 实际关键词过滤可能为「简报」，标题使用「具身智能简报日报 YYYY-MM-DD」
- 单条超 15000 字按 `##` 章节拆分（日报 1/3、2/3…）
- 失败重试一次

## 邮件

- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：完整简报 Markdown 转 HTML，不设字数上限

## arXiv 抓取

- 列表页：`https://arxiv.org/list/cs.RO/recent`
- 标题：逐篇访问 `https://arxiv.org/abs/{id}` 或 export API
- 论文速递按 VLA / Manipulation / Navigation / Humanoid / Sim2Real / 其他 分类

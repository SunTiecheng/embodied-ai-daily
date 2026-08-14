# 具身智能每日简报

由 Cursor Automation 自动生成，每日整理具身智能（Embodied AI）行业新闻、论文与开源动态。

## 目录结构

```
docs/
  RUNBOOK.md           # 运行手册与推送配置
  BRIEFING_TEMPLATE.md # 每日简报 Markdown 模板
scripts/
  send_briefing.py     # 邮件 + 飞书推送脚本
briefings/
  YYYY-MM-DD.md        # 每日完整简报
```

## 阅读/推送方式

- **GitHub**：本仓库 `briefings/` 目录查看完整版。
- **邮件**：每日推送完整简报（Markdown 转 HTML），主题「具身智能日报 YYYY-MM-DD」。
- **飞书**：每日推送完整简报原文，超过 15000 字按章节拆分多条发送。

## 简报格式

每份简报约 30–45 分钟阅读量，包含：

- 今日必看 Top 5
- 行业要闻（8–12 条）
- 行业公司发布会 & Demo 视频专题
- 具身世界模型 & 仿真专题
- 论文速递（20 篇以内，按主题分类）
- 开源 & 产品动态
- 今日关键词

论文标题保留英文，其余内容使用中文。

## 运行手册

详见 [`docs/RUNBOOK.md`](docs/RUNBOOK.md)。

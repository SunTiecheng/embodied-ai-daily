# 具身智能日报模板

> 本文件规范每日简报的 Markdown 结构。实际生成文件名为 `briefings/YYYY-MM-DD.md`（北京时间当天）。

## 模板正文

```markdown
# 具身智能日报 | YYYY-MM-DD

> 预计阅读 30–45 分钟 | 论文 N 篇 | 生成时间 HH:MM 北京时间

## 今日必看 Top 5

（每篇 150–200 字：核心贡献 + 为何重要 + 链接。必须为当日最有价值的条目。）

### 1. 标题

正文……

[来源](URL)

### 2. 标题

……

## 行业要闻

1. **标题** — 50–80 字摘要 + 来源链接。
2. ……

## 专题：行业公司发布会 & demo 视频

（集中报道近 24–48 小时发布会、产品 demo、视频、大事件，按公司/项目分类，附视频/链接。）

## 专题：具身世界模型 & 仿真

（报道世界模型、仿真平台、Sim2Real、数据集等进展，附论文/项目链接。）

## 论文速递

> 论文总数控制在 20 篇以内，每篇仅「标题 + 一句话摘要 + 链接」。

### VLA / 视觉-语言-动作

- **Paper Title** — 一句话摘要 — [arXiv:XXXX.XXXXX](URL)

### 操作 / Manipulation

- **Paper Title** — 一句话摘要 — [arXiv:XXXX.XXXXX](URL)

### 导航 / Locomotion

- **Paper Title** — 一句话摘要 — [arXiv:XXXX.XXXXX](URL)

### 人形 / Humanoid

- **Paper Title** — 一句话摘要 — [arXiv:XXXX.XXXXX](URL)

### Sim2Real / 仿真 / 世界模型

- **Paper Title** — 一句话摘要 — [arXiv:XXXX.XXXXX](URL)

### 其他

- **Paper Title** — 一句话摘要 — [arXiv:XXXX.XXXXX](URL)

## 开源 & 产品

1. **项目名称** — 做什么 — [GitHub](URL) / 链接 / ⭐ 动态
2. ……

## 今日关键词

（5–10 个关键词 + 一句趋势概括）
```

## 注意事项

- 标题层级：`#` 用于主标题，`##` 用于大章节，`###` 用于 Top 5 条目与论文分类内的子标题。
- 飞书推送拆分章节时以 `##` 为界。
- 所有外部链接必须真实可访问，禁止虚构。

# 具身智能每日简报运行手册

## 触发时间

每日自动生成一次（北京时间 07:30，UTC 23:30）。

## 运行顺序

1. 读取本文档与 `docs/BRIEFING_TEMPLATE.md`
2. 抓取近 24-48 小时具身智能新闻、论文、开源/产品动态
3. 按模板生成 `briefings/YYYY-MM-DD.md`（日期为北京时间当天）
4. 提交并推送至当前 Git 分支
5. 邮件 + 飞书推送**完整简报**（非摘要）

## 环境常量

- `MAIL_TO=tiechengsun@126.com`
- `SMTP_HOST=smtp.126.com`
- `SMTP_PORT=465`
- `SMTP_USER=tiechengsun@126.com`
- `SMTP_PASS=AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET=`（空）
- `FEISHU_KEYWORD=日报`
- 简报路径：`briefings/YYYY-MM-DD.md`

## 提交前配置

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 推送渠道

### 邮件

- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：完整简报 Markdown 转 HTML，包含全部章节与链接，不限制字数
- 发送失败重试一次

### 飞书

- 将完整简报原文推送至 `FEISHU_WEBHOOK`
- 每条消息标题须含 `日报`（关键词过滤）
- 单条超过 15000 字时按 `## 章节` 拆成多条顺序发送（如 `日报 1/3`、`2/3`…），每条正文均含 `日报`
- `msg_type` 可用 `text`
- `FEISHU_SECRET` 非空时加签名
- 发送失败重试一次

## 内容约束

- 禁止虚构新闻、论文或链接
- 禁止只发送摘要，必须发送完整简报
- 论文控制在 20 篇左右，每篇仅简短摘要
- 补充：行业公司发布会、Demo 视频等专题
- 补充：具身世界模型、仿真专题
- 全中文，论文标题保留英文原名

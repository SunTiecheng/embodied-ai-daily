# 具身智能每日简报运行手册

## 目标
每日自动生成并推送一份具身智能（Embodied AI）行业简报，覆盖新闻、论文、开源与产品动态，完整版推送至邮件与飞书。

## 运行流程
1. 读取 `docs/BRIEFING_TEMPLATE.md` 了解今日简报结构。
2. 抓取近 24–48 小时（以北京时间当天计）具身智能相关新闻、论文、发布会与 demo 视频。
3. 按模板撰写 `briefings/YYYY-MM-DD.md`（使用北京时间当天日期）。
4. 提交前配置 git：
   ```bash
   git config user.email SunTiecheng@users.noreply.github.com
   git config user.name SunTiecheng
   ```
5. 提交并推送：
   ```bash
   git add briefings/YYYY-MM-DD.md
   git commit -m "Add briefing for YYYY-MM-DD"
   git push -u origin <current-branch>
   ```
6. push 成功后，读取完整简报文件，执行邮件与飞书推送。

## 内容要求
- 必须有：今日必看 Top 5、行业要闻、世界模型专题、具身仿真专题、论文速递、开源 & 产品、今日关键词。
- 补充行业发布会、demo 视频等专题。
- 论文控制在 20 篇左右，简短摘要即可，含 arXiv 链接。
- 禁止虚构；引用真实来源链接。
- 不限制字数，必须推送完整简报，禁止只发摘要。

## 推送要求
- 邮件：主题 `具身智能日报 YYYY-MM-DD`，正文为 Markdown 转 HTML 的完整简报，发送至 `MAIL_TO`。
- 飞书：msg_type `text`，将完整简报原文推送至 `FEISHU_WEBHOOK`。每条消息标题须含 `日报`（关键词过滤）。若单条超过 15000 字，按 `##` 章节拆分为多条顺序发送（如 `日报 1/3`、`2/3`），每条正文均含 `日报`。`FEISHU_SECRET` 非空时加签名。
- 飞书或邮件失败重试一次。

## 常量
```bash
MAIL_TO=tiechengsun@126.com
SMTP_HOST=smtp.126.com
SMTP_PORT=465
SMTP_USER=tiechengsun@126.com
SMTP_PASS=AXwS4p3Avd2C2KFy
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268
FEISHU_SECRET=
FEISHU_KEYWORD=日报
```

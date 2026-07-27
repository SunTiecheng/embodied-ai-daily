# 具身智能每日简报运行手册

## 目标

为仓库 `SunTiecheng/embodied-ai-daily` 的 `main` 分支每日生成一份具身智能（Embodied AI）领域简报，文件路径为 `briefings/YYYY-MM-DD.md`（以北京时间当天为准）。

## 每次运行顺序

1. 读取 `docs/RUNBOOK.md` 和 `docs/BRIEFING_TEMPLATE.md`。
2. 通过可靠信源（WebSearch、权威媒体、arXiv）抓取近 24-48 小时的新闻、论文、开源/产品动态、公司发布会及 demo 视频。
3. 按模板撰写简报，确保：
   - 不虚构任何事件、数据或论文。
   - 论文总数控制在 20 篇左右，仅提供简短摘要。
   - 补充行业公司发布会、demo 视频、世界模型与仿真专题。
4. 提交前执行：
   - `git config user.email SunTiecheng@users.noreply.github.com`
   - `git config user.name SunTiecheng`
5. 将简报文件 `git add`、`git commit` 并 `git push -u origin <branch>`。
6. Push 成功后，读取 `briefings/YYYY-MM-DD.md` 全文并推送：
   - 邮件：主题为「具身智能日报 YYYY-MM-DD」，正文为 Markdown 转 HTML 的完整简报，无字数上限。
   - 飞书：将完整简报原文推送至 `FEISHU_WEBHOOK`，每条消息标题含「日报」；单条超过 15000 字则按 `##` 章节拆成多条顺序发送（如“日报 1/3”）。
   - 邮件或飞书失败时重试一次。

## 常量

- `MAIL_TO=tiechengsun@126.com`
- `SMTP_HOST=smtp.126.com`
- `SMTP_PORT=465`
- `SMTP_USER=tiechengsun@126.com`
- `SMTP_PASS=AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET=`（空，不加签名）
- `FEISHU_KEYWORD=日报`

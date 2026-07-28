# 具身智能日报运行手册

本手册定义每日简报的自动化运行流程，供 Cursor Cloud Agent 执行。

## 常量

| 常量 | 值 |
|------|-----|
| 仓库 | `SunTiecheng/embodied-ai-daily` |
| 基础分支 | `main` |
| 开发分支 | `cursor/bc-f8009c84-4e78-4693-8f39-b3e682d79c1c-149a` |
| 简报文件 | `briefings/YYYY-MM-DD.md`（日期为北京时间当天） |
| MAIL_TO | `tiechengsun@126.com` |
| SMTP_HOST | `smtp.126.com` |
| SMTP_PORT | `465` |
| SMTP_USER | `tiechengsun@126.com` |
| SMTP_PASS | `AXwS4p3Avd2C2KFy` |
| FEISHU_WEBHOOK | `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268` |
| FEISHU_SECRET | （空） |
| FEISHU_KEYWORD | `日报` |

## 每次运行顺序

1. 读取本文件 `docs/RUNBOOK.md` 与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24–48 小时（优先）具身智能行业新闻、论文、开源/产品动态、发布会与 demo 视频。
   - 论文源：arXiv (cs.RO / cs.AI / cs.LG / cs.CV)、Papers with Code、Semantic Scholar。
   - 新闻源：The Robot Report、TechCrunch、IEEE Spectrum、机器之心、量子位、36氪、极客公园。
   - 公司/产品：Figure、1X、Tesla Optimus、Unitree、宇树、智元、银河通用、Physical Intelligence、Hyundai/Boston Dynamics、BYD、EngineAI、Generative Bionics 等。
3. 按模板撰写 `briefings/YYYY-MM-DD.md`（全中文，论文标题保留英文）。
   - 论文总数控制在 **20 篇**左右，每篇仅标题 + 一句话摘要 + 链接。
   - 必须补充：行业公司发布会/demo 视频专题、具身世界模型/仿真专题。
4. 执行 `git config user.email SunTiecheng@users.noreply.github.com` 与 `git config user.name SunTiecheng`。
5. `git add briefings/YYYY-MM-DD.md`，`git commit -m "briefing: YYYY-MM-DD embodied AI daily"`，`git push -u origin <开发分支名>`。
6. Push 成功后，读取刚生成的简报文件全文，依次发送：
   - **邮件**：主题 `具身智能日报 YYYY-MM-DD`，正文为完整简报（Markdown 转 HTML，含全部章节与链接）。
   - **飞书**：将完整简报原文推送至 `FEISHU_WEBHOOK`。
     - 每条消息标题须含 `日报`（关键词过滤）。
     - 单条正文超过 15000 字则按 `##` 章节拆成多条顺序发送（如 `日报 1/3`、`2/3`…）。
     - `msg_type` 可用 `text`；`FEISHU_SECRET` 非空时加签名。
7. 若邮件或飞书失败，重试一次。

## 注意事项

- 禁止虚构内容；所有论文/新闻必须附真实链接。
- 禁止只发送摘要，必须推送完整简报。
- 多提交、小提交；每个逻辑变更独立 commit。

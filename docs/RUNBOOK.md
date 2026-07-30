# 具身智能每日简报运行手册

## 1. 环境常量

- MAIL_TO: `tiechengsun@126.com`
- SMTP_HOST: `smtp.126.com`
- SMTP_PORT: `465`
- SMTP_USER: `tiechengsun@126.com`
- SMTP_PASS: `AXwS4p3Avd2C2KFy`
- FEISHU_WEBHOOK: `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- FEISHU_SECRET: ``（空）
- FEISHU_KEYWORD: `日报`
- 简报文件: `briefings/YYYY-MM-DD.md`（日期为北京时间当天）
- GitHub 仓库: `SunTiecheng/embodied-ai-daily`
- 开发分支: `cursor/bc-11364d17-64cc-407a-99e2-9f9e2be17ed2-5bdd`（以当前运行指定分支为准）

## 2. 运行顺序

1. 读取本手册与 `docs/BRIEFING_TEMPLATE.md`。
2. 抓取近 24-48 小时具身智能新闻与论文。
3. 写入 `briefings/YYYY-MM-DD.md`（北京时间当天）。
4. 提交前执行：`git config user.email SunTiecheng@users.noreply.github.com` 和 `git config user.name SunTiecheng`。
5. `git add briefings/YYYY-MM-DD.md` → `git commit` → `git push -u origin <分支>`。
6. Push 成功后，读取 `briefings/YYYY-MM-DD.md` 全文并推送完整简报（非摘要）：
   - 邮件：主题「具身智能日报 YYYY-MM-DD」，正文为完整 Markdown 转 HTML，含全部章节与链接，不设字数上限。
   - 飞书：将完整简报原文推送至 `FEISHU_WEBHOOK`。每条消息标题须含「日报」（关键词过滤）。单条超 15000 字则按 `##` 章节拆成多条顺序发送（如 日报 1/3、2/3…），每条正文均含「日报」。`msg_type` 可用 `text`。`FEISHU_SECRET` 非空时加签名。
7. 飞书或邮件失败重试一次。

## 3. 信息源

- 论文：arXiv（cs.RO, cs.AI, cs.LG, cs.CV）、Papers with Code、Semantic Scholar。
- 新闻：The Robot Report、TechCrunch Robotics、IEEE Spectrum Robotics、机器之心、量子位、36 氪、极客公园。
- 开源/产品：GitHub Trending、Figure、1X、Tesla Optimus、Unitree、宇树、智元、银河通用、Physical Intelligence 等。
- 专题补充：行业公司发布会、Demo 视频、具身世界模型、仿真。

## 4. 内容约束

- 禁止虚构。
- 禁止只发摘要。
- 论文篇数控制在 20 篇左右，论文简短摘要即可。
- 全中文，论文标题保留英文原名。
- 去重：同一论文/新闻不重复。
- 质量：Top 5 必须是当日最有价值的条目。

## 5. 提交信息规范

- 提交信息：`briefing: YYYY-MM-DD embodied AI daily`

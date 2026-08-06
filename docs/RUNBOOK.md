# 具身智能每日简报运行手册

## 运行前准备

- 日期：北京时间当天，格式 `YYYY-MM-DD`。
- 简报文件：`briefings/YYYY-MM-DD.md`。
- 环境常量：
  - `MAIL_TO=tiechengsun@126.com`
  - `SMTP_HOST=smtp.126.com`, `SMTP_PORT=465`
  - `SMTP_USER=tiechengsun@126.com`, `SMTP_PASS=AXwS4p3Avd2C2KFy`
  - `FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
  - `FEISHU_SECRET=`, `FEISHU_KEYWORD=日报`

## 运行顺序

1. **读取模板**：`docs/BRIEFING_TEMPLATE.md`。
2. **抓取信息**：
   - 论文：arXiv(cs.RO/AI/LG/CV)、Papers with Code、Semantic Scholar；关键词 embodied AI、VLA、vision-language-action、robot manipulation、humanoid、world model、sim2real、teleoperation 等。
   - 新闻：The Robot Report、IEEE Spectrum Robotics、TechCrunch、机器之心、量子位、36氪、极客公园等。
   - 开源/产品：GitHub Trending、Figure、1X、Tesla Optimus、Unitree/宇树、智元、银河通用、Physical Intelligence 等。
   - 专题：行业发布会、demo 视频、具身世界模型、仿真/仿真器。
3. **生成简报**：使用模板写入 `briefings/YYYY-MM-DD.md`（全中文，论文标题保留英文，论文控制在20篇，简短摘要）。
4. **Git 提交**：
   - `git config user.email SunTiecheng@users.noreply.github.com`
   - `git config user.name SunTiecheng`
   - `git add briefings/YYYY-MM-DD.md`
   - `git commit -m "briefing: YYYY-MM-DD embodied AI daily"`
   - `git push -u origin <开发分支>`（具体分支以当前 checkout 的开发分支为准）。
5. **推送简报**：push 成功后，读取 `briefings/YYYY-MM-DD.md` 全文：
   - **邮件**：主题 `具身智能日报 YYYY-MM-DD`，Markdown 转 HTML 发送完整简报；失败重试一次。
   - **飞书**：将完整原文推送至 `FEISHU_WEBHOOK`；标题须含 `日报`；单条超 15000 字按 `##` 章节拆分；`FEISHU_SECRET` 非空时加签名；失败重试一次。

## 质量检查

- [ ] 简报文件已生成，日期为北京时间当天。
- [ ] 论文数量控制在 20 篇左右，含简短摘要。
- [ ] 无虚构内容，新闻/论文均附真实来源链接。
- [ ] Git 提交成功并已推送。
- [ ] 邮件、飞书均成功送达（失败已重试）。

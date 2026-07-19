# 具身智能每日简报运行手册

本仓库为「具身智能每日简报」自动化流程。每次运行请按以下顺序执行。

## 环境常量（由运行时环境注入，勿提交到 Git）

- `MAIL_TO`: 邮件收件地址
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`: 邮件 SMTP 配置
- `FEISHU_WEBHOOK`: 飞书机器人 Webhook URL
- `FEISHU_SECRET`: 飞书签名密钥（可为空）
- `FEISHU_KEYWORD`: 飞书关键词过滤（如 `日报`）
- 简报文件：`briefings/YYYY-MM-DD.md`（日期为北京时间当天）

提交前执行：

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 运行顺序

1. **读取模板**：打开 `docs/BRIEFING_TEMPLATE.md`，确认当日简报结构。
2. **抓取信息**：搜索近 24–48 小时（优先）具身智能新闻、论文、发布会、Demo 视频。重点关注：
   - 论文：arXiv cs.RO / cs.AI / cs.LG / cs.CV，关键词 embodied AI、VLA、vision-language-action、robot manipulation、humanoid、world model、sim2real、simulation、teleoperation、mobile manipulation。
   - 新闻：The Robot Report、TechCrunch、IEEE Spectrum、机器之心、量子位、36氪、极客公园、新浪财经等。
   - 公司动态：Figure、1X、Tesla Optimus、Unitree、宇树、智元、AgiBot、银河通用、Physical Intelligence、NVIDIA、小米、腾讯、阿里等。
3. **生成简报**：按模板写入 `briefings/YYYY-MM-DD.md`。补充：
   - 行业公司发布会、Demo 视频等专题；
   - 具身世界模型专题；
   - 具身仿真专题。
   论文总量控制在 20 篇左右，简短摘要即可。禁止虚构。
4. **Git 提交**：
   ```bash
   git add briefings/YYYY-MM-DD.md
   git commit -m "briefing: YYYY-MM-DD embodied AI daily"
   git push -u origin <分支名>
   ```
5. **推送简报**：push 成功后，读取 `briefings/YYYY-MM-DD.md` 全文，分别通过邮件与飞书推送完整版（非摘要）：
   - 邮件主题：`具身智能日报 YYYY-MM-DD`，正文 Markdown 转 HTML，含全部章节与链接。
   - 飞书：使用 `FEISHU_WEBHOOK` 发送完整简报原文。每条消息标题含关键词（如 `日报`）。单条超过 15,000 字则按 `##` 章节拆成多条顺序发送（`日报 1/3`、`日报 2/3`…）。`msg_type` 可用 `text`。`FEISHU_SECRET` 非空时加签名。飞书或邮件失败均重试一次。

## 质量检查

- [ ] 文件已写入并 push 成功。
- [ ] 邮件、飞书均推送成功或已重试一次。
- [ ] 日期为北京时间当天。
- [ ] 无虚构内容，论文/新闻均附来源链接。
- [ ] 论文数量控制在 20 篇左右。
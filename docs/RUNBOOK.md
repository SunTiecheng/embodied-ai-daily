# 具身智能每日简报运行手册

## 运行顺序

1. 读取本运行手册与 `docs/BRIEFING_TEMPLATE.md`
2. 抓取近 24–48 小时具身智能新闻、论文、发布会、Demo 视频、世界模型与仿真动态
3. 按模板写入 `briefings/YYYY-MM-DD.md`（日期为北京时间当天）
4. Git 提交并推送至当前工作分支
5. 推送完整简报（非摘要）：邮件 + 飞书

## 环境常量

- `MAIL_TO`: `tiechengsun@126.com`
- `SMTP_HOST`: `smtp.126.com`
- `SMTP_PORT`: `465`
- `SMTP_USER`: `tiechengsun@126.com`
- `SMTP_PASS`: `AXwS4p3Avd2C2KFy`
- `FEISHU_WEBHOOK`: `https://open.feishu.cn/open-apis/bot/v2/hook/f978e1ee-2af3-437a-8d95-a6b5a68a9268`
- `FEISHU_SECRET`: （空）
- `FEISHU_KEYWORD`: `日报`
- 简报文件: `briefings/YYYY-MM-DD.md`

## 提交前配置

```bash
git config user.email SunTiecheng@users.noreply.github.com
git config user.name SunTiecheng
```

## 信息源

### 论文源
- arXiv: `cs.RO`, `cs.AI`, `cs.LG`, `cs.CV`
- Papers with Code、Semantic Scholar
- 关键词: `embodied AI`, `VLA`, `vision-language-action`, `robot manipulation`, `humanoid`, `sim2real`, `world model`, `dexterous`, `teleoperation`, `mobile manipulation`, `loco-manipulation`, `embodied world model`, `simulation`

### 新闻源
- 英文: The Robot Report, TechCrunch Robotics, IEEE Spectrum Robotics, NVIDIA Blog
- 中文: 机器之心, 量子位, 36氪, 极客公园

### 开源/产品/公司动态
- GitHub Trending（robotics / embodied / VLA）
- 头部公司: Figure, 1X, Tesla Optimus, Unitree, 宇树, 智元, 银河通用, Physical Intelligence, Agility, Boston Dynamics 等

### 专题补充
- 行业公司发布会、新品 Demo 视频
- 具身世界模型、仿真与 Sim2Real 专题

## 简报约束

- 全中文，论文标题保留英文原名
- 论文总量控制在 **20 篇** 左右，每篇仅一句话简短摘要
- 禁止虚构信息，禁止只发送摘要
- 邮件与飞书均推送完整简报；飞书单条超过 15000 字按 `##` 章节拆分多条顺序发送，每条标题含「日报」
- 飞书 `msg_type` 可用 `text`；`FEISHU_SECRET` 非空时加签名
- 飞书或邮件失败时重试一次

## 推送说明

### 邮件
- 主题：`具身智能日报 YYYY-MM-DD`
- 正文：Markdown 转 HTML，包含全部章节与链接
- 不设字数上限

### 飞书
- 将完整简报原文推送至 `FEISHU_WEBHOOK`
- 每条消息标题须含「日报」关键词
- 单条超过 15000 字按 `##` 章节拆分，如 `日报 1/3`、`日报 2/3`
- 每条正文均含「日报」

## 质量检查

- [ ] 文件已写入且 push 成功
- [ ] 邮件已发送（如失败已重试一次）
- [ ] 飞书已发送（如失败已重试一次）
- [ ] 日期为北京时间当天
- [ ] 论文数控制在 20 篇左右
- [ ] 无虚构信息

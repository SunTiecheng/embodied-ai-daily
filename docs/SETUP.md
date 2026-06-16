# Cursor Automation 配置说明

## 1. 创建 GitHub 远程仓库

1. 在 GitHub 新建空仓库，例如 `embodied-ai-daily`
2. 在本地执行：

```powershell
cd C:\Users\S094\embodied-ai-daily
git remote add origin https://github.com/SunTiecheng/embodied-ai-daily.git
git add .
git commit -m "init: embodied AI daily briefing archive"
git push -u origin main
```

3. 在 Cursor Cloud Agents 设置中确保该仓库已授权

## 2. 创建 Cursor Automation

在 Cursor 中打开 **Automations → New automation**，填入以下配置：

| 字段 | 值 |
|------|-----|
| 名称 | 具身智能每日简报 |
| 触发 | 每天 07:30（北京时间，cron 见下） |
| 仓库 | `SunTiecheng/embodied-ai-daily`，分支 `main` |

**Cron 表达式（UTC，对应北京时间 07:30）：**

```
30 23 * * *
```

## 3. Agent 指令

将 `docs/automation-prompt.md` 的全文粘贴到 Automation 的 Instructions 字段。

## 4. PushPlus Token

在 Automation 的 Instructions 里，把 `PUSHPLUS_TOKEN` 占位符换成你的 Token（参考本地文件 `docs/automation-prefill.local.json`，该文件已加入 `.gitignore` 不会上传 GitHub）。

**安全提示：** 若 Token 曾在聊天中发送过，建议在 [PushPlus 控制台](https://www.pushplus.plus/) 重置后再填入 Automation。

## 5. 测试 PushPlus（可选）

```powershell
$env:PUSHPLUS_TOKEN = "你的token"
.\scripts\send-pushplus.ps1 -Title "测试" -Content "具身智能简报推送测试"
```

## 6. 手动试跑

保存 Automation 后，在 Automations 界面点击 **Run now** 验证：

- `briefings/YYYY-MM-DD.md` 是否生成并 push 到 GitHub
- 微信是否收到 PushPlus 消息

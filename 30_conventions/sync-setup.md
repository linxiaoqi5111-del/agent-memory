---
title: 同步机制 (Mac launchd 自动双向同步)
type: convention
agent: devin
source: 部署记录
date: 2026-06-28
tags: [convention, sync, infra, mac]
status: verified
---

# 同步机制

本 vault 在 **a77 Mac** 上通过 launchd 定时任务**自动双向同步**,你无需手动 pull/push。

## 怎么跑的
- 脚本:`/Users/a77/bin/agent-memory-sync.sh`
- 调度:`~/Library/LaunchAgents/com.a77.agent-memory-sync.plist`(`StartInterval` 180 秒 + 开机自启)
- 每次执行:`commit 本地改动 → git pull --rebase --autostash → push`
- 凭证:复用系统 git(`gh` 以 `linxiaoqi5111-del` 登录),无需手输 token
- 日志:`/Users/a77/agent-memory-sync.out.log`、`.err.log`、脚本内 echo

## 效果
- 你在 Obsidian 里写/改 → 最多 3 分钟自动推到 GitHub
- 别的 Agent(Devin 等)push 的新笔记 → 最多 3 分钟自动拉到 Mac,Obsidian 自动刷新

## 冲突处理
- 若 rebase 遇冲突,脚本会 `rebase --abort` 并在日志记 `needs manual resolution`,**不会**强推或丢改动 → 需要人工解决一次。

## 常用运维(在 Mac 上)
```bash
# 手动跑一次
bash /Users/a77/bin/agent-memory-sync.sh
# 看日志
tail -20 /Users/a77/agent-memory-sync.out.log
# 重载任务
launchctl unload ~/Library/LaunchAgents/com.a77.agent-memory-sync.plist
launchctl load -w ~/Library/LaunchAgents/com.a77.agent-memory-sync.plist
# 确认在跑
launchctl list | grep agent-memory
```

> 注:`.obsidian/workspace*` 已在 `.gitignore` 忽略(每台机器不同),其余 `.obsidian/` 配置会同步,方便多端共享设置。

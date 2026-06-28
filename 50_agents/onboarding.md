---
title: 开场白 (接入任意新会话)
type: agent-card
agent: devin
source: 设计约定
date: 2026-06-28
tags: [agent-card, onboarding, bootstrap, core]
related: ["[[devin]]", "[[grok]]", "[[../30_conventions/preferences]]"]
---

# 开场白 — 让任意新会话立刻进入状态

给新开的一次性 Devin / 任何不自动读文件的 agent 用。**复制对应版本粘到对话开头即可。**

## A. 能读到仓库文件的会话（Devin / Cursor 等，在 Mac 本机的 repo 里）

```
开始前先读取记忆底座并严格遵守，再动手：
1. 读 `.agent-memory/30_conventions/preferences.md` —— 我的偏好与教学模式（中文；讲原理 + 给技术选型/替代方案对比；标注可复用知识点；照顾非科班背景）。这些是硬性要求。
2. 读本项目笔记 `.agent-memory/20_projects/<repo>.md` —— 背景、关键决策、任务看板。
3. Git：开工先报 `git status --short && git branch --show-current`；大任务开分支，合并 main 必须等我确认。
4. 完工后按 `.agent-memory/40_playbooks/devin-writeback.md` 回写到 `20_projects/<repo>.md`。
（`.agent-memory/` 是 repo 内指向 vault 的软链；若不存在，路径用 `/Users/a77/agent-memory/`。）
```

## B. 读不到文件的会话（Grok 等）

> 先粘下面这句，再把 `30_conventions/preferences.md` 全文贴进去。

```
以下是我的长期偏好与人设，本次对话请全程严格遵守（尤其“教学模式”：讲原理、给技术选型对比、标注可复用知识点、用中文）。读完确认后再开始：

<把 preferences.md 全文粘贴到这里>
```

## 备注
- Claude Code 自动读 `CLAUDE.md`、Codex 自动读 `AGENTS.md`，这两类**通常无需开场白**；但若发现没生效，也可贴 A 版强化。
- `<repo>` 替换成实际仓库短名：`finhot` / `finance-workspace-private` / `knowledge-base-private` / `finance-research-site`。

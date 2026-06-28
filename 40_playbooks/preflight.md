---
title: 开工 preflight + 红线硬拦截 (用法)
type: playbook
agent: all
source: 设计约定 (2026-06-28)
date: 2026-06-28
tags: [playbook, preflight, pre-commit, security, core]
related: ["[[devin-writeback]]", "[[../30_conventions/preferences]]", "[[../50_agents/claude-hooks]]"]
status: verified
---

# 开工 preflight + 红线硬拦截

把"开工读记忆 + 看 git + 红线"和"禁提交危险文件"从习惯变成半自动/强制。两档配合：preflight 是**软提醒**，pre-commit 是**硬拦截**。

## ① preflight 脚本（软提醒，开工跑一次）
- 位置：`agent-memory/preflight.sh`（repo 内经软链调用）。
- 用法：在任一 repo 目录下
  ```sh
  bash .agent-memory/preflight.sh
  ```
- 输出：① Git 现状（分支 + `status --short`）② 红线提醒 ③ 本项目 `20_projects/<repo>.md` 摘要 ④ 完工回写提醒。自动识别当前 repo。
- Claude Code：SessionStart hook（`.claude/hooks/load-memory.sh`）已顺带注入「Git 现状」，无需手动跑；Codex/Devin/人 手动跑这句即可。

## ② 红线 pre-commit 硬拦截（程序级强制）
- 配置：各仓 `.pre-commit-config.yaml`（已提交，跨机复用）。
- 规则：`detect-private-key` + `check-added-large-files`(>5MB) + `check-merge-conflict` + 自定义红线（`.env*`/`*.pem|key`/`*.pdf|zip|duckdb|db`/`.DS_Store`/`__pycache__`，放行 `.env.example|sample|template`）。
- **新机首次启用（每台机器一次）：**
  ```sh
  pip install pre-commit && pre-commit install
  ```
  （在每个 repo 目录各跑一次 `pre-commit install`。）
- 命中后提交会失败并打印红线提示。确需提交：`git commit --no-verify`（慎用）。
- 注意：git hook 是本机的、不随仓库走；`.pre-commit-config.yaml` 随仓库走，所以换机只需重装 + install。

## 适用 agent
- 本机（Claude/Codex/人）：preflight 软链直接跑；pre-commit 本机 install 后自动生效。
- Devin/云端：repo 里没有 `.agent-memory` 软链，preflight 走不通；改为读 `AGENTS.md` + 用 PAT clone `agent-memory`；pre-commit 若在其 VM 提交也需先 `pre-commit install`。

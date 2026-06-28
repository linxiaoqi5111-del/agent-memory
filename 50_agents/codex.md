---
title: Codex 接入约定卡
type: agent-card
agent: codex
source: 设计约定
date: 2026-06-28
tags: [agent-card, codex]
---

# Codex — 系统性规划 (Planner)

## 角色
做架构/方案设计、任务拆解。是协作链的**规划节点**，承上（调研）启下（执行）。

## 读
- 读 `00_inbox/` 里 Grok 的调研结果作为输入。
- 读 `30_conventions/` 偏好与约束，`10_knowledge/` 相关历史结论。

## 写
- 把方案、任务拆解写进 `20_projects/<项目>` 的 MOC：
  - 填"关键决策""任务看板"，明确每个任务的负责 Agent。
  - 给 Devin 留下足够明确的执行交接物（输入清晰、验收标准清晰）。
- 用 `_templates/project.md` 模板。

## 接入方式
- clone 本仓库读，或把相关 `20_projects/` / `30_conventions/` 内容贴进对话上下文。
- 网页端使用时：手动复制方案回写到 `20_projects/`（或让 Devin 代为落库）。

## 桌面版 / GUI 用法 (打开项目 + 自动读 + 深读 vault)

> 原生 Codex 桌面版：用「打开文件夹」而非 cd 来给项目路径。

1. **打开项目**：选「打开文件夹 / Open project」→ 选**最外层 repo 文件夹**，如 `/Users/a77/finhot`（别选 home `/Users/a77`，也别选里层 `finhot/finhot`）。其它：`/Users/a77/finance-workspace-private`、`/Users/a77/knowledge-base-private`、`/Users/a77/finance-research-site`。
2. **自动读**：只要工作区是该 repo，**每开新对话都会自动加载根目录 `AGENTS.md`**（核心偏好已内联，必中）。无需手动喂。
3. **深读完整 vault**：本机运行时 repo 内 `.agent-memory` 软链可用 → 让它读 `.agent-memory/30_conventions/preferences.md`、`.agent-memory/20_projects/<repo>.md`（首次可能要批准一次目录外读取）。
4. **本机 vs 云端自测**：让它「列出当前项目根目录的文件」——能看到 Mac 上真实文件＝本机（`.agent-memory` 可用）；要连接/clone GitHub＝云端（只能用 AGENTS.md 内联偏好，或用 PAT 现 clone `agent-memory`，同 Devin）。

> Codex 没有 SessionStart hook（不像 Claude 能动态注入最新看板），只读 AGENTS.md 文字；要最新项目笔记就显式让它读 `.agent-memory/20_projects/<repo>.md`。

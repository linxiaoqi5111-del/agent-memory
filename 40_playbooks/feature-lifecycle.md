---
title: 需求全流程协作 (调研→规划→执行→沉淀)
type: playbook
agent: devin
source: 设计约定
date: 2026-06-28
tags: [playbook, workflow, core]
status: verified
---

# 需求全流程协作

最常用的多 Agent 协作链：一个新需求从调研到落地的标准流程。

## 适用场景
有一个新需求/功能/问题，需要跨调研、设计、开发多个环节。

## 角色分工
| 步骤 | 负责 Agent | 输入（交接物） | 输出（交接物） |
|---|---|---|---|
| 1. 调研 | grok | 需求一句话描述 | `00_inbox/` 调研笔记（含来源链接） |
| 2. 规划 | codex | 调研笔记 + `30_conventions/` 偏好 | `20_projects/<项目>` 方案 + 任务看板 |
| 3. 执行 | devin | 项目方案 + 任务看板 | 代码 / PR + 更新看板 |
| 4. 沉淀 | devin/claude | 执行结果 | `10_knowledge/` 提炼条目 |

## 交接物格式约定
- **调研笔记**：用 `inbox-item.md` 模板，每条结论带 source URL。
- **项目方案**：用 `project.md` 模板，任务看板里每行指定负责 Agent + 验收标准。
- **执行回写**：在项目 MOC 的"交接记录"追加一行 `YYYY-MM-DD · devin · 做了…`，PR 链接放看板备注。

## 失败/回退处理
- 执行阶段发现方案不可行 → Devin 在看板标 `blocked` 并写明原因，回退给 Codex 重规划。
- 调研信息过时/无出处 → 不进入规划，打回 Grok 补来源。

---
title: 接入约定卡总览
type: agent-card
agent: devin
source: 设计约定
date: 2026-06-28
tags: [agent-card, index]
---

# 接入约定卡

每个 Agent 一张卡，说明它在协作中的**角色**和**如何读写本库**。

用法：把对应卡片的内容贴进各工具的 **system prompt / 自定义指令 / 项目说明**，让它知道这个记忆底座的存在和规则。

| Agent | 角色 | 卡片 |
|---|---|---|
| Devin | 开发执行 + 回写沉淀 | [[devin]] |
| Codex | 系统性规划 (Planner) | [[codex]] |
| Grok | 搜索 / 信息采集 | [[grok]] |
| Claude | 通用读写 (备用) | [[claude]] |

## 所有 Agent 的通用规则

1. 动手前先读 `30_conventions/`（规范、偏好、术语）。
2. 写入必须带完整 frontmatter（见 [[frontmatter-spec]]），用 `_templates/` 模板。
3. 原始产出进 `00_inbox/`，提炼后的结论进 `10_knowledge/`。
4. 项目相关写进对应 `20_projects/<项目>` 的 MOC，并更新任务看板。
5. 每次写入标明 `agent` 和 `source`，可追溯。

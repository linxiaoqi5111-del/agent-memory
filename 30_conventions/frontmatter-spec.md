---
title: Frontmatter 规范
type: convention
agent: devin
source: 设计约定
date: 2026-06-28
tags: [convention, spec, core]
---

# Frontmatter 规范

每个笔记**必须**以 YAML frontmatter 开头。这是不同 Agent 能互相消费内容的前提。

## 通用字段（所有笔记都要有）

| 字段 | 必填 | 说明 | 示例 |
|---|---|---|---|
| `title` | ✅ | 人类可读标题 | `finhot 数据回填流程` |
| `type` | ✅ | 笔记类型，见下表 | `knowledge` |
| `agent` | ✅ | 创建/最后更新者 | `devin` / `codex` / `grok` / `claude` / `human` |
| `source` | ✅ | 信息来源（URL / 工具 / 对话 / 推断） | `https://...` / `grok-search` |
| `date` | ✅ | 创建或更新日期 (YYYY-MM-DD) | `2026-06-28` |
| `tags` | ✅ | 标签数组，便于检索 | `[finhot, data, pipeline]` |
| `status` | ⬜ | `draft` / `verified` / `deprecated` | `verified` |
| `related` | ⬜ | 双链到相关笔记 | `["[[finhot-overview]]"]` |

## `type` 取值

| type | 放在哪 | 含义 |
|---|---|---|
| `inbox` | `00_inbox/` | 原始产出，未整理 |
| `knowledge` | `10_knowledge/` | 已提炼的事实/结论 |
| `project` | `20_projects/` | 项目 MOC / 任务状态 |
| `convention` | `30_conventions/` | 跨 Agent 约定 |
| `playbook` | `40_playbooks/` | 可复用工作流 |
| `agent-card` | `50_agents/` | Agent 接入约定卡 |

## 校验要点

- 日期统一 `YYYY-MM-DD`。
- `agent` 用小写固定值，方便聚合"谁写了什么"。
- `verified` 状态表示有人/某 Agent 核实过，可被下游放心引用；`draft` 表示待核实。
- 引用其他笔记用 Obsidian 双链 `[[文件名]]`，不要用裸文件路径。

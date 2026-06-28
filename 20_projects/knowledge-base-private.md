---
title: 知识库 (knowledge-base-private)
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/knowledge-base-private (AGENTS/CLAUDE)
date: 2026-06-28
tags: [project, 知识库, wiki, rag, knowledge-graph, python]
status: active
related: ["[[finance-workspace-private]]", "[[finance-research-site]]"]
---

# 知识库 — 项目 MOC

## 概述
- **是什么**：**LLM 维护的个人知识库 / Wiki**。人类策划来源，LLM 负责写作、交叉引用与维护。底层是金融主题的实体/概念/关系知识图谱（Theme Radar）。
- **仓库**：`linxiaoqi5111-del/knowledge-base-private`（private，Python，分支 `main`）

## 目录导览
- `wiki/` — `entities/`(公司/人物)、`concepts/`(概念/框架)、`sources/`(来源摘要)、`synthesis/`(跨源综合)、`relations/`(Theme Radar 底层大 JSON)
- `scripts/` — `ingest.py`(统一入口: pdf/entity-delta/concept/baseline/check)、`query_relations.py`(关系查询，替代直接 cat 大 JSON)、`rag_index.py`(RAG 检索)
- `skills/` + `skills/lib/`(共享库 knowledge_graph.py / repo_paths.py / obs_log.py)
- `raw/` — 不可变原文（禁止修改）；`docs/` — 参考文档；`dashboard/` `eval/`

## 强制规则（来自 AGENTS.md）
- **禁止直接 `cat` 大文件进 context**：`relations/` 下 4~13MB 的 JSON（entity_exposures / evidence_index / report_contexts / concept_graph）。查关系数据走脚本：
  ```bash
  python3 scripts/query_relations.py exposures --theme "液冷" --top 20
  python3 scripts/query_relations.py graph --concept "液冷服务器"
  ```
- **Git 分支安全**：大任务（PDF ingest、baseline、批量改 entities/relations、索引重建）必须新建分支；分支命名 `pdf-ingest/<名>`、`baseline/<名>` 等；合并等用户确认。
- 详细规范按需读：`docs/conventions.md`、`docs/operations.md`、`skills/<name>/SKILL.md`、`skills/lib/INGEST_FIELD_STANDARDS.md`。

## 关联
- ingest 类 skill 由 [[finance-workspace-private]] 迁入（2026-06-12）。
- 错误教训统一沉淀到 `finance-workspace-private/.claude/lessons_learned.md`，本库用 `[kb]` 前缀。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
|  |  |  |  |

## 交接记录
- 2026-06-28 · devin · 初次建档（基于 AGENTS/CLAUDE）

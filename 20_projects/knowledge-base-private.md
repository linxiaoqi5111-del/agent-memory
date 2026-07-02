---
title: 知识库 (knowledge-base-private)
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/knowledge-base-private (AGENTS/CLAUDE)
date: 2026-06-28
tags: [project, 知识库, wiki, rag, knowledge-graph, python]
status: active
related: ["[[finance-workspace-private]]", "[[finance-research-site]]", "[[finance-agent-capability-graph]]"]
---

# 知识库 — 项目 MOC（Map of Content，内容地图/目录页）

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
- 2026-06-29 · codex · 将多 Agent 共享记忆底座整理为系统设计文档，沉淀到 [[multi-agent-memory-system-design]]，覆盖架构图、权衡、容量估算与面试讲法。
- 2026-06-29 · codex · 打通金融 repo -> 知识库 repo 的 v1 闭环：金融侧生成 `kb_ingest_queue` JSON 任务包；知识库侧 `scripts/kb_ingest_queue.py` 负责 validate/preview/receive，归档到 `wiki/raw/cross-repo-ingest-queue/`，默认人工复核、禁止自动写 wiki。
- 2026-07-02 · codex · 新增跨仓金融 Agent 能力图谱 [[finance-agent-capability-graph]]，记录知识库作为事实层、图谱层、RAG 层与 Theme Radar 底座如何被金融 repo 的 ask/daily/forecast_preflight/l3-ingest 消费；后续新增稳定 ingest skill、relations 数据源、RAG 索引或跨仓任务队列时，应同步更新该图。
- 2026-07-02 · devin · draft PoC PR #50/51/52 处置完成（用户确认方案）：#50（事实 status 生命周期 + predicate 语义分层 + 证伪回链 overlay 派生层）与 main 的 generate_one/shared 批量重构冲突，把 status/predicate/overlay 渲染**移植进新架构**后合入 main（--include-invalidated 开关、✗ 曲线标记、🔴已证伪/⚠待定性 证据标签、脚注提示均保留）；#51/#52 是 stale 派生数据演示，未直接合——在最新 main 上重跑 `backfill_fact_predicate.py --theme 光模块 --write`（CONFIRMED 3/TECH 2/INTENT 4/DELIVERY 1/RUMOR 1/未判定 18）与 `link_invalidations.py --write --write-overlay`（15 条回链：风华高科 hard×2 等）重算落库后关闭。设计要点：证伪判决走 overlay 派生意见层（invalidation_links.json），不污染 evidence_index ground-truth，判决可随时重算——"stale 派生数据不合并、用脚本重算"正是该架构的用途。integrity 0 错误。
- 2026-07-02 · devin · kb-ingest-queue v2 状态回执（PR #192 待合并）：任务生命周期 pending→received→ingested/skipped；`receive` 归档时自动置 received 并生成日期目录 `receipt.json`（含 summary 状态计数 + 各队列任务状态），人工入库后 `mark <归档.json> --status ingested --note "wiki/log.md #N"` 回写状态并刷新回执，事件追加 `status_log.jsonl` 审计；`receipt <date_dir>` 可给旧归档补建回执。金融仓 PR #117 是消费端（kb-queue-status + 出队列去重）。validate 红线不变（pending/auto_apply=false/requires_human_review=true），mark 只改归档副本不动 raw 原文。
- 2026-07-02 · devin · 年报 baseline 批量入库 20 家（天/腾字头，PR #193 待用户 review，不合并）：走 company-baseline-ingest 结构化路径（annual-report --mode baseline → entity_baseline_writer），13 新建 + 7 合并实体页，relations 四件套同步，log #2178。关键教训：①writer 子串校验要求 main_business/products 为 raw 源文**连续子串**，须从 raw 提直引不能综述改写；②披露日不可考（报告期年末 2025-12-31）按 #2163 规约回退批次日期并记 date_note；③批量 sed/glob 修 frontmatter 时务必先限定到本批文件，本次两度误伤旧批次（源文改名波及 内蒙新华/宁波银行、log 前缀 sed 波及 166 篇旧 source note），均用 git diff 定位后精确还原。
- 2026-07-02 · devin · 晚间卖方研报20260702 完整晚间流程入库（PR #194 待用户确认，不合并）：concept-delta×14、卖方观点交叉（65主题/91实体，17观点 gate PASS：🟢12/🟡2/🔴3）、催化日历+9事件、提及频率、dashboard 重建、log #2179、qa_ingest PASS。要点：①log id 冲突——next_log_id 扫 refs 前须先 `git fetch`，否则未拉取的并行分支占用的 #NNN 看不见（本次 #2178 被年报 baseline 分支占用，让位改 #2179）；②index.md 发现两处历史遗留 diff3 合并标记（`|||||||`）顺手清理；③按用户指示改 daily-ops skill：第8步向量化发布改为可选——**单次 ingest 不做 RAG**，跑完 7.5 质检即算收尾，仅明确要求发索引时才在建索引机执行。
- 2026-07-02 · devin · 年报 baseline 第二批入库 20 家（天/田/铁字头，追加到 PR #193，不合并）：11 新建 + 9 合并实体页，log #2180，qa_ingest 20/20 PASS，integrity 0 错误，PIT 0 缺。要点：①log id 再次撞号——#2179 已被晚间卖方研报分支占用，`git fetch` 后 grep 全部远端分支 wiki/log.md 确认后改用 #2180（教训与 #2178 撞号同源：next_log_id 必须先 fetch 扫全部 refs）；②硬事实修正：田中精机股票代码 603919→300461（以年报官方口径为准，entity + relations 同步替换并记 log）；③天有为披露日按董事会审议年度利润分配日 2026-04-22 认定，其余 19 家回退批次日并记 date_note；④本批直接用修复后的 writer（已有 baseline 页仍追加 relations trace，降级保护收敛在 knowledge_graph 库层），未再出现图谱断链。

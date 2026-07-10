---
title: 知识库 (knowledge-base-private)
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/knowledge-base-private (AGENTS/CLAUDE)
date: 2026-06-28
tags: [project, 知识库, wiki, rag, knowledge-graph, python]
status: active
related: ["[[finance-workspace-private]]", "[[finance-research-site]]", "[[finance-agent-capability-graph]]", "[[demand-first-theme-vertical-slice]]"]
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
| Top-N 主题纵切片 planner | devin | done | PR #256（堆叠 #255），见 [[demand-first-theme-vertical-slice]] |
| F10 missing-exposure 终态路由 | devin | done | PR #255（堆叠 #254） |

## 交接记录
- 2026-07-10 · devin · P2 主题纵切片 planner 已落地（PR #256，堆叠 #255）：先用真实 eval、近期/历史提及、Theme Radar 来源和公司覆盖选 Top N，再用 concept page、parent、产业链、exposure、L1、source、wikilink、eval 十道 gate 路由为 `ready/build`；无法解析到 canonical concept 的信号只进 ontology `review`，必须确认 exact/alias、parent、node type、source 后才能 create/alias/reject，禁止自动建页或强造关系。产物同时提供 JSON 机器合同与 Markdown 执行视图。**关键决策**：重要度与完成度分离，避免“缺得越多优先级越高”反向奖励冷门空页；Graph RAG 前先完成高价值节点的证据闭环，而非平均清理全库。方法论见 [[demand-first-theme-vertical-slice]]。
- 2026-07-10 · devin · F10 baseline `missing exposures` 改为可审计终态合同（PR #255，堆叠 #254）：候选经 canonical exact/alias 匹配后写 `apply`，有 F10 支撑但缺 canonical concept 的进入 `review`，无可验证候选的写 `no_exposure`；后两者保留 company baseline 但不写 relations，避免为了通过门禁强造弱关系。每个终态记录 reason/source/raw/decision time，历史失败可复用 raw 重跑。该放宽只适用于 a-stock，年报完整入库闸门不变。**可复用原则**：验证门禁应区分“输入无效”与“合法的空关系结果”；空关系是业务终态，不应等同于整条记录失败。
- 2026-07-09 · devin · a-stock baseline 全量放量收官（批次明细见 wiki/log.md #2417–#2437，PR #226–#247）：队列 2032 家全部处理完毕。**可复用经验**：①runner fetch 阶段改 ThreadPoolExecutor 8 并发（每家独立 raw json 互不冲突），build/写库保持串行——「并行抓取+串行写入」生产者-消费者模式，批耗时 18min→4min；写入端共享 relations 大 JSON 决定了多 agent/多会话并行不可行，提速应在 IO 阶段做。②`scan_entity_baseline_queue.py` 会整队列重置为 pending（覆盖已处理状态）——batch 进行中禁止重跑 scan，误跑后用 `git checkout --` 恢复；③批次 PR 叠链（每批 base 指向前一批分支）+ 固定 finalize 脚本（log 追加/staged 白名单/红线检查/REST 建 PR）适合长滚动批量任务。
- 2026-07-03 · devin · missing-concept 回补收尾（PR #201 待合并，wiki/log.md #2185）：承接 #200 剩余 33 个缺概念引用，三桶裁决清零——①删污染 key 21（报告标题/股票代码/泛产业链层级词/实体名当概念/脏元数据）；②别名重写 10 到已有概念页（LPU→LPU推理芯片、液冷板→冷板式液冷 等）；③真缺页新建 3（Pogo Pin/3D玻璃/离型膜，均引用库内已有 source note，未引入新材料）。收尾 integrity 0 错误/0 告警。**可复用教训**：①泛层级词（材料/设备/耗材）当 concept key 属污染——该信息已由 chain_layer 字段承载，删边只损失噪音（与排除词并集同理：噪音清理类操作风险不对称）；②别名重写/删除工具可用 audit JSON 格式自造输入复用（repair_missing_concept_aliases/remove_polluted_concept_refs 均吃 audit 结构，手工裁决结果包装成 audit 行即可走标准管线）；③该仓无 CI，质量闸门=本地 check_relations_integrity + pytest 56 例 + pre-commit。
- 2026-06-28 · devin · 初次建档（基于 AGENTS/CLAUDE）
- 2026-06-29 · codex · 将多 Agent 共享记忆底座整理为系统设计文档，沉淀到 [[multi-agent-memory-system-design]]，覆盖架构图、权衡、容量估算与面试讲法。
- 2026-06-29 · codex · 打通金融 repo -> 知识库 repo 的 v1 闭环：金融侧生成 `kb_ingest_queue` JSON 任务包；知识库侧 `scripts/kb_ingest_queue.py` 负责 validate/preview/receive，归档到 `wiki/raw/cross-repo-ingest-queue/`，默认人工复核、禁止自动写 wiki。
- 2026-07-03 · devin · 全仓审计（PR #200 待合并）：integrity 长期告警「entity_exposures 引用 81 个无概念页概念」中 30 个用现成 `audit_missing_concepts.py` + `repair_missing_concept_aliases.py --apply` 别名修复（81→33），别名合并致条数变化后须 `check_relations_integrity.py --repair-meta` 重建 meta；剩余 33 个是真缺概念页（3D玻璃/ABF膜/LPU 等）或脏 key（`300655`/`PDF`/`entity_stub`），需走 concept-ingest 或人工清洗，建议另开任务。顺手补了 AGENTS.md Skill Index 缺失的 planning-with-files/obsidian 两行。**可复用教训**：integrity 告警别只当噪音，先跑 audit 脚本分「可别名修复」vs「真缺页」两桶再动手。
- 2026-07-02 · codex · 新增跨仓金融 Agent 能力图谱 [[finance-agent-capability-graph]]，记录知识库作为事实层、图谱层、RAG 层与 Theme Radar 底座如何被金融 repo 的 ask/daily/forecast_preflight/l3-ingest 消费；后续新增稳定 ingest skill、relations 数据源、RAG 索引或跨仓任务队列时，应同步更新该图。
- 2026-07-02 · devin · draft PoC PR #50/51/52 处置完成（用户确认方案）：#50（事实 status 生命周期 + predicate 语义分层 + 证伪回链 overlay 派生层）与 main 的 generate_one/shared 批量重构冲突，把 status/predicate/overlay 渲染**移植进新架构**后合入 main（--include-invalidated 开关、✗ 曲线标记、🔴已证伪/⚠待定性 证据标签、脚注提示均保留）；#51/#52 是 stale 派生数据演示，未直接合——在最新 main 上重跑 `backfill_fact_predicate.py --theme 光模块 --write`（CONFIRMED 3/TECH 2/INTENT 4/DELIVERY 1/RUMOR 1/未判定 18）与 `link_invalidations.py --write --write-overlay`（15 条回链：风华高科 hard×2 等）重算落库后关闭。设计要点：证伪判决走 overlay 派生意见层（invalidation_links.json），不污染 evidence_index ground-truth，判决可随时重算——"stale 派生数据不合并、用脚本重算"正是该架构的用途。integrity 0 错误。
- 2026-07-02 · devin · kb-ingest-queue v2 状态回执（PR #192 待合并）：任务生命周期 pending→received→ingested/skipped；`receive` 归档时自动置 received 并生成日期目录 `receipt.json`（含 summary 状态计数 + 各队列任务状态），人工入库后 `mark <归档.json> --status ingested --note "wiki/log.md #N"` 回写状态并刷新回执，事件追加 `status_log.jsonl` 审计；`receipt <date_dir>` 可给旧归档补建回执。金融仓 PR #117 是消费端（kb-queue-status + 出队列去重）。validate 红线不变（pending/auto_apply=false/requires_human_review=true），mark 只改归档副本不动 raw 原文。
- 2026-07-02 · devin · 年报 baseline 入库经验（批次明细见 wiki/log.md #2182，PR #193）：①writer 子串校验要求 main_business/products 为 raw 源文**连续子串**，须从 raw 提直引不能综述改写；②披露日不可考（报告期年末）按 #2163 规约回退批次日期并记 date_note；③批量 sed/glob 修 frontmatter 时务必先限定到本批文件，否则易误伤旧批次（用 git diff 定位后精确还原）。
- 2026-07-02 · devin · 晚间流程经验（批次明细见 wiki/log.md，PR #194）：①log id 冲突——next_log_id 扫 refs 前须先 `git fetch`，否则未拉取的并行分支占用的 #NNN 看不见；②历史遗留 diff3 合并标记（`|||||||`）见到顺手清理；③流程变更：daily-ops 第8步向量化发布改为可选——**单次 ingest 不做 RAG**，跑完 7.5 质检即算收尾，仅明确要求发索引时才在建索引机执行。
- 2026-07-02 · devin · 年报 baseline 第二批经验（批次明细见 wiki/log.md #2180，PR #193）：①log id 撞号再次验证：定号前必须 `git fetch` 后 grep 全部远端分支 wiki/log.md；②硬事实以年报官方口径为准（如股票代码勘误需 entity + relations 同步替换并记 log）；③披露日优先取董事会审议日，不可考则回退批次日并记 date_note；④writer 对已有 baseline 页仍追加 relations trace，降级保护收敛在 knowledge_graph 库层。
- 2026-07-02 · devin · PR #193 冲突收尾经验（不含 ingest 内容，批次明细见 wiki/log.md #2181）：①log.md 多分支合并用「theirs + 追加 ours 新增段」策略，并清理历史遗留 diff3 标记（`|||||||`/`=======` 会被 pre-commit check-merge-conflict 拦截）；②entity_exposures/concept_graph 不在 merge driver 覆盖范围（.gitattributes 只挂了 evidence_index/meta），需 3-way 语义并集脚本手工合并，建议后续把这两个文件也纳入 kb-relations-union；③log id 三度撞号，next_log_id 必须先 `git fetch` 扫全部远端分支再定号；④合并后跑 `check_relations_integrity.py --repair-meta` 重建条数统计；⑤writer Rule 6：已有 baseline 画像区不被年报覆盖，只追加 relations/证据，若要覆盖需人工决定。
- 2026-07-02 · devin · 台账统一落地（PR #196 待合并，配对金融仓 PR #122）：新增 `wiki/raw/briefings/`（晨汇当日原始材料归档 `YYYY-MM-DD/序号-来源摘要.md`）与 `wiki/raw/sellside/`（**所有卖方材料第一落点** `YYYY-MM-DD-<券商或摘要>.md` + `<date>.digest.json`），各带 README；morning-briefing SKILL Stage 1 加归档步、material-router SKILL 开头加「先落 sellside 再路由」；AGENTS.md 指向金融仓 `docs/learning/ledger-map.md` 台账地图。禁 PDF 本体，红线不变；opinion-events.jsonl 不搬家只登记。
- 2026-07-02 · devin · 年报 baseline 第四批经验（批次明细见 wiki/log.md #2183，PR #197）：①首次全程自动化闭环打通：Mac 端从 ~/IMA知识库下载 自主选批（跳过 ST 类）/压缩/隧道分块传输 → Linux 解析 → 披露日抽取 → manifest → writer → 闸门 → PR，无需用户手工压缩投喂；②披露日抽取脚本支持中文数字日期（二〇二六/二Ｏ二六等），优先级 内控披露日 > 审计报告日 > 批准报出日，本批 20/20 取到真实披露日；③writer 子串校验再次验证：main_business/products 必须是 raw 源文连续子串，综述改写会被 preflight 整批拒掉，正确做法是锚点定位后从源文切片直引；④知识库 repo 经用户 PAT 访问时 Devin 内置 git_create_pr 不可用（Not Found），走 GitHub REST API 建 PR，注意 502 后先查 head 分支是否已建成功再重试，避免重复建 PR。

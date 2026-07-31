---
title: 金融 Agent 大模型面试学习
type: project
agent: devin
source: "https://app.devin.ai/sessions/deebe5e092fe49579a9983ee14ca02d3"
date: 2026-07-14
tags: [project, learning, interview, finance-agent, handoff]
status: active
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]", "[[金融Agent面试-循序渐进教学计划]]", "[[finance-workspace-private]]", "[[knowledge-base-private]]"]
---

# 金融 Agent 学习与项目跨账号交接

> 生成日期：2026-07-14
> 用途：作为 Agent Memory 中的学习入口，让任意有仓库访问权的新 Agent 继续当前进度。
> 注意：本文不含密钥或临时环境信息。

## 1. 新 Session 可直接使用的启动提示词

新 Agent clone `linxiaoqi5111-del/agent-memory` 后，先打开本文，再使用以下提示词：

```text
请读取 agent-memory 仓库中的三份文件：

1. 20_projects/金融Agent面试学习.md
2. 70_tutor/大模型面试-金融Agent项目第一性原理复习手册-V3.md
3. 70_tutor/金融Agent面试-循序渐进教学计划.md

继续我的金融 Agent 大模型面试学习。严格以 V3 手册为教材，按照：

项目场景 → 第一性原理 → 当前真实实现 → 替代方案与 trade-off
→ 不能夸大的边界 → 面试题评分

中文教学；英文术语首次出现时解释中文；一次只问一道题；我的回答要评分并直接纠错。

不要重新从 SQL 或通用会计题开始。当前进度是：
- V3 第 18 章 Knowledge Base RAG：已完成；
- 第 19 章 Closed-loop Retrieval：只学了概览，用户明确认为过于粗略，必须从 19.1 开始重新精讲；
- 第 20 章 DuckDB 与结构化市场数据：学过 SQL/DuckDB 基础和 D0–D9 概览，尚未达到完整面试掌握；
- 第 21 章 Output Review：只学到定向修订和 reviewer 边界，暂时暂停。

请先重新教授第 19 章 Closed-loop Retrieval，不要直接跳到第 20 或第 21 章。要求像第 18 章一样逐节深入：

1. 从一次 top-k 的确认偏误推导为什么需要 closed loop；
2. 逐步画出 entity anchor → narrow → broad → counter 的真实数据流；
3. 解释每类 query candidate 怎样生成、前一步如何影响后一步；
4. 解释 RetrievalAttempt、BucketedHit、ClosedLoopRetrievalResult；
5. 解释三次空尝试、状态、去重、分桶、freshness gate 和 warning；
6. 映射到 `closed_loop_retrieval.py` 与 `ask.py`；
7. 讲异常降级、延迟代价、评测指标、当前边界；
8. 完成 30 秒、2 分钟和连续追问验收后，才能标记第 19 章完成。
```

## 2. 学习偏好

- 使用中文。
- 采用“项目实战与面试题结合”。
- 不只背答案，要解释第一性原理、输入输出、数据流、异常降级和评测。
- 第一次出现英文术语时补充中文解释。
- 一次只问一道题。
- 每题评分；概念错误要直接指出，不要顺着错误答案。
- 每章给出 30 秒面试表达，并说明不能夸大的实现边界。
- 当前几乎没有独立 Python 编码经验，只能看懂少量代码。
- 现阶段先完成 V3 原教材，再决定是否系统补 Python。

## 3. 当前学习进度

### 3.1 已完成：Knowledge Base RAG

已掌握：

```text
Markdown/YAML Page
→ section-aware chunking
→ BGE-m3 dense retrieval
+
独立 rank_bm25 lexical retrieval
→ Chunk 级 RRF
→ exact entity/code/wikilink boost
→ 按 page_id 聚合
→ Page 级 one-hop neighbor expansion
→ optional cross-encoder rerank
→ PageHit
```

关键口径：

- BGE-m3 当前只负责 dense；lexical 路径是独立 BM25。
- Dense 与 BM25 默认各召回约 80 个 Chunk。
- RRF 在 Chunk 级融合。
- 同页最高分 Chunk 成为 `best_chunk_id`。
- one-hop 在 Page 级扩邻居。
- rerank 对前约 50 个 Page 候选重排，输入是 query + Page title + best Chunk。
- Finance 默认最终返回约 6 个 PageHit。
- 生成式 LLM 读取受预算控制的 `llm_evidence`，不是整页全文。
- `fresh` 才能进入正式路径；`stale/unknown` fail-closed。

### 3.2 已完成：RAG 证据上下文改造

两个 PR 已 squash merge：

- Knowledge Base PR #281
  https://github.com/linxiaoqi5111-del/knowledge-base-private/pull/281
- Finance PR #224
  https://github.com/linxiaoqi5111-del/finance-workspace-private/pull/224

合并提交：

- Knowledge Base：`47a99336b2e754d78bccab98bd43dfdc63a001b1`
- Finance：`f486be676c30a674b58d77795e3843af83a3b314`

改造内容：

- 双层文本：短 `display_excerpt` 与长 `llm_evidence`；
- query-centered window（查询命中词居中窗口）；
- 同 Page 有限相邻 Chunk；
- direct/neighbor、query type、source/evidence layer 动态预算；
- 全局证据预算；
- evidence chunk IDs、hash、revision、freshness provenance；
- claim coverage、citation fidelity、truncation、成本、延迟评测；
- stale/unknown 仍不能进入正式 LLM prompt。

测试结果：

- Knowledge Base：240 passed，8 skipped，3 subtests passed；
- Finance：1469 passed，3 skipped，7 subtests passed；
- 两仓 pre-commit 和 CI 通过。

### 3.3 需重新精讲：Closed-loop Retrieval

本章此前只通过概览和选择题快速带过。用户明确反馈：教学深度明显低于第 18 章，不能标记为已完成。

三个检索孔径：

- `narrow`：主体、公司、代码、订单等直接证据；
- `broad`：上下游、同业、宏观需求、替代表达；
- `counter`：风险、证伪、不及预期、竞争替代。

第一性原理：

```text
提出假设
→ 找直接证据
→ 扩展相关变量
→ 主动寻找反证
→ 决定结论强度
```

结果分桶：

- `conclusion`：硬度或主体绑定足以支持结论；
- `clues`：相关但不足以直接支持结论；
- `counter_clues`：反方线索；
- `discarded`：无有效分数或不足以使用。

每次 attempt 记录：

- aperture；
- query；
- status；
- hit_count。

最多三次空尝试，在召回和延迟间折中。

已理解：

> “本轮未检索到反证”不等于“没有风险”。

仍需系统掌握：

- 为什么一次 top-k 会放大原始问题中的确认偏误；
- entity anchor 如何生成 narrow candidate；
- narrow hit 中的高信息词如何进入 broad context；
- counter query 如何围绕主体和相关词主动证伪；
- `RetrievalAttempt`、`BucketedHit`、`ClosedLoopRetrievalResult` 的字段与职责；
- `MAX_EMPTY_ATTEMPTS = 3` 的控制流与召回/延迟权衡；
- conclusion/clue/counter/discarded 的精确分桶条件；
- aperture/path/chunk 去重；
- freshness gate、timeout、stale、空命中的不同状态；
- `ask.py` 如何消费 closed-loop result；
- aperture 级评测、延迟和当前启发式边界；
- 30 秒、2 分钟和连续追问表达。

### 3.4 已初步学习：DuckDB 与结构化事实

已掌握：

- SQL 是结构化查询语言，不是模型或数据库。
- DuckDB 是嵌入式列式 OLAP 数据库，适合本地分析、聚合、排名和回测。
- SQLite 更偏本地小型事务存储。
- PostgreSQL 更适合多用户在线事务和并发写入。
- 推荐 PostgreSQL 做 OLTP 真源、DuckDB 做 OLAP 分析层。
- 数值事实用 D；语义材料用 W；官方核验用 L3。
- 数字 claim 优先绑定 D，并保留表、日期、字段和口径。
- W 中的二手数字与 D 冲突时要披露，并升级到 L3 官方材料核验。

SQL 已学：

- `WHERE`、`GROUP BY`、`AVG`、`ORDER BY`；
- `COUNT(DISTINCT trade_date)` 与完整 20 交易日；
- `NULL` 与真实 `0`；
- 主键/外键；
- `INNER JOIN` 与 `LEFT JOIN`；
- `RANK()`；
- `PARTITION BY`；
- 窗口函数与 `GROUP BY` 的区别；
- `ROWS BETWEEN 19 PRECEDING AND CURRENT ROW`。

D0–D9 已学：

- 并非每个问题都运行全部数据块；
- 无依赖 block 可由 planner-worker 并行；
- D3 依赖前序汇总的 `evidence_text`，必须在 barrier 后串行；
- block 状态必须区分：
  - `not attempted`；
  - `empty`；
  - `error`；
  - `ok`。

### 3.5 已开始但暂缓：Output Review

已掌握：

- 检索正确不等于生成正确。
- 确定性检查顺序：

```text
新鲜度
→ 证据分层
→ 反证
→ 数据缺口
→ 可验证假设
→ 弱证据硬写
```

- 不能只让生成答案的同一 LLM 做唯一 reviewer，因为会共享盲点。
- 正确修订链：

```text
初始 answer
→ reviewer 指出具体 violation
→ LLM 定向修订
→ AnswerSpec 校验
→ 合格后采用
```

- 当前 `blocking=False`，是 advisory gate，不是生产级硬阻断安全门。

恢复第 21 章时的下一题：

> 一份回答的来源、分层、反证和缺口都合规，但股票后来下跌。能否据此判定 Output Review 失败？

正确方向：

> 不能。Output Review 审核证据和表达是否合规，不保证预测正确；预测结果由历史 outcome、checkpoint 和 verdict 评估。

## 4. 后续顺序

继续遵循教学计划：

1. 从 19.1 开始完整重学第 19 章 Closed-loop Retrieval；
2. 回看第 20 章实现、异常、评测和面试表达，补足到 L5；
3. 完成第 21 章 Output Review；
4. 第 22 章 Agent Memory；
5. 第 23 章 PIT 与防前视；
6. 第 24 章可观测性与回放；
7. 第 25 章 L3、Research Judge、Research Queue；
8. 第 26 章编排与风险门控；
9. 第 27 章评测与学习闭环；
10. 第 28 章真实问题全链路；
11. 第 29–35 章选型、项目追问、实现边界和模拟面试；
12. 最后补 Transformer、训练、推理和 Serving 等 P1 理论。

## 5. 项目真实边界

面试中不能夸大：

- 这是个人金融研究 Agent 工作台，不是完全自主的生产级多 Agent 系统。
- 当前核心是规则编排 + LLM 精修，不是 LLM 完全自由规划。
- Knowledge Base RAG 仍有 POC 属性。
- BGE-m3 learned sparse 没有接入主链。
- counter retrieval 不能保证找到最强反证。
- Output Review 当前是 advisory，不是硬安全门。
- DuckDB 不是实时交易或 tick 级基础设施。
- 不能用股价表现证明订单已兑现为收入。
- Wiki 命中不能自动升级为 L3。
- “没查到”不能写成“不存在”。

## 6. 跨账号操作清单

新账号通常不会继承当前账号的：

- 私有 Session 访问权；
- 当前 VM；
- 未提交文件和运行进程；
- GitHub 私有仓库集成；
- 组织级 secrets、Knowledge 或环境配置。

因此建议：

1. 为新账号授予 `linxiaoqi5111-del/agent-memory` 的只读或写入权限；
2. 新 Session clone 本仓库并打开 `20_projects/金融Agent面试学习.md`；
3. 若要继续代码工作，再授予两个 GitHub 私有业务仓库的访问权限；
4. 新 Session 基于最新 `main` clone，不要依赖旧 VM；
5. 不要复制 `.env`、token、askpass 或任何密钥；
6. 使用第 1 节提示词启动；
7. 若两个账号属于同一 Devin 组织且新账号有 Session 权限，可以附当前 Session URL；如果不在同一组织，不要假定 `@Sessions` 能读取本 Session。

当前 Session：

https://app.devin.ai/sessions/deebe5e092fe49579a9983ee14ca02d3

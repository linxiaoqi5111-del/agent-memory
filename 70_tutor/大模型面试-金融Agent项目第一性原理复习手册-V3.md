---
title: 大模型面试：金融 Agent 项目第一性原理复习手册（V3）
type: tutor-note
agent: devin
source: "Devin Session deebe5e092fe49579a9983ee14ca02d3；三个项目仓库与《大模型面试题与答案.pdf》"
date: 2026-07-14
tags: [llm, interview, finance-agent, rag, agent, handbook]
status: draft
related: ["[[金融Agent面试-循序渐进教学计划]]", "[[金融Agent面试学习]]"]
reviewed_by: human
reviewed_at: 2026-07-14
---

# 大模型面试：结合你的金融 Agent 项目的第一性原理复习手册（V3：金融 Agent 实现详解版）

> 资料来源：已只读分析 `linxiaoqi5111-del/agent-memory`、`finance-workspace-private`、`knowledge-base-private`，并审计附件《大模型面试题与答案.pdf》。
> 目标：不要背 PDF，而是用“第一性原理 → 标准答案 → 你的项目怎么讲 → 不能夸大的边界”准备大厂面试。
> V2 新增：Transformer、训练对齐、PEFT、显存与分布式、推理与量化、Serving 详解，以及口头自测与白板题。
> V3 新增：金融 Agent 从业务问题、技术选型、架构设计到真实代码落地的完整链路；逐项说明输入输出、数据流、失败降级、评测、当前边界，以及 30 秒 / 2 分钟面试表达。

---

## 0. 面试总故事：你的项目到底是什么

一句话版本：

> 我做的是一个面向 A 股题材研究的个人金融 Agent 工作台。它不是只会聊天的 LLM 包装，而是把盘面数据、知识库、关系图谱、RAG 检索、用户记忆、证据分层、反证审稿和可回放评测组合起来，让模型在有来源、有边界、有降级策略的前提下辅助研究。

架构版本：

```text
agent-memory
  Git + Markdown + YAML frontmatter + Obsidian
  -> 记录用户偏好、项目交接、方法论、Agent 协作规则

knowledge-base-private
  raw 原文 / wiki 知识页 / relations 结构化图谱 / .rag_index 派生检索索引
  -> 负责事实、证据、图谱、RAG 候选页

finance-workspace-private
  DuckDB 市场特征库 + Agent 服务 + Workbench + eval
  -> 负责盘面数据、问题路由、检索编排、回答生成、质检、回放
```

面试时要突出四个工程思想：

1. **LLM 不是事实源**：事实来自 DuckDB、wiki、relations、原文证据；LLM 主要做理解、组织、解释和表达。
2. **RAG 不只是“向量库 + prompt”**：还包括 chunking、BM25、dense embedding、RRF 融合、rerank、图谱扩展、新鲜度门禁、评测。
3. **金融 Agent 必须防幻觉和防前视**：区分事实、推演、预测；历史回测只能用当时可得信息。
4. **记忆要分层**：事实记忆、经验记忆、方法论记忆不能混在一起，否则 RAG 会把旧判断当新事实。

---

## 1. PDF 审计结论：哪些能背，哪些必须更新

附件覆盖很广，但整体更像 2023 年资料，不适合原样背。

### 主要问题

- **重复**：RAG 整章重复两次；Transformer、LoRA、优化器、训练显存等跨章节重复。
- **过时**：模型家族还停在 ChatGLM、Falcon、PaLM、LLaMA 早期；上下文长度仍按 2k/4k 讲。
- **错误或不严谨**：
  - 多次写 `LLaMA-6B`，常见 LLaMA 版本应是 7B/13B/30B/65B 等。
  - “int8 一般比 fp16 慢”是早期 bitsandbytes 经验，2026 语境要结合 AWQ/GPTQ/FP8/INT4 kernel 讲。
  - LangChain 章节有伪 API，不要照抄。
  - “13B 指令精调达到 GPT-4 90%”这类说法没有定义指标，面试中不要引用。

### 优先级

P0：最适合绑定你的金融 Agent 讲
Agent、Memory、RAG、Hybrid 检索、rerank、评测、防幻觉、长上下文 vs RAG、系统设计。

P1：大厂基础高频
Transformer、Self-Attention、RoPE、RMSNorm、SwiGLU、MQA/GQA/MLA、FlashAttention、SFT/RLHF/DPO/GRPO、LoRA/QLoRA、KV cache、vLLM、分布式训练、Tokenizer。

P2：收益较低或陈旧
Prompt Tuning、Prefix Tuning、P-Tuning v1/v2、早期 LangChain API、老模型参数对比、泛泛的蒸馏/多模态章节。

---

## 2. P0 高频题标准答案

### 2.1 什么是 Agent？你的金融 Agent 为什么算 Agent？

#### 一句话结论

Agent 是以 LLM 为推理核心，能围绕目标进行规划、调用工具、使用记忆、根据反馈迭代的系统；它不是一次性文本生成器。

#### 第一性原理

普通 LLM 只有“输入文本 → 输出文本”。现实任务需要：

1. 确定用户意图；
2. 拆解子任务；
3. 选择数据源或工具；
4. 检索证据；
5. 执行或生成；
6. 检查结果；
7. 把经验写回长期记忆。

所以 Agent 的本质是：**LLM + 状态 + 工具 + 记忆 + 控制回路**。

#### 标准面试答案

Agent 通常由几部分组成：

- **Planner / Router**：理解任务并决定路径。
- **Tools**：搜索、数据库、代码执行、API、文件系统等外部能力。
- **Memory**：短期上下文和长期知识/经验。
- **Executor**：执行计划或调用工具。
- **Critic / Evaluator**：反思、验收、纠错。
- **State / Trace**：记录每一步，便于恢复和回放。

常见范式：

- ReAct：Reason + Act，把推理和行动交替进行。
- Reflexion：失败后把经验写入记忆，下次改进。
- LangGraph / workflow：把 Agent 流程显式建成状态图，提升可控性。

#### 结合你的项目

你的金融项目可以这样讲：

> 我的 Agent 没有完全交给 LLM 自由规划，而是采用“规则编排 + LLM 精修”的混合方式。问题先经过 `question_router` / `answer_orchestrator` 识别类型，再决定是否调用盘面数据、知识库 RAG、图谱关系、用户记忆、反证审稿等模块。事实由工具和数据源提供，LLM 主要负责把证据组织成可读回答。

可引用代码路径：

- `finance-workspace-private/intelligence/services/question_router.py`
- `finance-workspace-private/intelligence/workflows/agent_orchestrator.py`
- `finance-workspace-private/intelligence/services/answer_orchestrator.py`
- `finance-workspace-private/intelligence/services/ask.py`

#### 不能夸大的部分

- 不要说它是完全自主的多 Agent 生产系统。
- 更准确说法：个人金融研究 Agent 工作台，有路由、工具调用、记忆、质检和可回放机制，但核心仍是受控工作流。

---

### 2.2 RAG 是什么？为什么你的项目需要 RAG？

#### 一句话结论

RAG（Retrieval-Augmented Generation，检索增强生成）是在生成前先从外部知识库检索相关证据，让模型基于证据回答，从而降低幻觉、提升时效性和可追溯性。

#### 第一性原理

LLM 参数里存的是训练时压缩后的统计知识，有三个天然问题：

1. **过期**：训练后发生的新信息不知道。
2. **不可追溯**：不知道某句话依据哪份材料。
3. **容易编造**：模型会补全“看起来合理”的答案。

RAG 把“记住所有知识”改成“需要时检索证据”，本质是把知识从模型参数中外置出来。

#### 标准面试答案

RAG 典型流程：

1. 文档清洗与切块；
2. embedding 建索引；
3. 用户 query 改写或扩展；
4. 召回候选 chunk / page；
5. rerank 精排；
6. 拼 prompt，让 LLM 基于上下文生成；
7. 引用来源、评测忠实度和召回质量。

核心指标：

- 检索侧：Recall@k、MRR、nDCG、命中率、索引新鲜度。
- 生成侧：faithfulness、answer relevance、context relevance、引用覆盖率。
- 业务侧：回答是否能支持决策、是否暴露缺口、是否可复验。

#### 结合你的项目

你的知识库仓不是简单向量库：

```text
raw/ 原文
→ wiki/entities, concepts, sources, synthesis
→ wiki/relations 结构化关系
→ .rag_index 派生索引
→ finance-workspace 的 kb_rag.py 调用 rag_index.py query
```

项目亮点：

- RAG 索引不作为事实源，只是派生索引，可从 wiki 重建。
- 检索结果带 `content_hash`、`index_source_revision`、`index_freshness`。
- finance 仓调用知识库仓时走 subprocess，失败则降级，不让 RAG 故障拖垮整个 Agent。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/README.md`
- `knowledge-base-private/scripts/rag_index.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`

#### 不能夸大的部分

- 知识库 RAG README 明确写的是 POC。
- 本次未实测 BGE 索引效果；评测集也存在合成/未校准问题。
- 面试中应说：“工程链路已实现，正式效果还需要真实查询集和人工校准真值验证。”

---

### 2.3 Hybrid 检索是什么？BM25、向量、RRF 怎么融合？

#### 一句话结论

Hybrid 检索把关键词检索和语义向量检索结合起来：BM25 擅长精确词面，dense embedding 擅长同义语义，RRF 用排名融合避免分数不可比。

#### 第一性原理

检索的目标是“不要漏掉相关证据”。单一方法有系统性盲区：

- BM25：看到“液冷服务器”能精确命中，但用户问“数据中心散热新方向”可能漏。
- 向量检索：能理解同义语义，但股票代码、公司名、罕见术语、数字很容易不稳。

因此最好让误差不相关的召回器并联。

#### 标准面试答案

BM25：

- 基于词频 TF、逆文档频率 IDF、文档长度归一化；
- 适合精确匹配、专有名词、代码。

Dense retrieval：

- 把 query 和 chunk 编码成向量；
- 用 cosine / dot product 搜相似语义；
- 适合同义、改写、模糊问题。

RRF（Reciprocal Rank Fusion）：

```text
score(d) = Σ 1 / (k + rank_i(d))
```

优点：

- 不要求 BM25 和向量分数在同一尺度；
- 对异常分数鲁棒；
- 工业界常用作简单强基线。

#### 结合你的项目

知识库检索实现：

- dense：BGE-m3 输出 1024 维向量；
- BM25：`rank_bm25` + 轻量中文 tokenizer；
- 两路各取 top-80；
- 用 RRF 融合；
- 对股票代码、公司名、概念名、wikilink 精确命中加 boost；
- 沿 wikilink 做一跳邻居扩展；
- 可选 rerank。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/config.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`
- `knowledge-base-private/skills/lib/rag/tokenizer.py`

#### 不能夸大的部分

- 代码里 BGE-m3 的 sparse / lexical_weights 没有接入检索；BM25 是独立 `rank_bm25`，不要说“用了 BGE-m3 dense+sparse 双路”。
- Hybrid 有工程实现，但效果提升需要可信评测集证明。

---

### 2.4 rerank 是什么？bi-encoder 和 cross-encoder 有什么区别？

#### 一句话结论

bi-encoder 快，适合大规模召回；cross-encoder 慢但更准，适合对少量候选重排。

#### 第一性原理

召回阶段要从海量文档中找候选，必须快；精排阶段只面对几十个候选，可以用更贵模型精细判断。

bi-encoder：

```text
q -> vector
d -> vector
score = q · d
```

优点是文档向量可预计算；缺点是 query 和 document 没有深度交互。

cross-encoder：

```text
[query, document] -> model -> relevance score
```

优点是相关性判断更细；缺点是每个候选都要跑模型。

#### 标准面试答案

工业 RAG 常用两阶段：

1. BM25 / dense / hybrid 先召回 top-N；
2. cross-encoder reranker 对 top-N 重打分；
3. 取 top-k 拼上下文。

rerank 只能重排已有候选，不能把没召回的好文档捞回来，所以召回池要足够大。

#### 结合你的项目

你的知识库实现了：

- `mode=rerank`；
- 在 hybrid 候选之上取前 `RERANK_CANDIDATES=50`；
- 使用 `bge-reranker-v2-m3`；
- `AutoModelForSequenceClassification` 输出 logit，再 sigmoid 到 0~1；
- hash reranker 只用于离线冒烟，不用于正式结论。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/rerank.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`

#### 不能夸大的部分

- README 提醒 rerank 收益要用 eval A/B 量化后再决定是否默认开启。
- 面试时说“已实现 rerank 管线，是否默认上线取决于延迟、成本和真实评测收益”更稳。

---

### 2.5 文档怎么切块？为什么不能直接固定长度切？

#### 一句话结论

chunk 是 RAG 的最小检索和引用单元；切得太大噪声多，切得太小丢上下文。你的项目用 Markdown section + 标题/tags 面包屑 + overlap 做折中。

#### 第一性原理

检索找的是 chunk，不是完整文档。chunk 决定：

- 能否被召回；
- 召回后语义是否完整；
- 引用是否能追溯；
- prompt 是否被噪声塞满。

固定长度窗口可能把一个产业链逻辑切断，也可能把标题和正文拆开。

#### 标准面试答案

常见切块策略：

- 固定 token 窗口：简单，但易切断语义；
- 递归字符切分：按段落、句子逐级切；
- 结构化切分：按 Markdown 标题、HTML 标签、PDF section；
- 语义切分：用 embedding 相似度检测主题变化；
- overlap：保留边界信息，但会增加冗余。

#### 结合你的项目

知识库 RAG：

- 按 `##/###` section 切；
- 每块前面拼标题、tags、section 面包屑；
- 超过 `MAX_TOKENS=1024` 再按段落切到 `TARGET_TOKENS=768`；
- overlap 约 15%；
- chunk 带 `file_path/page_type/title/tags/section/wikilinks/content_hash`。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/chunking.py`
- `knowledge-base-private/skills/lib/rag/config.py`

---

### 2.6 如何保证 RAG 索引新鲜度？为什么这是防幻觉的一部分？

#### 一句话结论

过期索引会让模型引用“看似有来源但已经过时”的证据，所以 RAG 必须有 freshness gate，默认 fail-closed。

#### 第一性原理

RAG 幻觉不只来自模型，也来自检索系统：

- 文档更新了，索引没更新；
- raw 原文变了，chunk hash 没对齐；
- 用旧 index 回答新问题；
- 评测集和索引版本不一致。

这类错误最危险，因为回答有引用，看起来更可信。

#### 标准面试答案

索引新鲜度可以检查：

1. index build time 是否超过阈值；
2. 源文件 git revision 是否变化；
3. working tree 是否有未入索引改动；
4. chunk content_hash 是否一致；
5. index metadata 是否记录 include_raw、模型名、构建参数。

默认策略：

- fresh：允许作为证据；
- stale：拒绝或显式降级；
- unknown：保守处理，不当正式证据。

#### 结合你的项目

知识库做了：

- `content_hash` 增量更新；
- `manifest_revision` 记录参与索引的文件内容；
- `rag_freshness.py` 检查 git diff、working tree、age；
- `rag_index.py query` 默认 `stale-policy=fail`，过期直接拒绝作为证据；
- finance 仓 `kb_rag.retrieve(require_fresh=True)` 会丢弃 stale/unknown 命中。

可引用代码路径：

- `knowledge-base-private/scripts/rag_freshness.py`
- `knowledge-base-private/scripts/rag_index.py`
- `knowledge-base-private/skills/lib/rag/store.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`

---

### 2.7 怎么防止 LLM / RAG 幻觉？

#### 一句话结论

不要只靠 prompt 说“不要幻觉”。成熟系统要把事实来源、证据分层、反证、缺口、程序化检查、回放评测都做出来。

#### 第一性原理

幻觉来自三类问题：

1. **模型内在生成错误**：语言模型目标是预测下一个 token，不是保证事实真。
2. **检索错误**：召回错文档、旧文档、低质量文档。
3. **推理越权**：事实是真的，但结论或预测跳得太远。

防幻觉不是让模型“更听话”，而是限制它能把什么升级成事实或决策。

#### 标准面试答案

防幻觉方法：

- RAG 引入外部证据；
- 引用必须绑定 source / chunk；
- 事实、推理、预测分层；
- 反证检索；
- 没证据时拒答或降级；
- LLM-as-judge + 程序化 gate；
- claim-level verification；
- 离线评测与线上 trace。

#### 结合你的项目

你的项目有多层防线：

1. `ask.py` 要求事实行带 `[S#]/[G#]/[R#]/[W#]/[M#]` 引用；
2. `answer_quality.py` 做 prompt 层质检；
3. `output_review.py` 做程序化 gate：新鲜度、证据分层、反证、缺口、可验证假设、弱证据硬写；
4. `red_team.py` 找过去错误和反方；
5. `claim_fidelity.py` 做 claim-level 抽取与验证；
6. 知识库写入时区分 L1/L2/L3 证据和 fact_hardness。

可引用代码路径：

- `finance-workspace-private/intelligence/services/output_review.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`
- `finance-workspace-private/intelligence/services/red_team.py`
- `knowledge-base-private/skills/lib/knowledge_graph.py`

#### 不能夸大的部分

- `output_review.py` 文档明确说：当前是 advisory review，不是自动硬阻断，也尚未通过历史盲测证明能区分 hit/miss。
- 面试时说“它提升可审计性和错误暴露能力，不等于证明预测更准”。

---

### 2.8 RAG 怎么评测？为什么只看最终答案不够？

#### 一句话结论

RAG 要分层评测：检索有没有找到证据、证据是否相关、生成是否忠实、系统是否可追溯、业务是否有用。

#### 第一性原理

一个错误回答可能来自：

- query 改写错；
- chunk 切错；
- embedding 召回漏；
- rerank 排错；
- prompt 拼接错；
- LLM 忽略上下文；
- 引用不支持结论。

只看最终答案无法定位问题。

#### 标准面试答案

评测维度：

检索：

- Recall@k：标准答案页是否进入 top-k；
- MRR：第一个正确结果排第几；
- nDCG：排序质量；
- coverage：证据覆盖。

生成：

- faithfulness：答案是否被上下文支持；
- answer relevance：是否回答问题；
- context relevance：上下文是否相关；
- citation precision/recall：引用是否准确。

系统：

- latency、cost、索引新鲜度、失败降级率、trace 完整度。

#### 结合你的项目

知识库：

- `rag_index.py eval` 支持 `recall@k`、`MRR`；
- 支持 bm25/dense/hybrid/rerank 多模式 A/B；
- 有 aliases 和逻辑卡 suffix 归一；
- 有 freshness gate。

金融仓：

- `agent_eval.py` 评估引用、免责声明、过期标记；
- `finance_answer_rubric.py` 评估金融回答质量；
- `claim_fidelity.py` 做 claim 级验证；
- `pit_snapshot.py` / `bitemporal_history.py` 关注无前视回放。

可引用代码路径：

- `knowledge-base-private/skills/lib/rag/evaluate.py`
- `finance-workspace-private/intelligence/eval/agent_eval.py`
- `finance-workspace-private/intelligence/eval/finance_answer_rubric.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`

#### 不能夸大的部分

- 知识库当前 eval queries 有合成痕迹，真实问题集仍需用户校准。
- 要说“评测框架已具备，但正式指标需要可信 golden set”。

---

### 2.9 长上下文能替代 RAG 吗？

#### 一句话结论

不能简单替代。长上下文解决“塞得下”，RAG 解决“找得准、可更新、可追溯、可评测”。二者互补。

#### 第一性原理

长上下文的代价：

- token 成本高；
- latency 高；
- lost-in-the-middle；
- 无法保证资料版本新鲜；
- 引用和评测更难。

RAG 的优势：

- 只取相关证据；
- 外部知识可实时更新；
- 可绑定来源；
- 可单独评测检索环节。

#### 标准面试答案

长上下文适合：

- 单份长文总结；
- 法律合同/代码仓上下文完整阅读；
- 多材料但数量可控。

RAG 适合：

- 知识持续更新；
- 文档规模大；
- 需要引用、权限、新鲜度和审计；
- 需要低成本高并发。

最佳实践是：RAG 先筛选，再用长上下文读少量高价值材料。

#### 结合你的项目

你的金融知识库有几千个实体/概念/来源页和大 relations JSON。如果全部塞进 prompt，不现实。项目明确使用：

- AGENTS.md 定义上下文加载纪律；
- 大 JSON 禁止直接 cat；
- 关系查询走 `query_relations.py`；
- RAG 先选页，再读相关内容。

可引用代码路径：

- `knowledge-base-private/AGENTS.md`
- `knowledge-base-private/scripts/query_relations.py`
- `knowledge-base-private/skills/lib/rag/README.md`

---

### 2.10 Memory 怎么设计？为什么不用直接把所有历史对话塞给模型？

#### 一句话结论

记忆系统的关键不是“存得越多越好”，而是分层、可追溯、可遗忘、不会污染事实源。

#### 第一性原理

历史对话有三类问题：

1. 噪声多：聊天流水不等于知识。
2. 会腐烂：旧判断可能过时。
3. 会自我强化：模型把自己以前生成的错误当事实。

所以记忆要区分：

- 工作记忆：本轮上下文；
- 情景记忆：发生过什么；
- 语义记忆：稳定知识；
- 程序记忆：可复用流程；
- 用户偏好/经验：只作为 prior，不是市场事实。

#### 标准面试答案

Memory 设计原则：

- 分层存储；
- 每条记录有 source、agent、date、status；
- 事实和经验分开；
- 过期知识要 stale / deprecated；
- 检索到记忆后要和当前数据交叉验证；
- 关键记忆需要人工确认或评测闭环。

#### 结合你的项目

`agent-memory` 是 Git + Markdown 的共享黑板：

- `10_knowledge`：长期方法论；
- `20_projects`：项目 MOC 和交接；
- `30_conventions`：偏好、规范；
- `40_playbooks`：可复用流程；
- `70_tutor`：人工审阅教学材料。

金融仓还有用户记忆：

- `corrections.jsonl`：纠偏；
- `judgments.jsonl`：用户判断；
- `experience_cards.jsonl`：回答经验；
- `checkpoints/verdicts`：回检校准。

可引用代码路径：

- `agent-memory/README.md`
- `agent-memory/30_conventions/frontmatter-spec.md`
- `finance-workspace-private/intelligence/services/user_memory.py`
- `finance-workspace-private/intelligence/services/experience_cards.py`
- `finance-workspace-private/intelligence/services/corrections.py`

#### 不能夸大的部分

- Agent Memory 目前主要是 Markdown/Git 黑板，对 vault 本身还没有完整 Hybrid 检索。
- 贝叶斯记忆仲裁在金融 Workbench 里仍有未落地缺口。

---

### 2.11 多 Agent 共享记忆怎么保证一致性？

#### 一句话结论

你的系统选择“Git + Markdown 黑板 + 约定 + lint + pre-commit”的轻量最终一致，而不是强一致数据库。

#### 第一性原理

多 Agent 协作需要共享状态，但过早引入中心数据库/调度器会增加复杂度。对个人项目来说：

- 写入频率低；
- 人类要能审阅；
- 工具要可迁移；
- Git 冲突可接受。

所以最终一致比强一致更划算。

#### 标准面试答案

一致性策略：

- 单一事实源 SSOT；
- append-only 交接记录；
- Git diff / review；
- pre-commit 拦截密钥和大文件；
- lint 检查 frontmatter、死链、老化；
- 冲突时人工裁决，不让 Agent 强行合并。

#### 结合你的项目

Agent Memory：

- README 定义纯文本、frontmatter、Git 托管；
- `frontmatter-spec.md` 规定 agent/source/date；
- `devin-writeback.md` 定义写回层级；
- `vault_lint.py` 检查结构。

可引用路径：

- `agent-memory/40_playbooks/devin-writeback.md`
- `agent-memory/30_conventions/maintenance.md`
- `agent-memory/scripts/vault_lint.py`

---

### 2.12 金融场景为什么特别强调 point-in-time 和无前视？

#### 一句话结论

金融研究里，正确答案不等于当时可得答案。历史回放只能使用决策时点之前已经可得的信息。

#### 第一性原理

如果 6 月 20 日才发布的研报被拿去解释 6 月 10 日的交易决策，就是前视泄露。模型会看起来很聪明，但回测无效。

需要区分：

- `publish_time`：信息产生时间；
- `available_time`：系统实际可使用时间；
- `created/updated`：知识库写入/更新日期。

#### 标准面试答案

金融 Agent 的评测要做：

- point-in-time 数据截断；
- 不可变快照；
- as-known-at 回放；
- 预测和结果分离；
- 样本外验证；
- 防止 hindsight bias。

#### 结合你的项目

知识库约定：

- `docs/conventions.md` 定义 `publish_time` 和 `available_time`；
- `pit_lib.py` / `pit_truncate.py` 做 PIT 截断；
- `audit_backfill_embargo.py` 防止回填早于发布日期。

金融仓：

- `pit_snapshot.py`；
- `bitemporal_history.py`；
- `fidelity_contract.py`；
- `claim_fidelity.py`。

可引用路径：

- `knowledge-base-private/docs/conventions.md`
- `knowledge-base-private/scripts/pit_lib.py`
- `finance-workspace-private/intelligence/eval/pit_snapshot.py`
- `finance-workspace-private/intelligence/eval/bitemporal_history.py`

---

## 3. P1 详解一：Transformer 与模型结构

> 本章目标：不只会背名词，而是能从“信息如何流动、复杂度从哪里来、为什么这样设计”回答追问。
> 统一回答模板：30 秒答案 → 第一性原理 → 公式/数据流 → 技术权衡 → 项目映射 → 边界。

### 3.1 Transformer 整体架构

#### 30 秒标准答案

> Transformer 用 Attention 建模 token 之间的依赖，用前馈网络 FFN 做逐 token 的非线性特征变换，再通过残差连接和归一化稳定深层训练。原始 Transformer 是 Encoder-Decoder；现代生成式大模型通常采用 Decoder-only，每层主要由因果自注意力、FFN、残差和归一化组成。

#### 第一性原理

语言建模需要解决两个问题：

1. **上下文聚合**：当前 token 应该从哪些历史 token 取信息；
2. **特征变换**：聚合后如何把信息映射成更有用的高维表示。

Attention 解决第一个问题，FFN 解决第二个问题。残差连接让信息和梯度能跨层直达；归一化控制数值尺度。

Decoder-only 的一层可写成：

```text
x1 = x + Attention(Norm(x))
x2 = x1 + FFN(Norm(x1))
```

这是常见的 **Pre-LN（归一化在子层之前）** 结构。最后：

```text
hidden states
→ vocabulary projection
→ logits
→ softmax
→ 下一个 token 的概率分布
```

#### 为什么现代 LLM 多用 Decoder-only

- 训练目标和生成目标统一：都是“根据左侧上下文预测下一个 token”；
- 所有参数都服务于生成，不需要单独的 encoder；
- 数据格式统一，网页、代码、对话都可串成 token 序列训练；
- 自回归生成和 KV Cache 的工程生态成熟。

但不能说 Decoder-only 在所有任务上理论最优：

- Encoder-only 仍适合双向理解、分类、检索表示；
- Encoder-Decoder 对翻译、摘要、输入输出边界明确的 seq2seq 任务仍有优势；
- 最优架构取决于任务、训练数据、参数预算和推理约束。

#### 项目映射

你的金融 Agent 没有训练 Transformer，但三类组件依赖它：

- embedding 模型：把 query 和知识页编码为语义向量；
- cross-encoder reranker：让 query 与候选文档联合编码并打分；
- 生成模型：根据市场数据、RAG 证据、用户 prior 组织回答。

正确项目说法：

> 我没有重新训练基础模型，而是把不同 Transformer 能力放在系统中合适的位置：bi-encoder 负责大规模召回，cross-encoder 负责小规模精排，decoder-only LLM 负责受证据约束的生成。

---

### 3.2 Self-Attention：公式、参数量和复杂度

#### 30 秒标准答案

> Self-Attention 先把输入投影为 Query、Key、Value。Query 表示当前位置要找什么，Key 表示每个位置可被怎样匹配，Value 是真正被聚合的信息。通过缩放点积得到相关性，经 softmax 归一后对 Value 加权求和。

#### 核心公式

输入：

```text
X ∈ R^(n × d_model)
Q = XW_Q
K = XW_K
V = XW_V
```

单头注意力：

```text
Attention(Q,K,V) = softmax(QK^T / sqrt(d_k) + M)V
```

其中：

- `n`：序列长度；
- `d_model`：隐藏维度；
- `d_k`：每个 head 的 Query/Key 维度；
- `M`：mask；被屏蔽位置加上负无穷，softmax 后权重接近 0。

#### 为什么除以 `sqrt(d_k)`

假设 Q、K 每个分量独立、均值 0、方差 1：

```text
q · k = Σ(q_i k_i)
Var(q · k) ≈ d_k
```

维度越大，点积绝对值通常越大。直接送入 softmax 会让分布过尖：

- 最大项接近 1；
- 其他项接近 0；
- softmax 梯度变小，训练不稳定。

除以 `sqrt(d_k)` 后方差恢复到约 1，使 logits 处于较稳定尺度。

#### 参数量

标准 MHA（Multi-Head Attention，多头注意力）通常有：

```text
W_Q, W_K, W_V, W_O ∈ R^(d_model × d_model)
```

忽略 bias：

```text
参数量 ≈ 4 × d_model²
```

“多头”一般是把同一个总隐藏维度切成多个 head，并不必然让参数量随 head 数增加。

#### 时间和空间复杂度

标准全注意力：

```text
Q/K/V/O 投影：O(n d_model²)
注意力分数与加权：O(n² d_model)
注意力矩阵显存：O(n²)
```

因此：

- 短序列、大隐藏维度时，线性层计算可能占主导；
- 长序列时，`n²` 的 Attention 成本会成为核心瓶颈；
- 自回归 decode 有 KV Cache 后，每步只对历史 KV 做一次查询，但总 KV 读带宽仍随上下文增长。

#### 常见追问

**Q：Self-Attention 和 Cross-Attention 区别？**
A：Self-Attention 的 Q/K/V 来自同一序列；Cross-Attention 的 Q 来自解码端，K/V 来自编码端或外部序列。

**Q：Attention 能表达顺序吗？**
A：纯 Attention 对输入排列本身没有位置感，需要位置编码或位置偏置。

**Q：Attention 权重能否直接当解释？**
A：不能简单等同。它描述该层该头的加权路径，但不等于完整因果贡献；残差、FFN、后续层都会改变结果。

---

### 3.3 Multi-Head Attention 为什么有效

#### 30 秒标准答案

> 多头注意力把隐藏空间分成多个子空间，让不同 head 并行学习不同匹配模式，例如局部搭配、远程指代、实体关系或格式结构。它的价值不是简单复制同一个 Attention，而是增加表示子空间和关系模式的多样性。

#### 第一性原理

如果只有一个 attention distribution，所有关系要挤在同一种加权模式里。多头允许：

```text
head_i = Attention(XW_Q^i, XW_K^i, XW_V^i)
MHA(X) = Concat(head_1 ... head_h)W_O
```

在总维度固定时：

```text
d_head = d_model / h
```

每个 head 的维度更小，但多个 head 可以形成不同关系视角。

#### 需要避免的错误

- 不要说“每个 head 一定分别学习语法、实体、情感”；这是可能出现的现象，不是硬编码保证。
- 不要说“head 越多越好”；head 太多会让 `d_head` 太小，也增加调度和 kernel 开销。
- 多头中可能存在冗余，工程上才有 MQA/GQA 等压缩方案。

#### 项目映射

RAG 的 embedding 和 reranker 都使用多层、多头表示，但系统设计不依赖“解释某个 head”。你的可解释性来自：

- 可追溯文档来源；
- 检索分数和召回路径；
- claim 对应 evidence；
- 确定性质量检查。

这比用 attention heatmap 当金融结论解释更可靠。

---

### 3.4 Encoder-only、Decoder-only、Encoder-Decoder

| 架构 | Attention 可见范围 | 典型目标 | 擅长任务 |
|---|---|---|---|
| Encoder-only | 双向，token 可看左右文 | Masked LM、对比学习 | 分类、抽取、embedding、rerank |
| Decoder-only | 因果，只看左侧 | Next-token prediction | 生成、对话、代码、Agent |
| Encoder-Decoder | Encoder 双向；Decoder 因果并 cross-attend encoder | 条件序列生成 | 翻译、摘要、结构化 seq2seq |

#### 标准面试答案

> Encoder-only 更像“读懂整段文本后做判断”；Decoder-only 更像“按历史逐 token 续写”；Encoder-Decoder 先把输入编码成表示，再条件生成输出。三者不是简单的新旧替代关系，而是不同信息流约束。

#### 你的项目如何映射

- BGE 类 embedding：更接近 encoder 表示模型；
- cross-encoder reranker：把 query 和 document 放在一起做双向联合判断；
- 回答生成器：decoder-only LLM；
- 这形成“召回—精排—生成”的异构模型流水线。

---

### 3.5 Causal Mask、Padding Mask 与 Prefix Mask

#### Causal Mask

生成第 `t` 个 token 时只能看到 `≤t` 的 token：

```text
可见矩阵：
1 0 0 0
1 1 0 0
1 1 1 0
1 1 1 1
```

目的不是节省计算，而是防止训练时偷看未来答案，使训练条件与推理条件一致。

#### Padding Mask

一个 batch 内句子长度不同，需要把补齐的 pad token 屏蔽，否则模型会把填充当真实输入。

#### Prefix / Prefix-LM Mask

一个前缀区域内部可双向注意，生成区域保持因果注意：

```text
[可双向理解的 prefix] → [逐 token 生成的 suffix]
```

适用于某些条件生成或统一理解—生成任务。它不同于 PEFT 中的 Prefix Tuning；前者是 attention mask，后者是训练可学习的虚拟前缀表示。

#### 常见错误

- Causal Mask 不等于把未来 token 从训练样本删除；输入仍可并行计算，只是注意力矩阵屏蔽未来位置。
- 训练 decoder-only 时可一次并行算完整序列，推理时才必须自回归逐步生成。

---

### 3.6 RoPE：为什么旋转能编码相对位置

#### 30 秒标准答案

> RoPE（Rotary Positional Embedding，旋转位置编码）不把位置向量直接加到 token embedding，而是按位置旋转 Q 和 K 的二维分量。两个位置向量做点积时，旋转角之差自然对应相对距离，所以注意力分数能同时包含内容相似性和相对位置信息。

#### 第一性原理

把每两个维度看成二维向量。位置 `m` 对应旋转：

```text
R(mθ) =
[ cos(mθ)  -sin(mθ) ]
[ sin(mθ)   cos(mθ) ]
```

对 q、k 分别旋转：

```text
q_m = R(mθ)q
k_n = R(nθ)k
```

点积：

```text
q_m^T k_n
= q^T R(mθ)^T R(nθ) k
= q^T R((n-m)θ) k
```

结果依赖 `n-m`，因此自然带相对位置信息。

#### 优点

- 不增加随最大长度增长的位置参数表；
- 与点积注意力自然结合；
- 相对位置性质适合语言；
- 可用于 KV Cache，历史 K 的位置信息已经旋转后缓存。

#### 长上下文外推为什么困难

模型只在训练长度内见过一定角度和距离分布。推理长度超出训练范围时：

- 高频维度旋转过快，位置模式失真；
- 模型未学习过超远距离的注意力行为；
- 即使位置公式能算，也不代表模型能有效利用。

常见扩展方法：

- Position interpolation：把更长位置压缩到训练范围；
- NTK-aware scaling：按频率调整旋转尺度；
- YaRN 等方法：结合不同频段缩放和温度调整；
- 长上下文继续训练：让模型真正见到长序列。

正确说法：

> RoPE scaling 可以缓解位置外推，但“配置支持 128K”不等于模型在 128K 都有稳定检索、推理和忠实度，仍要做 needle、长文问答及业务任务评测。

---

### 3.7 ALiBi 与 RoPE 怎么选

ALiBi（Attention with Linear Biases）不旋转表示，而是在注意力 logits 上加入随距离增长的线性负偏置：

```text
score(i,j) = q_i · k_j / sqrt(d_k) - slope_h × distance(i,j)
```

| 对比项 | RoPE | ALiBi |
|---|---|---|
| 注入位置 | 旋转 Q/K | 修改 attention logits |
| 位置信息 | 相对旋转相位 | 距离惩罚偏置 |
| 参数 | 通常无可学习位置表 | 每个 head 固定 slope |
| 归纳偏置 | 内容与相对位置耦合 | 越远越受惩罚 |
| 生态 | 现代 decoder LLM 非常常见 | 一些长上下文模型使用 |

标准回答：

> ALiBi 更简单，具有明确的距离衰减偏置；RoPE 表达更丰富且生态更主流。不能脱离预训练方式直接替换，因为模型权重已经适应原位置方案。

---

### 3.8 LayerNorm、RMSNorm、Pre-LN、Post-LN

#### LayerNorm

对单个 token 的隐藏维度计算：

```text
μ = mean(x)
σ² = mean((x-μ)²)
LN(x) = γ ⊙ (x-μ) / sqrt(σ²+ε) + β
```

它同时做重新中心化和重新缩放。

#### RMSNorm

```text
rms(x) = sqrt(mean(x²)+ε)
RMSNorm(x) = γ ⊙ x / rms(x)
```

它不减均值，主要控制向量尺度，计算更简单。很多现代 LLM 使用 RMSNorm，但不能泛化成“RMSNorm 一定更准”；这是稳定性、效率和模型配方共同选择。

#### Post-LN

```text
x' = Norm(x + Sublayer(x))
```

原始 Transformer 使用。深层训练时梯度跨层路径会反复经过 Norm，通常更依赖 warmup 和初始化。

#### Pre-LN

```text
x' = x + Sublayer(Norm(x))
```

残差主干提供更直接的梯度通路，深层训练更稳定，因此现代 LLM 常见。

#### 追问：Pre-LN 的代价

- 深层表示变化有时不如 Post-LN 强；
- 最终输出前通常还要一个 final norm；
- 不能只看 Norm 位置，还要结合初始化、残差缩放、学习率。

---

### 3.9 FFN、GELU 与 SwiGLU

#### FFN 的作用

Attention 在 token 之间混合信息；FFN 在每个 token 内独立变换通道：

```text
FFN(x) = W_2 φ(W_1x)
```

它通常占 Transformer 大量参数和计算。

标准两层 FFN 参数量约：

```text
2 × d_model × d_ff
```

#### GELU

GELU（Gaussian Error Linear Unit）是平滑非线性函数，可理解为按输入大小做软门控。BERT、GPT 早期模型常用。

#### SwiGLU

常见形式：

```text
SwiGLU(x) = (SiLU(xW_gate) ⊙ xW_up)W_down
SiLU(z) = z × sigmoid(z)
```

含义：

- `W_up` 产生候选特征；
- `W_gate` 决定哪些特征通过；
- 逐元素乘法实现内容相关门控；
- `W_down` 投回隐藏维度。

SwiGLU 有三块矩阵，若 `d_ff` 不变会比普通 FFN 参数更多，所以很多架构会相应调整中间维度，不能只比较公式而忽略参数预算。

#### 项目类比

可用一个谨慎类比帮助理解：

> Attention 像从多份金融材料中决定“看谁”，FFN/SwiGLU 像对已聚合的信息做通道级加工和门控。但这只是认知类比，不能把神经网络内部机制等同于你的显式 Router。

---

### 3.10 MHA、MQA、GQA、MLA

#### 30 秒标准答案

> MHA 每个 Query head 都有自己的 K/V head，质量强但 KV Cache 大；MQA 让所有 Query head 共享一组 K/V，最省 KV 但可能损失表达；GQA 让若干 Query head 共享一组 K/V，是质量与效率折中；MLA 用低秩潜表示压缩 KV 相关状态，进一步降低缓存和带宽，但实现更复杂且依赖特定架构。

设：

- Query heads：`H_q`
- KV heads：`H_kv`

则：

```text
MHA: H_kv = H_q
GQA: 1 < H_kv < H_q
MQA: H_kv = 1
```

#### 为什么减少 KV head 能加速

自回归服务需要为每层、每个历史 token 保存 K 和 V。缓存近似正比于：

```text
H_kv × d_head
```

减少 `H_kv`：

- KV Cache 更小；
- 每步 decode 从显存读取的数据更少；
- 可容纳更多并发请求或更长上下文。

#### 质量权衡

- K/V 共享越多，不同 Query head 能访问的独立记忆子空间越少；
- MQA 最激进；
- GQA 常作为工程折中；
- 从 MHA 转 GQA 通常需要训练或 uptraining，不能只在配置中删 head。

#### MLA

MLA（Multi-head Latent Attention，多头潜在注意力）的核心思想是把 K/V 相关表示压缩到低维 latent，再在需要时恢复或吸收进投影计算。回答时应强调：

- 它不是简单的“更多 KV 共享”；
- 目标同样是减少 KV Cache 和内存带宽；
- 具体维度、RoPE 解耦方式依模型实现而异；
- 不要在没读目标模型实现时背一个万能公式。

---

### 3.11 FlashAttention：为什么“数学一样，速度更快”

#### 30 秒标准答案

> FlashAttention 是 IO-aware 的精确注意力算法。它不改变 Attention 的数学结果，而是把 Q/K/V 分块放进更快的片上 SRAM，通过 tiling 和 online softmax 避免把完整 `n×n` 注意力矩阵反复写入和读取高带宽显存 HBM，从而减少 IO、降低显存并提高速度。

#### 第一性原理

GPU 的算力增长快于显存带宽。标准 Attention 的问题不只是 FLOPs，而是：

```text
生成大矩阵 S = QK^T
→ 写回 HBM
→ 读出做 softmax
→ 再写回
→ 再读出乘 V
```

FlashAttention 分块计算，并维护每行 softmax 的：

- 当前最大值；
- 指数和；
- 累积输出。

因此不需要在 HBM 中物化完整 Attention 矩阵。

#### 必考边界

- 它是 exact attention，不是稀疏近似；
- 理论 Attention 计算量仍大体是 `O(n²d)`；
- 主要改进 IO 复杂度和中间显存；
- 实际加速依赖 GPU、数据类型、序列长度、head dimension、kernel 支持；
- FlashAttention 和 PagedAttention 不同：前者优化单次 attention kernel，后者管理 serving 的 KV Cache。

---

### 3.12 MoE：为什么参数很多但每 token 计算有限

#### 30 秒标准答案

> MoE（Mixture of Experts，混合专家）把一部分稠密 FFN 替换成多个 expert。Router 为每个 token 选择 top-k expert，只激活少数专家，所以总参数量可以很大，而单 token 的活跃计算量相对有限。核心挑战是路由稳定、负载均衡、跨设备通信和专家容量。

#### 数据流

```text
token hidden state
→ router logits
→ 选择 top-k experts
→ token 分发到 expert
→ expert FFN 计算
→ 加权合并
```

如果有 `E` 个 expert、每 token 只激活 `k` 个：

- 总参数量随 `E` 增长；
- 活跃 FFN 计算更接近 `k` 个 expert；
- 但 Router 和 all-to-all 通信不可忽略。

#### 为什么需要负载均衡

如果大部分 token 都被路由到少数专家：

- 热门 expert 超容量、排队或丢 token；
- 冷门 expert 学不到东西；
- 多卡计算不均衡；
- 吞吐下降。

因此常见辅助机制包括：

- load balancing auxiliary loss；
- expert capacity；
- router z-loss；
- expert parallelism；
- 无辅助损失的偏置调整等新方案。

#### Dense 与 MoE 怎么选

| 维度 | Dense | MoE |
|---|---|---|
| 每 token 激活 | 全部参数 | 少数 expert |
| 实现复杂度 | 较低 | 高 |
| 通信 | 常规并行通信 | 额外 token dispatch/all-to-all |
| 小规模部署 | 更简单 | 容易被调度开销抵消 |
| 扩大总参数 | 计算同步增加 | 可保持相近活跃参数 |

不能说“MoE 推理一定便宜”：虽然活跃 FLOPs 较低，但所有专家权重仍要存储或分布，通信、batch 和硬件利用率决定真实成本。

---

### 3.13 Tokenizer、BPE 与 SentencePiece

#### 30 秒标准答案

> Tokenizer 把字符串映射为离散 token id。BPE 从较小符号开始，反复合并高频相邻片段；SentencePiece 是直接从原始文本训练和执行子词切分的工具体系，可实现 BPE 或 Unigram，不依赖语言专用空格分词。

#### 为什么不能按“词”直接建词表

- 词表无限增长；
- 新词、公司名、代码无法覆盖；
- 中文没有天然空格；
- 纯字符序列又太长。

子词是折中：

- 高频词合成少量 token；
- 低频词拆成可组合片段；
- 未登录词仍能表示；
- 词表大小与序列长度之间可调。

#### BPE 过程

```text
1. 从字符/字节等基础符号开始
2. 统计相邻 pair 频率
3. 合并最高频 pair 为新 token
4. 重复直到达到目标词表大小
```

#### SentencePiece 要点

- 把空格也作为普通符号处理；
- 可直接处理中文、日文等文本；
- 常见模型包括 BPE 与 Unigram LM；
- “SentencePiece”不是与 BPE 同一层级的单一算法名称。

#### 词表大小的权衡

词表更大：

- 序列通常更短；
- embedding/output projection 参数更多；
- 稀有 token 学习样本更少。

词表更小：

- 参数更省；
- 序列更长，Attention/KV 成本增加；
- 代码、数字、中文可能被切得过碎。

#### 金融场景

金融文本特别关注：

- 股票代码 `600519` 是否被稳定保留；
- 公司名、产品名、英文缩写；
- 百分比、日期、小数；
- 同一实体的别名。

你的项目真实映射：

> 生成模型使用其自身 tokenizer；知识库 BM25 则使用独立的轻量 lexical tokenizer，采用汉字单字 + bigram，并保留拉丁字母和数字片段。这样做是为了零依赖、确定性和股票代码可检索，不代表它等同于 LLM 的 BPE tokenizer。

---

### 3.14 Transformer 高频追问与纠错

1. **Attention 的 `O(n²)` 指什么？**
   主要指 token 两两匹配形成的注意力分数规模；完整层还包括 `O(nd²)` 投影。

2. **FlashAttention 是否把复杂度降成线性？**
   没有。它主要减少 HBM IO 和中间显存，标准全注意力的理论 FLOPs 仍近似二次。

3. **RoPE 是否保证无限长度？**
   不保证。公式可计算不等于模型在未训练长度上会推理。

4. **RMSNorm 是否一定优于 LayerNorm？**
   不一定；它更简洁高效，但效果依模型配方。

5. **GQA 是否只是把 KV Cache 除以 group 数？**
   缓存确实按 KV head 数缩小，但质量、kernel 和投影参数也要一起考虑。

6. **MoE 的“参数量”应怎么报？**
   同时报总参数和每 token 活跃参数，否则容易误导。

7. **你的项目用了哪些？**
   使用了基于 Transformer 的现成 embedding、reranker 和 LLM 接口；没有自己训练 Transformer、改 RoPE、训练 MoE 或实现 FlashAttention kernel。

---

## 4. P1 详解二：训练、对齐与 PEFT

### 4.1 语言模型预训练目标

#### 30 秒标准答案

> Decoder-only 语言模型通常用最大似然训练：给定前面的 token，最大化真实下一个 token 的条件概率。工程上等价于最小化每个位置的交叉熵。模型不是逐句背诵规则，而是在海量样本上学习一个条件概率分布。

给定序列 `x_1 ... x_T`：

```text
P(x_1...x_T) = ∏ P(x_t | x_<t)
```

负对数似然损失：

```text
L_NLL = -Σ log Pθ(x_t | x_<t)
```

通常对有效 token 取平均。训练使用 teacher forcing：计算位置 `t` 时输入真实历史 token，而不是模型自己先前生成的 token。

#### 第一性原理

文本联合概率难以直接建模。链式法则把它拆成一系列“预测下一步”：

```text
看到“中国人民银行”
→ 下一个 token 可能是“发布”“决定”“表示”……
```

长期训练后，模型为了降低下一个 token 的预测误差，会学习：

- 词法和语法；
- 世界知识的统计关联；
- 文档结构；
- 代码和推理模式；
- 不同任务的隐式表示。

但 next-token objective 不自动保证：

- 事实永远正确；
- 遵循用户意图；
- 安全；
- 给出引用；
- 承认不确定。

所以才需要 SFT、偏好对齐和系统约束。

#### Perplexity

困惑度：

```text
PPL = exp(平均 token NLL)
```

PPL 越低表示模型对测试文本的平均预测更好，但：

- 不同 tokenizer 的 PPL 不宜直接比较；
- PPL 低不等于指令遵循、事实性或业务效果好；
- 金融 Agent 最终还要评测检索、引用、PIT 和决策支持。

---

### 4.2 Pre-training 与 Continue Pre-training

#### Pre-training

从随机初始化或接近随机初始化开始，在大规模通用语料上学习基础能力。关键工作包括：

- 数据收集、去重、清洗和配比；
- tokenizer；
- 模型架构与 scaling；
- 分布式训练；
- 数值稳定性；
- checkpoint 和评测。

#### Continue Pre-training

Continue Pre-training（CPT，继续预训练，也常叫 domain-adaptive pretraining）从已有 base model 出发，继续使用语言建模目标训练：

- 注入领域语料；
- 适配新语言或代码分布；
- 扩展上下文长度；
- 更新较大规模知识分布。

#### 与 SFT 的区别

| 维度 | CPT | SFT |
|---|---|---|
| 主要数据 | 大量原始领域文本 | instruction-response |
| 训练目标 | 通常预测所有文本 token | 通常重点计算 assistant answer loss |
| 主要目的 | 调整领域分布和基础表示 | 学会按指令完成任务 |
| 数据规模 | 往往较大 | 可较小但需高质量 |
| 风险 | 灾难性遗忘、语料污染 | 过拟合格式、能力偏移 |

一句话：

> 预训练更像“广泛阅读并形成语言和知识表示”，SFT 更像“看标准示范，学会如何回答”。

#### 金融项目选择

你的系统目前不需要 CPT：

- 金融事实变化快，写进权重后难更新、难引用；
- 已有知识库和市场数据库更适合外置事实；
- 你的核心瓶颈是证据治理和评测，不是 base model 完全看不懂金融语言。

如果未来确实发现模型连专业语料的语言分布都无法理解，且有大规模、合法、高质量金融原文，才考虑 CPT；不能用几十份研报就宣称完成领域继续预训练。

---

### 4.3 SFT：目标、数据格式与 masking

#### 30 秒标准答案

> SFT（Supervised Fine-Tuning，有监督微调）用高质量输入—理想输出示范继续训练模型。损失仍通常是 token-level cross-entropy，但会用 chat template 串联 system、user、assistant，并常把非 assistant token mask 掉，只让模型为目标回答承担损失。

示例：

```text
<system>你是金融研究助手</system>
<user>分析某公司利润增长的驱动</user>
<assistant>先区分收入、毛利率、费用率和一次性项目……</assistant>
```

常见 loss mask：

```text
system tokens:    ignore
user tokens:      ignore
assistant tokens: calculate loss
padding tokens:   ignore
```

有些配方也训练完整对话 token。面试时要说“取决于训练实现”，不要把 assistant-only 当唯一方案。

#### SFT 真正学到什么

- 指令遵循；
- 回答格式；
- 工具调用 schema；
- 领域表达；
- 拒答和安全示范；
- 某些任务模式。

它也可能吸收知识，但把 SFT 简化成“只学格式、绝不学知识”是错误的。更准确：

> SFT 可以改变知识行为和任务能力，但少量指令数据不是可靠、可更新、可引用的事实数据库。

#### 数据质量比数量更重要的原因

同一个问题若有冲突答案，模型收到相反梯度；模板化垃圾数据会让输出同质化。SFT 数据应检查：

- 正确性；
- 多样性；
- 难度覆盖；
- 去重；
- 长度和任务分布；
- 安全边界；
- train/validation 泄漏；
- chat template 一致性。

#### 项目映射

若未来给金融 Agent 做 SFT，合理目标是：

- 稳定输出“结论—证据—风险—翻转条件”格式；
- 稳定生成合法 tool call；
- 学会在证据不足时显式暴露缺口；
- 学会区分事实、解释、预测、动作。

不合理目标是：

- 把每日行情和最新公告长期写进 adapter；
- 用 SFT 代替 RAG freshness；
- 用少量自生成问答证明模型获得可靠金融知识。

---

### 4.4 经典 RLHF：SFT、Reward Model、PPO

#### 30 秒标准答案

> 经典 RLHF（Reinforcement Learning from Human Feedback，人类反馈强化学习）一般先得到 SFT 模型，再让模型对同一 prompt 生成多个回答，由人类排序训练 Reward Model，最后用 PPO 优化策略模型，使奖励上升，同时用 KL 惩罚限制它不要偏离参考模型太远。

#### 完整流水线

```text
1. Pretrained base model
2. SFT on demonstrations
3. 对同一 prompt 采样多个 responses
4. 人类给 preference/ranking
5. 训练 Reward Model
6. PPO 更新 policy
7. KL 约束 policy 与 reference model 的距离
8. 安全、能力和回归评测
```

#### Reward Model

输入 `(prompt, response)`，输出标量奖励：

```text
rθ(x,y)
```

偏好对 `(y_w, y_l)` 常用 Bradley-Terry 风格损失：

```text
L_RM = -log σ(r(x,y_w) - r(x,y_l))
```

#### PPO 中有哪些模型

典型工程可能包含：

1. policy / actor：正在优化的生成模型；
2. reference model：冻结，计算 KL；
3. reward model：给完整回答奖励；
4. value / critic：估计 value，降低策略梯度方差。

实现可能共享部分权重，但概念上要分清。

#### PPO 为什么复杂

- on-policy 采样成本高；
- 同时维护多个大模型；
- advantage、value、clip、KL 等超参敏感；
- reward hacking；
- 训练不稳定；
- 分布式 rollout 与训练调度复杂。

#### PPO 核心直觉

如果一次更新把 policy 推太远，旧数据将迅速失效。PPO 用概率比值裁剪限制更新：

```text
ratio = πθ(a|s) / πold(a|s)
L_clip = min(ratio × A, clip(ratio, 1-ε, 1+ε) × A)
```

在 LLM 中还常加：

```text
reward_total = reward_model_score - β × KL(policy || reference)
```

#### 常见错误

- RLHF 不等于“人直接给每个 token 奖励”；
- PPO 的 policy 不是“Actor + Critic 两个模型组成一个策略”；Actor 是 policy，Critic 是 value estimator；
- Reward Model 分数高不等于真实质量高，模型可能学会钻 RM 漏洞；
- KL 不是越小越好，过小可能没学到偏好，过大可能能力漂移。

---

### 4.5 DPO：为什么可以跳过显式 Reward Model 和 PPO

#### 30 秒标准答案

> DPO（Direct Preference Optimization，直接偏好优化）从 KL 约束的奖励最大化目标推导出一个偏好分类损失，直接提高 chosen 相对 rejected 的概率优势，并用 reference model 作为基准。它省掉显式 Reward Model 和 on-policy PPO，工程简单稳定，但依赖离线偏好数据，探索能力和在线奖励优化能力弱于通用 RL。

定义：

```text
Δ_policy =
log πθ(y_w|x) - log πθ(y_l|x)

Δ_ref =
log πref(y_w|x) - log πref(y_l|x)
```

DPO 损失：

```text
L_DPO =
-log σ(β(Δ_policy - Δ_ref))
```

直觉：

- 如果 policy 比 reference 更偏好 chosen，目标变好；
- 如果只无脑提高两个回答概率而不改变相对偏好，不足以优化目标；
- `β` 控制偏离 reference 的尺度。

#### DPO 与 PPO 对比

| 维度 | DPO | PPO-based RLHF |
|---|---|---|
| 数据 | 离线 chosen/rejected | 在线 rollout + reward |
| 显式 RM | 不需要 | 通常需要 |
| Critic | 不需要 | 通常需要 |
| 工程复杂度 | 较低 | 高 |
| 探索新策略 | 弱 | 更强 |
| 奖励类型 | 偏好对最自然 | 可接任意可计算 reward |
| 稳定性 | 通常更容易 | 超参和系统更复杂 |

不能说 DPO“全面取代 PPO”。如果任务有可验证环境奖励、需要在线探索、多步决策或持续更新，RL 方法仍可能更合适。

---

### 4.6 IPO、KTO、ORPO、SimPO、GRPO、RLVR 的位置

这些方法不要背成孤立缩写，应先按问题分类：

```text
离线 preference optimization
  DPO / IPO / KTO / ORPO / SimPO

在线或采样式 reinforcement learning
  PPO / GRPO / 其他 policy-gradient 方法

奖励来源
  人类偏好、AI 反馈、Reward Model、可验证规则
```

#### IPO

IPO（Identity Preference Optimization）可理解为对 DPO 类目标的改造，强调避免偏好数据可分时 logits 无限制增大，使用更明确的 margin/回归式约束以改善泛化。

面试重点：

- 它属于离线偏好优化；
- 目标是改善 DPO 可能的过拟合或偏好 margin 无限扩张问题；
- 不要在没看具体论文实现时声称“永远优于 DPO”。

#### KTO

KTO（Kahneman-Tversky Optimization）可以使用“这个回答好/坏”的二元反馈，不要求每条数据都有严格 chosen-rejected 配对。

适用场景：

- 点赞/点踩日志；
- 正负样本不天然成对；
- 配对标注成本高。

#### ORPO

ORPO（Odds Ratio Preference Optimization）把 SFT 的生成损失与偏好 odds-ratio 目标组合，可在一个阶段同时做 instruction learning 与 preference alignment，并通常不需要独立 reference model。

应回答的权衡：

- pipeline 更简化；
- 但 SFT 与偏好权重需要调节；
- 参考模型缺失不代表完全没有正则化问题。

#### SimPO

SimPO（Simple Preference Optimization）常用长度归一化的平均 log probability 作为隐式 reward，并加入 target margin；不依赖 reference model。

为什么关注长度归一：

- 序列总 log probability 随长度累加；
- 不处理长度可能产生偏差；
- 平均 log probability 更接近逐 token 质量，但也不是万能。

#### GRPO

GRPO（Group Relative Policy Optimization）对同一 prompt 采样一组回答，用组内奖励相对值构造 advantage，避免单独训练与 policy 同规模的 critic。

直觉：

```text
同题生成 G 个答案
→ 计算各自 reward
→ 用组均值/方差标准化
→ 高于组平均的回答得到正 advantage
→ 低于组平均的得到负 advantage
```

优势：

- 省 critic 显存和训练；
- 适合一题多采样；
- 可与可验证奖励结合。

局限：

- 多次采样本身昂贵；
- 组内 reward 方差不足时学习信号弱；
- reward 设计错误仍会被 hacking；
- GRPO 不等于“不要 reference/KL/clip”，具体实现仍可能使用这些稳定机制。

#### RLVR

RLVR（Reinforcement Learning with Verifiable Rewards，可验证奖励强化学习）更像一类训练范式，不是唯一固定算法：

- 数学题用最终答案检查；
- 代码题运行测试；
- 结构化输出做 schema validation；
- 工具任务检查执行结果。

可验证 reward 相比人类偏好更客观、可扩展，但只覆盖“容易自动验证”的维度。形式正确不等于推理可靠，测试也可能不完备。

#### 与金融 Agent 的关系

你的项目目前**没有执行这些模型训练**。可迁移思想是：

- output review 类似规则反馈，但没有更新模型参数；
- claim fidelity、引用覆盖率、PIT 检查可形成部分可验证 reward；
- 将来可以用这些信号做数据筛选或训练实验；
- 金融预测最终回报噪声大、延迟长、非平稳，不能简单当高质量 RL reward。

---

### 4.7 LoRA：低秩更新到底省了什么

#### 30 秒标准答案

> LoRA（Low-Rank Adaptation，低秩适配）冻结原权重 `W`，把任务更新写成低秩矩阵乘积 `BA`，只训练 A、B。它显著减少可训练参数、梯度和优化器状态，但前向与反向仍要通过基座模型，所以计算量和 activation 显存不会按参数比例同等下降。

设：

```text
W ∈ R^(d_out × d_in)
A ∈ R^(r × d_in)
B ∈ R^(d_out × r)
```

则：

```text
y = Wx + (α/r)BAx
```

可训练参数：

```text
r(d_in + d_out)
```

远小于：

```text
d_in × d_out
```

当 `r << d_in,d_out` 时节省明显。

#### 初始化

常见做法让一个矩阵随机初始化，另一个为零，使初始：

```text
BA = 0
```

模型开始时行为与 base model 一致，同时非零一侧使梯度能打破对称并开始学习。

#### target modules

常见目标：

- `q_proj`, `k_proj`, `v_proj`, `o_proj`；
- 也可包括 `gate_proj`, `up_proj`, `down_proj`。

不能说固定只调 Q/K 最优。目标矩阵、rank 和数据分布需要实验。

#### LoRA 真正节省

- trainable weights；
- gradients；
- optimizer states；
- 多任务 adapter 存储；
- 分布式同步的可训练梯度量。

不完全节省：

- 基座权重仍要加载；
- 主网络前向仍执行；
- 反向要计算传向 adapter 的梯度；
- activation 仍可能是大头。

#### 合并

推理前可计算：

```text
W_merged = W + (α/r)BA
```

从而避免额外 adapter matmul。多 adapter 动态服务时可能保持未合并，以换取灵活性。

---

### 4.8 QLoRA 与其他 PEFT

#### QLoRA

QLoRA 的核心：

- 冻结的 base weights 以 4-bit 存储；
- 计算时按需要反量化到较高精度；
- 训练 LoRA adapter；
- 常见关键技术包括 NF4、double quantization、paged optimizer。

它减少的是基座权重存储和相关内存压力，不代表所有计算都直接用 4-bit 完成。

#### 为什么 QLoRA 可能不更快

- 反量化有开销；
- 低比特 kernel 和硬件支持决定吞吐；
- 小 batch 或不匹配的 kernel 可能更慢；
- 主要卖点首先是“能装下并训练”，不是无条件更高 tokens/s。

#### PEFT 家族

| 方法 | 训练什么 | 优点 | 代价 |
|---|---|---|---|
| LoRA | 权重旁路低秩矩阵 | 效果/生态/可合并较好 | 仍需主模型前反向 |
| Adapter | 层间小网络 | 模块化 | 常增加推理层和延迟 |
| Prompt Tuning | 输入端可学习软 token | 参数极少 | 小模型/复杂任务效果可能弱 |
| Prefix Tuning | 每层 attention 的可学习 prefix K/V | 更深层影响注意力 | 占用有效 prefix/KV，实现更复杂 |
| P-Tuning | 学习连续 prompt 表示 | 适合特定任务 | 版本定义多，面试需说明具体方案 |

#### 全量微调还是 PEFT

考虑：

- 数据量和任务分布变化有多大；
- 计算预算；
- 是否要保留通用能力；
- 是否要服务多个任务；
- 是否可接受 adapter 管理；
- 质量提升是否经评测证明。

不能用“10k 数据以上一定全量微调”这类固定阈值。模型规模、数据质量、任务距离和预算更关键。

---

### 4.9 数据工程：去重、过滤、配比与主动学习

#### 为什么数据是训练的第一性瓶颈

梯度只反映训练样本。如果样本错误、重复、泄漏或冲突，优化器会高效地学错。

#### 去重

层级：

- exact dedup：完全相同文档；
- near dedup：MinHash/SimHash 等近重复；
- semantic dedup：embedding 相近；
- benchmark contamination：训练语料含测试答案。

重复过多会：

- 浪费 token 预算；
- 放大特定来源偏见；
- 增加记忆化；
- 使 validation 虚高。

#### 质量过滤

- 规则：长度、乱码、广告、重复率、语言；
- classifier：质量、安全、领域；
- perplexity：异常文本筛选；
- source weighting：可信来源更高权重；
- 人工抽检。

注意：用模型过滤数据会把过滤模型的偏见带入训练集。

#### 数据配比

训练分布不是简单“全部混合”。要控制：

- 通用 vs 领域；
- 中文 vs 英文；
- 代码 vs 自然语言；
- 简单 vs 困难；
- 安全 vs 能力；
- 新数据 vs replay 旧数据。

#### 主动学习

优先标注模型最不确定、最易错或业务价值最高的样本：

```text
模型运行
→ 找失败簇/低置信/分歧样本
→ 人工标注
→ 加入下一轮训练
→ 再评测
```

你的项目已有潜在数据源：

- output review 的失败类型；
- answer feedback；
- experience cards；
- claim fidelity 缺口；
- 历史回放的 hit/miss。

但这些目前是系统评测/记忆信号，不等于已经形成训练闭环。

---

### 4.10 灾难性遗忘

#### 30 秒标准答案

> 灾难性遗忘是模型在新分布上继续训练后，新任务变好但原有能力下降。原因是同一参数被新梯度覆盖。缓解方法包括混入通用 replay 数据、降低学习率、减少训练步数、PEFT、正则化以及持续做旧能力回归评测。

#### 判断方式

不能只看领域 validation：

```text
领域集提升
通用集下降
安全集下降
格式集提升
```

这就是多目标权衡，不应只报告最好的一项。

#### 缓解

- domain data 与 general replay 混合；
- 更小 learning rate；
- warmup 和合理 schedule；
- early stopping；
- LoRA/adapter 限制更新空间；
- checkpoint soup/merge 需谨慎；
- 多套能力评测矩阵。

PEFT 可能缓解遗忘，但不保证不忘：adapter 仍可能改变输出行为，且合并后也可能损害通用能力。

---

### 4.11 AdamW、学习率、Warmup 与 Cosine Decay

#### AdamW

Adam 使用梯度一阶矩和二阶矩做自适应更新。AdamW 把 weight decay 与梯度更新解耦：

```text
m_t = β1 m_(t-1) + (1-β1)g_t
v_t = β2 v_(t-1) + (1-β2)g_t²
θ ← θ - lr × m_hat/(sqrt(v_hat)+ε) - lr × wd × θ
```

面试重点：

- AdamW 不是“Adam 加 L2 完全等价”；
- 解耦 weight decay 更符合直接缩小权重的意图；
- Norm 和 bias 参数是否 decay 取决于配方。

#### Warmup

训练初期参数和 optimizer moments 尚未稳定，直接使用峰值学习率容易发散。Warmup 让 lr 从小到大。

#### Cosine Decay

Warmup 后按余弦逐渐降低学习率：

```text
lr(t) = lr_min + 0.5(lr_max-lr_min)(1+cos(π progress))
```

直觉：

- 前期大步学习整体结构；
- 后期小步收敛；
- 不是所有任务都必须 cosine，也可 constant、linear decay、WSD 等。

#### 学习率选择

不能死背“7B 一定 3e-4”：

- pretraining、CPT、SFT、LoRA 的 lr 尺度不同；
- global batch、数据质量、模型规模、初始化和 optimizer 都影响；
- 应通过 loss、gradient norm、validation 和小规模 sweep 决定。

---

### 4.12 Batch、Gradient Accumulation 与 Clipping

#### Global Batch

```text
global_batch
= micro_batch_per_gpu
× gradient_accumulation_steps
× data_parallel_world_size
```

若按 token 计，应进一步乘有效 sequence tokens。

#### Gradient Accumulation

多次 micro-batch 前反向后再 optimizer step：

- 降低单步 activation 显存；
- 模拟更大 global batch；
- 不能减少完成同样 token 数的总计算；
- accumulation 越多，参数更新频率越低。

#### Gradient Clipping

常见 global norm clipping：

```text
if ||g|| > c:
    g ← g × c / ||g||
```

用于抑制异常大梯度，但如果长期每步都被 clip，应排查：

- learning rate；
- 数据异常；
- loss scaling；
- 数值精度；
- 模型实现错误。

Clipping 是安全带，不是修复所有发散的万能药。

---

### 4.13 FP32、FP16、BF16、FP8 与 Loss Scaling

| 格式 | 位数 | 关键特点 | 常见用途 |
|---|---:|---|---|
| FP32 | 32 | 范围和精度高 | master weights、敏感计算 |
| FP16 | 16 | 尾数较多但指数范围小 | 混合精度，常需 loss scaling |
| BF16 | 16 | 与 FP32 相同指数位宽，尾数较少 | 现代训练常用，范围更稳 |
| FP8 | 8 | 更低精度，需逐 tensor scaling/recipe | 新硬件训练和推理加速 |

#### FP16 为什么需要 Loss Scaling

小梯度可能低于 FP16 可表示范围而下溢为 0。把 loss 乘以 `S`：

```text
scaled_loss = S × loss
scaled_grad = S × grad
```

反向后再除以 `S`。动态 loss scaling 在溢出时降低 `S`，稳定时提高。

#### BF16

BF16 指数范围接近 FP32，因此通常更少需要 loss scaling；但尾数更短，局部精度更低。现代训练中“范围”往往比额外尾数更重要。

#### FP8

FP8 动态范围和精度更有限，通常不能只靠一个全局 loss scale，需要：

- 每个 tensor 或分组 scale；
- amax 历史；
- E4M3/E5M2 等格式选择；
- 高精度累加和敏感算子保留。

不能说“FP8 就是把所有张量无脑改成 8 位”。

---

### 4.14 Gradient Checkpointing

#### 30 秒标准答案

> Gradient Checkpointing 用计算换显存。普通反向传播保存很多中间 activation；checkpointing 只保存部分边界，反向时重新执行前向来恢复中间结果，因此 activation 显存降低，但训练变慢。

数据流：

```text
普通：
forward 保存所有 activation
→ backward 直接使用

checkpoint：
forward 只存检查点
→ backward 重新计算区间 activation
→ 求梯度
```

它不减少：

- 模型参数；
- optimizer states；
- 理论训练任务本身。

它主要减少 activation memory，尤其适合深层和长序列。

---

### 4.15 训练异常排查

#### Loss spike

排查顺序：

1. 是否特定数据 batch 异常；
2. learning rate 是否过大或 schedule 跳变；
3. gradient norm 是否突增；
4. 混合精度 overflow；
5. 分布式通信或 checkpoint 恢复错误；
6. tokenizer/chat template/mask 错位。

单次 spike 后恢复不一定致命；持续恶化才说明训练失稳。

#### NaN / Inf

- 降低 lr；
- 检查 loss scaling；
- 检查除零、log(0)、softmax mask 全负无穷；
- 使用 BF16 或敏感算子 FP32；
- 检查异常样本；
- 记录首个出现 NaN 的 layer/gradient。

#### 训练 loss 降，验证 loss 升

典型过拟合或分布不匹配：

- early stop；
- 更多/更干净数据；
- dropout/weight decay；
- 降 rank 或训练步数；
- 检查 validation 是否代表真实业务；
- 检查 train/val template 是否一致。

#### Loss 正常但生成坏

- loss mask 是否训练错角色；
- EOS 是否正确；
- chat template 是否一致；
- decoding 参数；
- 训练数据是否模板化；
- 只看 token loss 没看任务评测；
- checkpoint 转换/adapter 加载错误。

---

### 4.16 训练章节的项目边界

面试建议这样说：

> 我的金融 Agent 当前没有训练基础模型，也没有做 RLHF、DPO 或 GRPO。项目的“对齐”主要发生在系统层：事实必须来自数据源，RAG 有新鲜度门禁，用户记忆只当 prior，回答需要证据、反证和缺口，输出再经过确定性 review。未来如果积累了足够反馈，可以先把失败样本做成 SFT 或偏好数据，但会先建立离线评测，避免为了训练而训练。

不能说：

- “我用了 RLHF”——规则审稿不是 RLHF；
- “经验卡就是 Reward Model”——它是文本化经验记忆；
- “用户点赞就是 DPO”——只有整理成偏好对并更新模型才是训练；
- “用了 API 模型就等于部署了推理框架”。

---

## 5. P1 详解三：显存、分布式训练与长上下文

### 5.1 训练显存由什么组成

#### 30 秒标准答案

> 训练显存不能只按“参数量 × 数据类型字节数”估算。完整组成包括模型参数、梯度、优化器状态、可能的 FP32 master weights、activation、中间临时 buffer、通信 bucket 和显存碎片。推理主要看权重、KV Cache 和运行时 workspace；训练还要为反向传播和 optimizer 付出更大成本。

#### 数据类型字节数

| 类型 | 理论字节/元素 |
|---|---:|
| FP32 | 4 |
| FP16 | 2 |
| BF16 | 2 |
| FP8 | 1 |
| INT8 | 1 |
| INT4 | 0.5 |

实际文件和显存可能更大，因为还有：

- scale / zero-point；
- group metadata；
- 对齐与 padding；
- 未量化层；
- kernel workspace；
- 框架对象。

#### 只加载权重的粗估

`P` 个参数、每参数 `b` 字节：

```text
weight_memory ≈ P × b
```

例如 7B 参数：

```text
FP16/BF16: 7e9 × 2 ≈ 14 GB
FP32:      7e9 × 4 ≈ 28 GB
INT8:      7e9 × 1 ≈ 7 GB
INT4:      7e9 × 0.5 ≈ 3.5 GB
```

这是十进制 GB 粗估，不含任何额外开销，不能据此断言某张同容量 GPU 一定装得下。

---

### 5.2 AdamW 全量训练为什么常按约 16 bytes/param 起算

一种常见 mixed precision 配方：

```text
FP16/BF16 model parameter:  2 bytes
FP16/BF16 gradient:         2 bytes
FP32 master parameter:      4 bytes
FP32 Adam first moment m:   4 bytes
FP32 Adam second moment v:  4 bytes
----------------------------------
total:                     16 bytes/param
```

有的实现不保留独立 master weight，或梯度/optimizer 使用不同精度，所以可能是 12、16 或其他数字。正确面试说法：

> 16 bytes/param 是特定 Adam mixed-precision 配方的粗略下界，不是统一常数；还未包含 activation、临时 buffer 和碎片。

对于 7B：

```text
7e9 × 16 ≈ 112 GB
```

再加 activation 后，单卡显然很难做全量训练。

#### LoRA 显存为什么小很多但不是“只剩 adapter”

LoRA 冻结 base model：

- base weights 仍占显存；
- 不需要为全部 base weights 保存梯度和 Adam states；
- 只为 adapter 保存 trainable weights、gradients、optimizer states；
- activation 仍需反向，因此可能仍很大。

QLoRA 再把冻结 base weights 压到 4-bit，从而进一步降低权重占用。

---

### 5.3 Activation 显存为什么难用一个公式

Activation 与以下因素有关：

```text
batch size
× sequence length
× hidden size
× number of layers
× 每层保存的中间张量数量
× bytes
```

还受：

- 标准 Attention 是否保存 `n×n` 矩阵；
- FlashAttention；
- Gradient Checkpointing；
- FFN 中间维度；
- dropout；
- tensor/sequence parallel；
- autograd 实现。

长上下文下：

- 普通 Attention 中间项可能按 `n²` 增长；
- 即使 FlashAttention 避免物化完整矩阵，其他 activation 和计算仍随长度显著增长；
- batch 往往被迫下降。

粗略原则：

> 参数显存主要随模型规模增长；activation 主要随 batch、长度、层数和隐藏维度增长；KV Cache 是推理阶段随并发和上下文增长的核心状态。

---

### 5.4 Data Parallel

#### 30 秒标准答案

> Data Parallel（数据并行）在每张 GPU 放完整模型，各自处理不同 micro-batch，反向后对梯度做 all-reduce，使参数保持一致。它容易扩吞吐，但不解决单卡放不下完整模型的问题。

```text
GPU0: full model + batch shard 0
GPU1: full model + batch shard 1
...
backward
→ all-reduce gradients
→ 每卡执行相同 optimizer update
```

优点：

- 实现简单；
- 计算扩展自然；
- 每卡 batch 独立。

代价：

- 参数、梯度、optimizer states 在每卡复制；
- global batch 随卡数扩大，需要调整训练配方；
- 梯度 all-reduce 通信。

DDP（DistributedDataParallel）就是常见同步数据并行实现。

---

### 5.5 Tensor Parallel

#### 30 秒标准答案

> Tensor Parallel（张量并行）把一个大矩阵运算切到多张 GPU，例如按列切 QKV 投影、按行切输出投影。它能解决单层权重放不下的问题，但每层都需要频繁集合通信，所以通常优先在高速互联的单节点内使用。

示意：

```text
W = [W1 W2]
GPU0 计算 XW1
GPU1 计算 XW2
→ concat / all-reduce
```

关键：

- 切的是同一层 tensor；
- 通信发生频繁；
- NVLink/NVSwitch 等高速互联很重要；
- TP degree 过大可能通信压过计算。

对于 Attention，常按 head 切分；需要保证 head 数与 TP degree 兼容，GQA 的 KV heads 还会影响切分策略。

---

### 5.6 Pipeline Parallel

#### 30 秒标准答案

> Pipeline Parallel（流水线并行）把不同层放在不同 GPU，micro-batch 像流水线一样依次经过各 stage。它能放下超深模型、跨节点通信量相对可控，但存在 pipeline bubble、负载不均和调度复杂度。

```text
GPU0: layers 0-9
GPU1: layers 10-19
GPU2: layers 20-29
GPU3: layers 30-39
```

为减少空闲，输入拆成多个 micro-batch。问题：

- pipeline warmup/drain bubble；
- stage 计算不均；
- activation 需要跨 stage 传输；
- 多种 1F1B / interleaved schedule；
- batch 太小时利用率差。

---

### 5.7 ZeRO-1、ZeRO-2、ZeRO-3

ZeRO（Zero Redundancy Optimizer）的第一性目标是消除 Data Parallel 中每卡重复保存的训练状态。

| Stage | 分片对象 | 每卡仍复制 |
|---|---|---|
| ZeRO-1 | optimizer states | 参数、梯度 |
| ZeRO-2 | optimizer states + gradients | 参数 |
| ZeRO-3 | optimizer states + gradients + parameters | 需要时 all-gather 完整参数片段 |

假设 data parallel world size 为 `N`，被分片状态理想情况下可约缩到 `1/N`，但实际还有通信 buffer、临时 all-gather、碎片和不均匀分片。

#### Stage 越高为什么不一定越快

- 分片越彻底，通信和调度越多；
- ZeRO-3 前向/反向需要按层 all-gather 参数；
- 小模型或慢网络下，节省显存可能换来吞吐下降；
- 最合适 stage 取决于“是否装得下”与网络。

---

### 5.8 FSDP

#### 30 秒标准答案

> FSDP（Fully Sharded Data Parallel，全分片数据并行）在数据并行 worker 间分片参数、梯度和 optimizer states。计算某模块前 all-gather 参数，反向后 reduce-scatter 梯度并重新分片。概念上与 ZeRO-3 接近，但 API、模块 wrapping、state dict 和运行时实现属于 PyTorch 体系。

关键数据流：

```text
sharded parameters at rest
→ forward 前 all-gather 当前模块参数
→ 计算
→ 可 reshard
→ backward 需要时再 gather
→ gradients reduce-scatter
→ optimizer 更新本地 shard
```

#### FSDP 与 DDP

- DDP：每卡完整模型，all-reduce gradients；
- FSDP：训练状态分片，计算时临时聚合。

#### Auto wrap 的意义

分片粒度太大：

- 峰值 all-gather 高；
- overlap 较差。

粒度太小：

- collective 次数太多；
- launch overhead 大。

通常按 Transformer block wrap 是常见起点，但需要 profiling。

---

### 5.9 CPU Offload

把参数、optimizer states 或 KV/activation 的一部分放到 CPU 内存，在需要时传入 GPU。

优点：

- GPU 显存不够时可运行；
- 允许更大模型或 batch。

代价：

- PCIe/NVLink-C2C 带宽远低于 GPU HBM；
- 数据搬运可能成为瓶颈；
- CPU 内存和 pinned memory 压力；
- optimizer step 可能变慢；
- 与 accumulation、checkpoint 等组合有实现限制。

正确回答：

> Offload 首先解决 capacity，不一定提升 speed。若模型本来能在 GPU 装下，盲目 offload 往往变慢。

---

### 5.10 3D 并行怎么选

3D Parallelism 通常指：

```text
Data Parallel
× Tensor Parallel
× Pipeline Parallel
```

有时再结合：

- Sequence Parallel；
- Expert Parallel；
- Context Parallel；
- ZeRO/FSDP；
- CPU/NVMe offload。

#### 选择思路

1. **单卡能装下完整训练状态**：DDP 最简单；
2. **完整模型能装，optimizer/gradient 太大**：ZeRO/FSDP；
3. **单层或完整参数都放不下**：TP；
4. **层数多、跨节点**：PP；
5. **MoE**：增加 expert parallel；
6. **超长序列**：sequence/context parallel。

实际先问：

- GPU 型号和 HBM；
- 节点内 NVLink/NVSwitch；
- 节点间 InfiniBand 带宽；
- 模型层数、hidden、heads、experts；
- sequence length；
- 吞吐目标和 checkpoint 约束。

不能背“ZeRO 一定优于 TP”或“TP 只适合 NVLink”。它们解决的切分维度不同，常组合使用。

---

### 5.11 Sequence Parallel 与 Context Parallel

#### Sequence Parallel

把某些原本在每个 TP rank 重复的 sequence 维度 activation 切分，常用于 Norm、dropout 等区域，降低 activation 冗余。

#### Context Parallel

把超长序列的 token 维度分到不同设备，让每卡只持有部分上下文，再通过 ring/all-gather 等方式完成 Attention 所需的信息交换。

区别需结合具体框架定义；面试不要把二者说成统一标准 API。核心共同点：

> 当模型维度切分已不足以解决长序列 activation/attention 压力时，再沿 sequence/context 维切分。

---

### 5.12 长上下文训练的成本

设序列长度从 `n` 增加到 `2n`：

- 线性层 token 计算约变 2 倍；
- 标准全 Attention 的 pairwise 计算约变 4 倍；
- KV/普通 token activation 约变 2 倍；
- 数据 batch 往往需要下降；
- 有效训练 token 数和优化配方也变化。

因此“把 max_length 改大”不是完整长上下文训练：

- 位置编码需适配；
- 数据需要真实长依赖；
- packing 和 document mask；
- FlashAttention；
- checkpointing；
- context parallel；
- 长上下文评测；
- 防止短任务能力退化。

#### Packing

把多个短文拼进一条长序列提高 token 利用率，但必须：

- 用 document boundary mask 防止跨文档错误注意；
- 正确处理 position id；
- 正确处理 EOS；
- 避免 label 泄漏。

---

### 5.13 显存估算面试例题

#### 例 1：7B BF16 只做推理，为什么 16GB 卡仍可能不够

```text
weights ≈ 14GB
+ KV Cache
+ CUDA context
+ temporary workspace
+ fragmentation
+ logits / sampling buffer
```

所以理论权重刚好小于 16GB 仍不代表可运行。

#### 例 2：为什么 batch 和 context 都会吃显存

- batch 增加：并发序列数变多，activation/KV 都增加；
- context 增加：每条序列状态变长；
- 两者相乘决定大量运行时状态。

#### 例 3：Gradient Checkpointing 和 ZeRO 是否解决同一问题

- Checkpointing：主要压 activation；
- ZeRO/FSDP：主要压训练状态冗余；
- 两者正交，可组合。

#### 例 4：量化能否用于全量训练

低比特权重可用于某些量化训练方法，但普通 PTQ 量化模型不能直接视为稳定的全量训练方案。QLoRA 的关键是：

- 量化 base frozen；
- adapter 在较高精度训练；
- 不是直接对所有 4-bit 离散权重做普通 AdamW 更新。

---

### 5.14 与金融 Agent 的真实边界

你的项目是模型能力的消费与编排系统，不是基础模型训练平台：

- 没有证据表明执行过多机 3D parallel 训练；
- 没有证据表明使用 ZeRO/FSDP 训练金融模型；
- 没有维护训练集群或 checkpoint pipeline；
- 当前价值主要在数据、检索、证据、路由、评测和降级。

可以这样把知识迁移到项目：

> 如果未来需要本地部署或微调，我会先按权重、KV Cache、activation 和训练状态分别核算显存，再决定 QLoRA、FSDP 或推理量化，而不是只看模型参数量。当前项目优先调用外部或现成模型，因为核心需求是最新事实和可追溯证据。

---

## 6. P1 详解四：推理、KV Cache、量化与 Serving

### 6.1 Prefill 与 Decode

#### 30 秒标准答案

> LLM 推理分 Prefill 和 Decode。Prefill 一次处理整段 prompt，生成各层 KV Cache，矩阵较大、并行度高，通常更偏计算密集；Decode 每步只输入新 token，读取全部历史 KV 并生成一个 token，矩阵较小、并行度低，常更受显存带宽和 KV Cache 访问限制。

#### Prefill

输入 `n` 个 prompt token：

```text
prompt
→ embedding
→ 所有 Transformer layers
→ 为每层生成 n 个 token 的 K/V
→ 得到最后位置 logits
```

特点：

- token 可并行计算；
- Attention 对 prompt 长度有二次部分；
- 大矩阵乘法较容易吃满 GPU；
- 决定 TTFT 的重要部分。

#### Decode

每一步：

```text
new token
→ 计算该 token 的 Q/K/V
→ Q 与历史所有 K 做 attention
→ 读取历史 V
→ 输出 logits
→ sampling 得到下一个 token
→ 新 K/V 追加到 cache
```

特点：

- 一次通常只处理每条序列的 1 个 token；
- 必须顺序进行，无法并行生成未来 token；
- 需反复读取模型权重和历史 KV；
- 高并发 batching 才能提高 GPU 利用率。

#### 为什么优化方向不同

- Prefill：chunked prefill、FlashAttention、计算并行；
- Decode：continuous batching、KV 管理、GQA/MQA/MLA、量化、speculative decoding。

---

### 6.2 KV Cache 原理与公式

#### 为什么需要缓存

没有 KV Cache 时，生成第 `t` 个 token 会重复计算前 `t-1` 个 token 的 K/V，浪费巨大。因为历史 token 的隐藏表示在固定层和固定上下文下不变，可以缓存。

#### 粗略显存公式

对 decoder-only 模型：

```text
KV bytes
≈ 2
× num_layers
× batch_or_concurrent_sequences
× cached_tokens_per_sequence
× num_kv_heads
× head_dim
× bytes_per_element
```

开头的 `2` 表示 Key 和 Value。

若请求长度不同，真实值应对每条序列的已缓存 token 求和，并考虑：

- beam / parallel samples；
- block padding；
- speculative tokens；
- prefix sharing；
- cross-attention cache；
- scale metadata；
- runtime fragmentation。

#### 示例

假设：

```text
layers = 32
tokens = 4096
kv_heads = 8
head_dim = 128
dtype = BF16 = 2 bytes
batch = 1
```

```text
KV ≈ 2×32×4096×8×128×2
   ≈ 512 MiB
```

并发 32 条、上下文都接近 4096 时，仅 KV 理论值约 16 GiB。说明 serving 不能只看权重。

#### MHA/MQA/GQA/MLA 影响

- MHA：`num_kv_heads = num_query_heads`；
- GQA：KV heads 减少到分组数；
- MQA：KV heads = 1；
- MLA：缓存低维 latent 与必要的位置相关分量，公式依架构。

所以 GQA/MQA 不只降低容量，也降低 decode 每步读取 KV 的带宽。

---

### 6.3 TTFT、TPOT、吞吐和端到端延迟

#### TTFT

TTFT（Time To First Token，首 token 延迟）：

```text
排队
+ tokenization
+ scheduling
+ prefill
+ 第一次 sampling
```

长 prompt 通常显著增加 TTFT。

#### TPOT / ITL

TPOT（Time Per Output Token，每输出 token 时间）或 ITL（Inter-Token Latency，token 间延迟）主要反映 decode 速度。

#### 端到端延迟

近似：

```text
E2E latency
≈ TTFT + output_tokens × TPOT
```

更精确时是首 token 后剩余 token 数。

#### 吞吐

常见：

- requests/s；
- input tokens/s；
- output tokens/s；
- total tokens/s。

必须注明口径，因为 prefill token 和 decode token 的计算特性不同。

#### 延迟与吞吐冲突

更大的 batch：

- GPU 利用率和吞吐上升；
- 请求可能排队更久；
- 单请求 latency 可能上升。

生产系统要看 SLO：

- p50/p95/p99 TTFT；
- p95 TPOT；
- 满载吞吐；
- 拒绝率；
- 成本/token。

---

### 6.4 Static Batching 与 Continuous Batching

#### Static Batching

等一批请求凑齐，一起生成到全部结束。短请求完成后仍可能等待最长请求，GPU slot 被浪费。

#### Continuous Batching

也叫 iteration-level batching。每个 decode iteration：

- 完成的请求立即移出；
- 新请求可加入；
- batch 组成动态变化；
- scheduler 在 prefill/decode 之间分配 token budget。

收益：

- 减少空闲 slot；
- 提升并发吞吐；
- 更适合请求长度不一致的在线服务。

代价：

- 调度更复杂；
- KV Cache 动态管理；
- 高负载下 TTFT 与 TPOT 要平衡；
- chunked prefill 可能影响 decode 抖动。

---

### 6.5 PagedAttention

#### 30 秒标准答案

> PagedAttention 借鉴虚拟内存分页，把每个请求逻辑连续的 KV Cache 拆成固定大小 block，物理显存可以非连续分配。这样能减少预留和碎片，支持动态增长、共享前缀和更高并发。它主要是 KV Cache 内存管理方法，不等于把 Attention 的理论计算复杂度降为线性。

#### 为什么传统连续分配浪费

请求最大长度未知。若提前按最大长度预留：

- 大量内部浪费；
- 并发下降。

若需要连续扩容：

- 搬移成本高；
- 外部碎片。

分页后：

```text
logical KV blocks for request A:
[0][1][2][3]

physical GPU blocks:
[7][21][4][18]
```

通过 block table 映射。

#### 与操作系统分页的不同

这是思想类比。GPU KV block 管理、attention kernel 和 swap/offload 策略由推理引擎实现，不等于直接调用 OS 虚拟内存机制。

---

### 6.6 Prefix Caching

#### 原理

若多个请求共享完全相同的 token prefix：

```text
[system prompt + 长文档] + question A
[system prompt + 长文档] + question B
```

可复用 prefix 对应的 KV Cache，避免重复 prefill。

#### 适合你的金融场景

- 同一份年报被连续追问；
- 固定 system prompt 和工具说明；
- 同一主题研究包上问多个问题；
- 多轮会话中前缀不变。

#### 关键限制

- 必须是 token 级前缀相同，不是“语义相似”；
- 只能减少共享前缀的 prefill 计算；
- 不会加速新生成 token 的 decode；
- 缓存会占显存，需要 eviction policy；
- prompt 中时间戳、随机 ID、证据顺序变化会破坏命中率。

工程启示：

> 稳定、规范化 prompt 不只是方便评测，也有利于 prefix cache 命中。

---

### 6.7 Speculative Decoding

#### 30 秒标准答案

> Speculative Decoding 用较小 draft model 或其他轻量方法一次提出多个候选 token，再由目标模型并行验证。只接受与目标模型分布一致的部分，因此在正确实现下不必改变目标分布。收益取决于接受率、draft 成本和验证 kernel；不是任何模型都加速。

#### 数据流

```text
draft model 先生成 k 个候选
→ target model 一次并行验证
→ 接受连续通过的 token
→ 在首次拒绝处按 target 分布修正
→ 重复
```

为什么可能更快：

- 原本 target 每次 forward 只得到 1 个 token；
- 现在一次 target 验证可能接受多个 token；
- 以更多单次计算换更少串行步骤。

#### 影响因素

- draft 与 target 越一致，acceptance rate 越高；
- draft 太大则自身成本高；
- batch 很大时 target 本已高利用率，收益可能下降；
- 采样温度越高，候选更难命中；
- 额外 KV、树候选和调度有内存开销。

EAGLE、MTP、n-gram speculation 等属于不同 draft 机制，不应混为一个固定算法。

---

### 6.8 Sampling：Temperature、Top-k、Top-p

模型输出 logits `z_i`。

#### Temperature

```text
p_i = softmax(z_i / T)
```

- `T < 1`：分布更尖，稳定保守；
- `T > 1`：分布更平，随机多样；
- `T → 0`：接近 greedy，但实现通常单独处理。

Temperature 不会给模型增加知识，只改变采样分布。

#### Top-k

只保留概率最高的 k 个 token，重新归一化。

- 固定候选数；
- 在分布很尖或很平时不自适应。

#### Top-p / Nucleus Sampling

按概率从高到低累计，保留累计概率达到 `p` 的最小集合。

- 候选数随分布自适应；
- 常用于开放生成。

#### Repetition Penalty

降低已出现 token 或 n-gram 的再次概率，可缓解复读。但过强会：

- 破坏必须重复的公司名和数字；
- 让措辞不自然；
- 不能修复训练或 prompt 的根因。

#### 金融回答建议

- 事实抽取、JSON、工具调用：低温或 greedy，更重确定性；
- 开放式 brainstorming：可适度提高温度；
- 高风险结论：多采样不是事实校验，应回到证据和规则；
- 固定随机种子也不等于跨硬件、框架绝对复现。

---

### 6.9 Greedy、Beam Search 与 Sampling

#### Greedy

每步选概率最大 token：

- 快、确定；
- 局部最优不保证全局序列概率最高；
- 容易单调或重复。

#### Beam Search

保留 top-B 条候选序列：

- 适合翻译等目标较确定的任务；
- 计算和 KV Cache 约随 beam 扩大；
- 开放对话中可能更模板化；
- 长度惩罚影响大。

#### Sampling

按概率采样：

- 产生多样结果；
- 适合创作和候选生成；
- 事实任务需外部校验。

Agent 工具调用通常偏 greedy/低温；研究假设生成可多样采样，但最终答案必须走证据门。

---

### 6.10 量化的三个问题：量化什么、何时量化、怎么计算

#### 量化对象

- Weight-only：W8A16、W4A16；
- Weight + Activation：W8A8、FP8 W8A8；
- KV Cache quantization；
- optimizer states；
- training-aware quantization。

`W4A16` 表示权重 4-bit，activation/计算路径通常更高精度。

#### 何时量化

- PTQ（Post-Training Quantization）：训练后量化；
- QAT（Quantization-Aware Training）：训练中模拟量化误差；
- 在线量化：加载时动态转换；
- 预量化 checkpoint：离线校准后保存。

#### 基本映射

将浮点数映射到整数：

```text
q = clamp(round(x / scale) + zero_point)
x_hat = scale × (q - zero_point)
```

可按：

- per-tensor；
- per-channel；
- per-group；
- 对称/非对称。

group 更小通常精度更好，但 scale metadata 和 kernel 开销更高。

---

### 6.11 INT8、INT4、FP8 的权衡

#### INT8

- 容量约为 FP16 权重一半；
- W8A8 可利用整数矩阵乘；
- activation outlier 处理很重要；
- 精度通常较稳，但速度依硬件/kernel。

#### INT4

- 权重容量约为 FP16 的四分之一；
- 常见 weight-only；
- 对 group size、校准和 kernel 更敏感；
- 适合容量受限和单机部署；
- 反量化开销可能限制速度。

#### FP8

- 浮点格式保留指数结构；
- 适合支持 FP8 Tensor Core 的新硬件；
- 可量化 weights、activations、KV；
- 需要 scale recipe；
- 旧 GPU 不能因为文件是 FP8 就获得原生加速。

#### 必考纠错

> 低比特一定减少存储，但不保证端到端更快。真实速度取决于硬件原生指令、矩阵形状、batch、反量化融合、kernel、内存带宽和未量化算子。

---

### 6.12 GPTQ、AWQ、GGUF、Marlin

#### GPTQ

GPTQ 是训练后 weight-only 量化家族，通常逐层/逐块利用校准数据和近似二阶信息，尽量降低量化引入的输出误差。

特点：

- 常见 4-bit；
- 需要校准；
- 有大量预量化模型；
- 速度取决于对应 runtime/kernel。

#### AWQ

AWQ（Activation-aware Weight Quantization）利用 activation 统计识别重要权重通道并做缩放/保护，目标是在低比特下保持精度。

特点：

- 常见 W4A16；
- 需要代表性校准数据；
- 适配高性能 kernel 时可加速；
- 校准分布不匹配会影响质量。

#### GGUF

GGUF 更准确地说是 llama.cpp 生态常用的模型文件格式/容器，支持多种量化类型和 metadata，适合 CPU、Apple Silicon 和本地混合推理。它不是一个单独量化数学算法。

#### Marlin

Marlin 是面向特定低比特权重的高性能 GPU kernel/执行方案。它说明：

> “量化方法”和“让量化模型真正跑得快的 kernel”是两层问题。

#### 选择建议

- 快速 QLoRA：bitsandbytes/NF4 生态；
- GPU 4-bit serving：看引擎支持的 AWQ/GPTQ/Marlin；
- 本地 CPU/Mac：GGUF/llama.cpp；
- 新 NVIDIA GPU 高吞吐：评估 FP8；
- 最终必须在目标模型、目标硬件和真实请求上 benchmark。

---

### 6.13 CPU 与 GPU 推理

#### GPU

适合：

- 大吞吐；
- 低延迟；
- 较大 batch；
- FP16/BF16/FP8/INT8 Tensor Core；
- 多并发服务。

限制：

- HBM 昂贵；
- 运维和功耗；
- 模型需适配多卡和 kernel。

#### CPU

适合：

- 小模型或低并发；
- 成本敏感；
- 数据不能离开本机；
- GGUF 低比特；
- prompt 不长、延迟要求不极端。

限制：

- 内存带宽通常低于 GPU HBM；
- 大模型每 token 需读取大量权重；
- 延迟和吞吐可能较差。

#### Apple Silicon / 统一内存

可运行较大低比特模型，开发体验和隐私好；但统一内存容量不等于高端数据中心 GPU 的吞吐，仍受带宽、kernel 和并发限制。

#### 选择公式

不要只问“模型能否装下”，还要问：

```text
目标 p95 latency
并发数
输入/输出 token 分布
每天 token 量
硬件成本和利用率
数据隐私
运维能力
```

---

### 6.14 vLLM、SGLang、TensorRT-LLM、LMDeploy

#### vLLM

定位：通用、高吞吐、OpenAI-compatible 的开源 LLM serving engine。

常见能力：

- PagedAttention；
- continuous batching；
- prefix caching；
- chunked prefill；
- speculative decoding；
- 多种量化；
- tensor/pipeline parallel；
- LoRA serving。

适合：快速搭建通用模型服务、模型生态广、吞吐优先。

#### SGLang

定位：高性能 serving runtime + 面向复杂生成程序/结构化调用的生态。

常见能力：

- Radix/Prefix cache 思路；
- continuous batching；
- speculative decoding；
- 多种 attention backend 和量化；
- tensor/data/expert parallel；
- structured output、复杂 LLM program 优化。

适合：复杂 Agent workload、前缀复用高、需要细粒度 runtime 控制。

#### TensorRT-LLM

定位：NVIDIA GPU 上的高性能编译和推理栈。

特点：

- 深度利用 TensorRT/CUDA kernel；
- FP8/INT8/INT4 等 NVIDIA 优化；
- inflight batching、KV 管理、多 GPU；
- 为特定模型和硬件调优可获得很高性能。

代价：

- NVIDIA 绑定更强；
- 构建 engine、版本兼容和部署复杂度较高；
- 自定义模型适配成本可能高。

#### LMDeploy

定位：开源大模型部署工具链，提供高性能推理后端、量化和服务接口，在中文模型生态中常见。

适合：

- 快速部署支持列表内模型；
- TurboMind/PyTorch backend；
- 量化与 OpenAI-compatible 服务。

#### 不能做的“排行榜回答”

不要说“vLLM 一定最快”：

- 模型架构不同；
- 输入输出长度不同；
- batch/concurrency 不同；
- GPU 不同；
- 量化不同；
- structured decoding、LoRA、speculation 支持不同。

标准选型流程：

```text
先定义 workload 和 SLO
→ 筛选模型/量化/硬件支持
→ 用真实 trace benchmark
→ 比 p95 latency、throughput、memory、稳定性和运维成本
```

---

### 6.15 Chunked Prefill 与 Prefill/Decode 调度

长 prompt 的 prefill 如果一次独占 GPU：

- 其他 decode 请求 token 间延迟抖动；
- TTFT 排队；
- batch token budget 难平衡。

Chunked Prefill 把长 prompt 拆为若干 chunk，与 decode iteration 混排：

优点：

- 更平滑调度；
- 控制单轮 prefill token 量；
- 改善 decode latency。

代价：

- 调度和 kernel launch 增加；
- TTFT 可能因分片和让路变长；
- 最优 chunk size 依 workload。

生产 serving 不只是“模型 forward 更快”，而是一个排队与资源调度问题。

---

### 6.16 金融 Agent 的推理选型

#### 当前真实实现

- Workbench 通过可选 LLM 配置做回答精修；
- 无可用 LLM key 时可降级为结构化模板/确定性输出；
- 事实来源是 DuckDB、知识库和关系数据；
- 没有证据表明当前生产使用 vLLM、SGLang、TensorRT-LLM 或 LMDeploy；
- 没有证据表明已部署 GPU 集群、量化模型或 speculative decoding。

#### 面试正确说法

> 当前项目把模型调用封装成可选生成层，优先保证无模型或模型失败时仍能输出结构化结果。如果未来本地化部署，我会先测 workload：金融问答通常 prompt 较长、输出中等、同一报告可能被多次追问，因此 prefix caching 和 chunked prefill 可能有价值；若并发上升，再比较 vLLM 和 SGLang。是否量化要在真实金融问答与结构化 tool call 集上验证，不能只看通用 benchmark。

#### 一个合理容量规划例子

先记录一周 trace：

- prompt p50/p95 tokens；
- output p50/p95 tokens；
- 峰值并发；
- 相同 prefix 比例；
- quick/deep 模式占比；
- 可接受 TTFT/TPOT。

再选择：

```text
模型大小
→ 精度/量化
→ 单卡或多卡
→ serving engine
→ max model length
→ concurrency/token budget
→ prefix cache
→ benchmark
```

这比先说“我要上 vLLM”更像真实工程决策。

---

### 6.17 推理高频追问与纠错

1. **KV Cache 是否缓存所有 hidden state？**
   主要缓存各层 Attention 的 K/V，不是把所有中间 activation 都保留用于反向。

2. **Prefix cache 是否对相似文档生效？**
   通常要求 token 前缀完全一致；语义相似不是 cache key。

3. **PagedAttention 是否让单请求算得更少？**
   主要减少 KV 浪费和碎片，支持高并发；不必然减少该请求所需 attention FLOPs。

4. **INT4 是否必然比 FP16 快 4 倍？**
   不。容量约四分之一是理论权重存储对比，端到端速度受反量化和 kernel 限制。

5. **TTFT 高应该只优化模型？**
   还要看排队、tokenization、prompt 长度、RAG、网络、scheduler 和 prefill。

6. **Speculative Decoding 是否改变答案？**
   严格接受/修正算法可保持目标分布；某些近似实现或配置可能改变输出，需要说明。

7. **金融任务温度应该设 0 吗？**
   结构化事实任务可低温，但事实正确性仍靠数据和校验；温度 0 不能消灭幻觉。

---

## 7. P1 面试速查表、项目映射与自测

### 7.1 一页公式速查

#### Attention

```text
Q = XW_Q, K = XW_K, V = XW_V
Attention(Q,K,V) = softmax(QK^T/sqrt(d_k) + Mask)V
```

```text
标准 Attention：
投影 O(nd²)
注意力 O(n²d)
注意力矩阵 O(n²)
```

#### 语言模型

```text
P(x_1...x_T) = ∏ P(x_t|x_<t)
L_NLL = -Σ log Pθ(x_t|x_<t)
PPL = exp(mean NLL)
```

#### LoRA

```text
W' = W + (α/r)BA
trainable params = r(d_in+d_out)
```

#### KV Cache

```text
KV bytes ≈
2 × layers × concurrent_sequences × cached_tokens
  × kv_heads × head_dim × bytes_per_element
```

#### 训练 Global Batch

```text
global_batch =
micro_batch_per_gpu
× accumulation_steps
× data_parallel_world_size
```

#### RRF（与你项目直接相关）

```text
RRF(d) = Σ 1/(k + rank_i(d))
```

---

### 7.2 概念对照速查

| 容易混淆 | 正确区分 |
|---|---|
| Self-Attention vs Cross-Attention | Q/K/V 同源 vs Q 与 K/V 不同源 |
| Causal Mask vs Prefix Tuning | 注意力可见性约束 vs PEFT 可学习前缀 |
| RoPE vs ALiBi | 旋转 Q/K vs logits 距离偏置 |
| MQA vs GQA | 1 组 KV vs 多组但少于 Q heads |
| FlashAttention vs PagedAttention | 优化 Attention IO vs 管理 KV blocks |
| Pretraining vs SFT | 原始文本语言建模 vs 指令示范 |
| DPO vs PPO | 离线偏好损失 vs 在线 rollout 强化学习 |
| LoRA vs QLoRA | 低秩 adapter vs 4-bit frozen base + LoRA |
| DDP vs FSDP | 每卡完整模型 vs 训练状态分片 |
| Checkpointing vs ZeRO | 压 activation vs 压训练状态冗余 |
| Quantization vs GGUF | 数值压缩方法 vs 模型文件格式/生态 |
| TTFT vs TPOT | 首 token 延迟 vs 后续 token 间延迟 |
| RAG freshness vs 模型知识 | 外部证据是否最新 vs 权重内统计知识 |

---

### 7.3 你的金融 Agent：技术能力矩阵

| 技术 | 当前项目状态 | 面试如何讲 |
|---|---|---|
| Transformer 基础模型训练 | 未实现 | 理解原理，消费现成模型能力 |
| Embedding | 已有 RAG 链路 | BGE dense 负责语义召回 |
| BM25 | 已实现 | `rank_bm25` + 自定义 tokenizer |
| Hybrid + RRF | 已实现 | BM25/dense 排名融合 |
| Cross-encoder rerank | 已实现代码链路 | 对候选页联合编码打分 |
| RAG freshness gate | 已实现 | stale/unknown 默认不得进严格证据 |
| LLM 回答精修 | 可选实现 | 无 key 时可降级 |
| SFT/LoRA/QLoRA | 未实现 | 未来只考虑格式、工具和行为适配 |
| RLHF/DPO/GRPO | 未实现 | 当前是系统层对齐，不是参数训练 |
| vLLM/SGLang serving | 未实现/未验证 | 可作为未来本地部署选型 |
| FP8/INT4 production | 未实现/未验证 | 必须在真实问答集 benchmark |
| FSDP/ZeRO 训练 | 未实现 | 能解释容量规划，但不能说有实战 |
| Agent Router | 已实现 | known/planner/data-gap/clarification |
| 风险门控 | 已实现一部分 | 低风险、置信度阈值、默认 preview |
| Output review | 已实现 advisory | 不是已验证自动裁判 |
| PIT/no-lookahead | 已有机制 | 历史回放只用当时可得信息 |

---

### 7.4 把 P1 技术自然接到项目，而不是硬贴

#### 问：你为什么没微调一个金融大模型？

> 我的目标是研究事实的时效性和可追溯性。行情、公告和产业证据变化快，把它们写进模型权重会更新慢、难引用，所以先选择 RAG + 结构化数据库。微调更适合稳定回答格式、工具调用和缺口表达；只有积累足够高质量失败样本并建立离线评测后，我才会考虑 LoRA/SFT。

#### 问：如果未来本地部署，你怎么选推理框架？

> 先采集真实 workload，包括 prompt/output 长度、峰值并发、重复 prefix 和 TTFT/TPOT SLO。这个项目可能是长 prompt、中等输出、同一研报多轮追问，因此 prefix caching 和 chunked prefill 值得测。然后在目标硬件上比较 vLLM 与 SGLang，而不是先凭框架名做决定。

#### 问：INT4 会不会影响金融回答？

> 可能。金融任务对数字、代码、结构化 tool call 和细粒度事实区分敏感。我会分别测检索后回答忠实度、引用正确率、数值抽取、JSON 合法率和延迟，而不是只看通用 benchmark。低比特先保证容量，速度和质量要实测。

#### 问：你项目中的“对齐”是什么？

> 不是 RLHF，而是系统层对齐：把事实源外置，用户记忆只当 prior，RAG 过期证据禁止进入严格回答，回答必须暴露反证和数据缺口，再做 claim-level fidelity 与 output review。它不更新模型参数，但能约束系统行为。

#### 问：长上下文模型能否把整个知识库塞进去？

> 不能把“能放下”等同于“能可靠利用”。全塞会增加 TTFT、成本和干扰，也缺乏新鲜度、权限和引用治理。我的系统仍先检索和精排，只把少量高质量证据给模型；长上下文用于保留更完整的候选材料，而不是替代 RAG。

---

### 7.5 20 道口头自测题

先用 30 秒回答，再检查是否包含“原理—权衡—项目边界”。

1. 为什么 Attention 要除以 `sqrt(d_k)`？
2. Attention 的 `O(n²)` 到底来自哪一步？
3. Multi-Head 为什么比单头更有表达力？
4. Decoder-only 训练为什么能并行，推理却不能并行生成未来 token？
5. RoPE 为什么能表达相对位置？
6. RoPE scaling 为什么不等于可靠长上下文？
7. Pre-LN 为什么通常更容易训练深层模型？
8. SwiGLU 比普通 FFN 多了什么？
9. MHA、MQA、GQA 如何影响 KV Cache？
10. FlashAttention 与 PagedAttention 有什么本质区别？
11. MoE 为什么总参数大但活跃计算小？最大工程难点是什么？
12. SFT 和预训练损失看似相同，为什么效果目标不同？
13. RLHF 中 policy、reference、reward、critic 各做什么？
14. DPO 为什么能不训练显式 Reward Model？它损失了什么能力？
15. LoRA 具体省了哪些显存，哪些没有省？
16. 为什么 QLoRA 不一定比 LoRA 更快？
17. ZeRO-3/FSDP 与 Gradient Checkpointing 分别解决什么？
18. Prefill 和 Decode 分别受什么限制？
19. 为什么 INT4 权重只有约四分之一，不代表速度四倍？
20. 你的金融 Agent 实际用了哪些 P1 技术，哪些只是未来选型？

---

### 7.6 8 道白板计算题

#### 题 1

`d_model=4096` 的标准 MHA，忽略 bias，Q/K/V/O 投影约多少参数？

答案：

```text
4 × 4096² ≈ 67.1M
```

#### 题 2

序列长度从 4K 变 8K，标准 Attention score 数量变几倍？

答案：约 4 倍；线性层 token 计算约 2 倍。

#### 题 3

一个 7B BF16 模型权重理论占多少？

答案：约 14GB 十进制；不含 KV、workspace 和碎片。

#### 题 4

LoRA 对一个 `4096×4096` 矩阵使用 `r=8`，可训练参数多少？

答案：

```text
8×4096 + 4096×8 = 65,536
```

原矩阵：

```text
4096² = 16,777,216
```

约为原矩阵的 0.39%。

#### 题 5

32 层、8 KV heads、head_dim 128、4096 tokens、BF16、batch 1，KV 约多少？

答案：约 512MiB。

#### 题 6

每卡 micro-batch 2，8 卡 DP，accumulation 16，global batch 多少条序列？

答案：

```text
2×8×16 = 256
```

#### 题 7

为什么 Adam mixed-precision 常粗估 16 bytes/param？

答案：2B 参数 + 2B 梯度 + 4B master weight + 4B m + 4B v；实现可能不同。

#### 题 8

GQA 从 32 个 KV heads 减到 8 个，其他不变，KV Cache 理论变为多少？

答案：约原来的 1/4。

---

### 7.7 典型错误答案纠正

| 错误说法 | 更准确说法 |
|---|---|
| Decoder-only 理论上永远最优 | 它对通用生成高效统一，但架构选择依任务 |
| FlashAttention 将复杂度降到 O(n) | 它主要减少 IO/显存，精确全注意力 FLOPs 仍近似二次 |
| DPO 不需要 Reward Model，所以没有奖励 | 它把隐式 reward/preference 关系写入直接优化目标 |
| GRPO 不需要任何其他模型 | 它省 critic，但仍需 policy、采样和 reward，可能还有 reference/KL |
| LoRA 训练时间一定远小于全参 | 状态和通信省很多，但主模型前反向仍执行 |
| BF16 比 FP16 全面更精确 | BF16 范围大，FP16 尾数精度更高；稳定性配方不同 |
| INT4 一定最快 | 低存储不等于 kernel/端到端最快 |
| vLLM 只支持 PagedAttention | 现代 vLLM 还有 continuous batching、prefix caching、量化等 |
| 长上下文替代 RAG | 长窗口不解决新鲜度、引用、权限和噪声 |
| output review 就是 RLHF | 没有用反馈更新 policy 参数就不是 RLHF |

---

### 7.8 建议的 7 天 P1 复习法

**Day 1：Transformer 数据流**
手画一层 Decoder：Norm → QKV → Masked Attention → Residual → FFN → Residual。

**Day 2：位置与 Attention 优化**
推导 `sqrt(d_k)`、RoPE 相对位置；口述 MHA/MQA/GQA 和 FlashAttention。

**Day 3：训练流水线**
讲清 Pretraining → SFT → preference alignment；对比 PPO/DPO/GRPO。

**Day 4：LoRA 与训练稳定性**
白板写 LoRA 维度和参数量；复习 AdamW、warmup、BF16、checkpointing。

**Day 5：显存与分布式**
做 7B/14B 权重和 Adam 粗估；讲 DDP、TP、PP、ZeRO、FSDP。

**Day 6：推理与量化**
讲 Prefill/Decode、KV 公式、TTFT/TPOT、PagedAttention、INT4/FP8。

**Day 7：项目模拟面试**
每道题最后必须加一句：“我的项目已实现什么、没实现什么、为什么这样选。”

---

## 8. 项目故事 STAR 模板

### 故事 1：从“会聊天”到“可审计金融研究 Agent”

S：金融问答容易出现看似合理但无证据的结论。
T：让 Agent 输出可追溯、可降级、可复验的研究回答。
A：设计多源检索 `[S/G/R/W/M]`，引入证据分层、反证、缺口、output review、claim fidelity。
R：系统从“生成答案”升级成“带证据、带边界、可审稿的研究工作台”。
边界：尚未证明预测更准，主要提升可审计性。

### 故事 2：知识库 RAG 从单向量召回升级成 Hybrid

S：金融术语、股票代码、同义概念混杂，单一检索容易漏。
T：提升召回覆盖并保持可解释。
A：BM25 + BGE dense + RRF + exact boost + wikilink neighbor + rerank。
R：具备完整工程链路和 A/B 评测框架。
边界：真实收益还需可信人工标注 query set。

### 故事 3：Agent Memory 解决多工具上下文断裂

S：Codex、Claude、Devin 等多个 Agent 参与同一项目，偏好和交接容易丢。
T：构建跨 Agent 共享记忆底座。
A：Git + Markdown + YAML frontmatter + Obsidian，分层目录、frontmatter、writeback、lint。
R：换工具不丢上下文，人类可读，Git 可审计。
边界：不是强一致数据库，检索层仍在演进。

### 故事 4：金融回测防前视

S：历史研究容易把未来信息提前用于过去决策。
T：把“信息发生时间”和“系统可得时间”分开。
A：定义 `publish_time/available_time`，PIT 截断，快照回放，claim 级验证。
R：让系统能区分“事后正确解释”和“当时可做判断”。
边界：不是所有存量页面都已完成时间治理。

---

## 9. 面试中一定要诚实表达的限制

1. **这是个人金融研究系统，不是多人生产 SaaS。**
2. **Workbench 默认本地 `127.0.0.1`，没有生产级公网认证。**
3. **RAG 检索已实现工程链路，但 README 明确仍是 POC。**
4. **评测集还需要真实问题和人工校准。**
5. **output_review 是 advisory gate，不是已验证的自动裁判。**
6. **Temporal Facts 的 active/superseded/invalidated 时序边还在规划。**
7. **daily-loop 的完整“盘前预测→盘后验证→写回记忆”闭环尚未完全自动化。**
8. **记忆 prior 化和贝叶斯仲裁是正确方向，但 Workbench 仍有旧 synthesis 被直接引用的缺口。**

这种诚实不会减分，反而显得你真的做过工程。

---

## 10. 30 秒自我介绍项目版

> 我自己落地了一个 A 股金融研究 Agent。它的核心不是让大模型直接给投资结论，而是把本地 DuckDB 盘面数据、Markdown/Obsidian 知识库、结构化关系图谱、Hybrid RAG、用户经验记忆和回答质检组合起来。
> 技术上我重点做了三件事：第一，知识库侧实现 BM25 + dense embedding + RRF + rerank 的检索链路；第二，金融回答侧把事实、推演、预测分层，并用引用、反证、缺口和 claim-level fidelity 降低幻觉；第三，用 Git + Markdown 的 agent-memory 解决多 Agent 协作和长期记忆沉淀。
> 我会诚实区分已实现和未实现：现在它更像个人研究工作台，不是生产 SaaS；检索和评测框架已经具备，但真实效果还需要更可靠的人工标注集和历史盲测。

---

## 11. 下一步学习顺序

1. 先背熟 P0：Agent / Memory / RAG / Hybrid / rerank / 防幻觉 / 评测 / 无前视。
2. 每个题都按“四段法”回答：
   - 第一性原理；
   - 标准答案；
   - 我的项目怎么做；
   - 边界和改进。
3. 用本手册第 3—7 章系统复习 P1，不再只背缩写。
4. 做白板估算：Attention、LoRA 参数量、训练状态、KV Cache。
5. 最后做模拟面试：围绕你的项目连续追问，而不是孤立背题。

---

## 12. 口径校对参考

本扩展版以原始论文与当前官方文档的稳定概念为主，避免照抄 PDF 中的旧框架结论。建议面试前按目标公司的模型栈再查看最新版本：

- Transformer：<https://arxiv.org/abs/1706.03762>
- RoPE / RoFormer：<https://arxiv.org/abs/2104.09864>
- RMSNorm：<https://arxiv.org/abs/1910.07467>
- GLU/SwiGLU：<https://arxiv.org/abs/2002.05202>
- GQA：<https://arxiv.org/abs/2305.13245>
- FlashAttention：<https://arxiv.org/abs/2205.14135>
- LoRA：<https://arxiv.org/abs/2106.09685>
- QLoRA：<https://arxiv.org/abs/2305.14314>
- DPO：<https://arxiv.org/abs/2305.18290>
- PyTorch FSDP2：<https://docs.pytorch.org/docs/stable/distributed.fsdp.fully_shard.html>
- NVIDIA 混合精度 / FP8：<https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/>
- vLLM：<https://docs.vllm.ai/>
- SGLang：<https://docs.sglang.io/>
- Hugging Face 量化选型：<https://huggingface.co/docs/transformers/en/quantization/selecting>

版本敏感提醒：

- serving 框架支持的模型、量化和硬件变化很快；
- FP8/INT4 是否加速必须以目标 GPU 和 kernel 为准；
- GRPO、RLVR、speculative decoding 变种较多，回答时先说明所指论文或实现；
- 不要把官方 feature list 等同于你在项目中实际启用和验证过。

---

## 13. V3 阅读方式：从“知道术语”升级到“讲清为什么这样实现”

V2 解决的是大模型基础知识问题；V3 解决的是项目深挖问题。

面试官问你的项目时，真正想判断的通常不是你能否说出 RAG、Agent、Memory、DuckDB，而是：

1. 你遇到的业务问题是什么；
2. 为什么一次 LLM 调用解决不了；
3. 哪些环节应该确定性执行，哪些环节可以交给概率模型；
4. 为什么选当前方案，而不是另一种常见方案；
5. 真实代码在哪里，输入和输出是什么；
6. 数据缺失、检索失败、模型失败时如何处理；
7. 如何知道系统比原来更好；
8. 哪些已经实现，哪些只是 POC、设计或下一步。

本章之后每项技术都尽量按同一套结构讲：

```text
业务问题
→ 第一性原理
→ 技术选型
→ 架构与模块边界
→ 真实代码实施
→ 输入输出与数据流
→ 异常和降级
→ 评测与证据
→ 当前实现边界
→ 30 秒答案 / 2 分钟答案 / 追问
```

### 13.1 你的系统不是一条“LLM 链”，而是四条彼此约束的链

```text
控制链
用户问题 → 澄清 → 路由 → QuestionPlan → 工具/数据块调度

证据链
S/G/R/W/M/V/D/L → evidence audit → 反证 → 引用 → claim lineage

生成链
AnswerSpec → 模板回答或可选 LLM synthesis → output review → 修订 → 校验

学习链
interaction → judgment/correction → checkpoint → verdict → experience card
```

四条链不能混为一谈：

- **控制链**决定“下一步做什么”；
- **证据链**决定“结论凭什么成立”；
- **生成链**决定“怎样表达且不越界”；
- **学习链**决定“下次能否减少同类错误”。

如果把它们全部交给一次自由生成，任何一步错误都会藏在一段流畅文本里，既难定位，也难回放。

### 13.2 确定性系统与概率模型的分工

| 问题 | 更适合的实现 |
|---|---|
| 股票代码、日期、表名、数据是否存在 | 确定性解析 / SQL / schema |
| 风险等级、是否允许自动执行 | 规则和门禁 |
| 索引是否新鲜、命令是否超时 | 程序检查 |
| 数字是否与来源一致 | claim-level 校验 |
| 用户到底想问什么 | 规则优先，必要时 LLM 辅助 |
| 多源证据如何组织为解释 | LLM 或模板 |
| 如何提出反证和后续验证点 | 规则骨架 + LLM 表达 |
| 最终语言是否清楚 | LLM 擅长 |

一句话：

> 把不能错、能形式化检查的部分交给程序；把开放语义理解和表达交给模型；模型输出再回到程序约束。

这也是整个金融 Agent 的主设计哲学。

---

## 14. 端到端实现总览：一个问题怎样穿过三仓

### 14.1 三个仓库的职责边界

```text
agent-memory
  跨 Agent 的长期协作记忆与方法论资产
  Git + Markdown + YAML frontmatter + Obsidian + hooks

knowledge-base-private
  原始材料、结构知识、关系、证据与派生 RAG 索引
  raw → source/concept/entity → relations → .rag_index

finance-workspace-private
  用户问答、路由、研究编排、市场数据、证据审计、输出质检、回放评测
  question_router → answer_orchestrator → ask → review/eval
```

它们不是三个重复的“知识库”：

- Agent Memory 保存的是**用户、项目和方法论的长期上下文**；
- Knowledge Base 保存的是**外部研究材料和结构化知识**；
- Finance Workspace 保存的是**运行时市场数据、控制逻辑和研究结果**。

### 14.2 主路径

以“某公司最近为什么强，逻辑是否可持续？”为例：

```text
1. 输入 query
2. clarify_for_query 检查空问题、歧义和缺参数
3. route_question 判断 known_workflow / planner / data_gap / clarification
4. plan_answer_question 生成 QuestionPlan
5. entity_anchor 解析公司、代码、题材和 graph_query
6. 读取 S：当前盘面候选和市场快照
7. 读取 G：实体—题材暴露关系
8. 读取 R：证据索引
9. 读取 W：narrow/broad/counter 闭环 RAG
10. 按问题类型决定是否补 D0-D9 结构化数据块
11. 可选读取 M：用户历史观点，只作为 prior
12. 可选读取 V：历史预测/回检
13. 可选运行 L：官方公告/互动平台等 L3 证据
14. audit_evidence_chain 做 L1/L2/L3/L4/E 分层
15. build_retrieval_telemetry 记录命中、延迟、降级、新鲜度
16. build_counterevidence_plan 生成反证与 T+1/T+3/T+5 验证
17. 构造 AnswerSpec
18. 默认模板或可选 LLM synthesis
19. review_output 按固定顺序审稿
20. WARN 时把问题回灌给 LLM 定向修订
21. validate_llm_answer 再校验修订结果
22. 输出结论、证据链、反证、缺口、验证点、telemetry、引用
23. 运行记录进入 trace；用户反馈进入 corrections/checkpoints/verdicts
```

### 14.3 一次请求中的核心对象

| 对象 | 作用 |
|---|---|
| `RouteDecision` | 决定走已知工作流、分析规划、数据缺口或澄清 |
| `QuestionPlan` | 规定问题类型、必看视角、检索计划、质量门、输出契约 |
| `EntityAnchor` | 把自然语言实体锚定为公司、ticker、概念和图谱查询 |
| `WikiRagResult` | W 源检索命中、warning 和 telemetry |
| `ClosedLoopRetrievalResult` | narrow/broad/counter 结果及分桶 |
| `EvidenceAudit` | 证据层、缺失层和结论口径 |
| `CounterEvidencePlan` | 最强反证、降级条件和验证排期 |
| `AnswerSpec` | 最终答案必须满足的结构和约束 |
| `ReviewResult` | PASS/WARN、检查明细和修订建议 |

### 14.4 为什么要有这些中间对象

如果只有一段 prompt：

```text
问题 + 一堆 context → LLM → answer
```

你无法回答：

- 路由为什么选择了这个工具；
- 哪个来源没命中；
- 哪条结论是用户记忆，哪条是当前事实；
- 索引是否过期；
- 是检索失败还是生成失败；
- 哪条 warning 导致了修订；
- 历史回放是否用了未来证据。

显式对象的价值是把隐式推理变成可观测状态。

---

## 15. Question Router：为什么先路由，而不是直接让 LLM 自由规划

真实代码：

- `finance-workspace-private/intelligence/services/question_router.py`
- `finance-workspace-private/intelligence/workflows/agent_orchestrator.py`

### 15.1 业务问题

金融工作台收到的问题跨度很大：

- “复盘今天市场”；
- “分析某家公司”；
- “这个题材有没有机会”；
- “帮我执行某个导入命令”；
- “这句话什么意思”；
- “我没有给日期，能不能回测”。

如果所有问题都让 LLM 自由生成计划，会出现：

1. 相同问题每次选不同路径；
2. 明明已有成熟 workflow，却重新发明工具链；
3. 缺参数时仍继续执行；
4. 高风险路径被模型误调用；
5. 路由难以单测；
6. 无法稳定统计各类请求的失败率。

### 15.2 第一性原理

路由的本质不是“让模型想得更聪明”，而是：

> 在一个有限能力集合中，选择满足前置条件且风险可控的下一步。

它更接近编译器前端或 API gateway，而不是开放式写作：

```text
自然语言
→ 识别意图、实体、日期、缺口
→ 映射到有限枚举
→ 产生可检查的执行计划
```

因此确定性规则应该优先处理：

- 空输入；
- 明显歧义；
- 已知触发词；
- 必填参数；
- 风险等级；
- 已注册 workflow。

Planner 只处理规则无法完全覆盖的开放分析问题。

### 15.3 技术选型

当前采用“规则注册表 + 轻量 Planner”的混合方式，而不是纯 LLM Router。

选择理由：

1. 已知工作流数量有限，规则命中更快、更便宜、更稳定；
2. 金融执行有副作用，不能只依赖模型置信；
3. `RouteDecision` 可以单测和记录；
4. 新增 workflow 时只需扩展 registry；
5. 长尾分析问题仍可进入 Planner，不被硬规则完全限制。

没有选择纯关键词路由，因为：

- “为什么涨”和“帮我复盘这个上涨”语义相近但表达多样；
- 实体、日期、目标可能组合出现；
- 长尾问题需要拆解。

没有选择纯 LLM function calling，因为：

- 输出仍可能缺参数或误选；
- 风险门禁不能由模型自证；
- 每次调用增加延迟和成本；
- 路由错误会污染后续全部检索。

### 15.4 真实数据结构

四种路由：

```python
ROUTE_KNOWN = "known_workflow"
ROUTE_PLANNER = "planner_analysis"
ROUTE_DATA_GAP = "data_gap"
ROUTE_CLARIFICATION = "clarification_needed"
```

入口：

```python
def route_question(
    query: str,
    registry: list[PathSpec] | None = None,
) -> RouteDecision:
```

`RouteDecision` 记录：

- `query`
- `route_type`
- `confidence`
- `selected_paths`
- `plan_steps`
- `missing_data_checks`
- `next_action`
- `warnings`

这使路由结果不是一句自然语言，而是下游可消费的协议。

### 15.5 真实路由行为

#### 空问题

```text
route_type = clarification_needed
confidence = 0.1
next_action = ask_user_to_clarify
```

原因：没有足够信息，最正确的行为不是猜。

#### 模糊问题

先调用 `clarify_for_query` 识别：

- 标的是谁；
- 日期是什么；
- 想要复盘、预测还是解释；
- 是快速回答还是深挖。

#### 显式数据缺口

命中 data-gap trigger 时：

```text
route_type = data_gap
```

下游优先检查数据，而不是让模型凭常识补全。

#### 分析型问题

“为什么”“怎么看”“有没有机会”等进入：

```text
route_type = planner_analysis
```

Planner 抽取实体、日期、目标并生成步骤。

#### 已知工作流

已知 trigger 命中：

```text
route_type = known_workflow
```

如果意图较弱，代码给出较低置信度，例如 `0.55`，并建议 preview，而不是直接执行。

### 15.6 与执行编排的连接

命令型路径由：

```python
run_agent_orchestrator(options)
```

管理。

关键配置：

```python
MIN_AUTO_EXECUTION_CONFIDENCE = 0.7
```

真正可自动执行必须同时满足：

```python
bool(item.argv)
and item.auto_execute
and item.risk_level == "low"
and confidence >= MIN_AUTO_EXECUTION_CONFIDENCE
and not item.skip_reason
```

默认：

```python
execute: bool = False
```

所以系统行为是：

```text
先规划
→ 展示 argv / preview
→ 检查风险、参数和置信度
→ 满足门禁才执行
```

### 15.7 异常和降级

| 情况 | 行为 |
|---|---|
| query 为空 | 请求澄清 |
| 实体/日期缺失 | 进入 clarification 或 data_gap |
| 命中 workflow 但置信低 | preview，不自动执行 |
| workflow 缺 argv | 不执行，记录 skip reason |
| 风险不是 low | 不自动执行 |
| confidence < 0.7 | 不自动执行 |
| `execute=False` | 只返回计划和命令 |

关键思想：

> 不确定性不能被流畅文本掩盖，必须转化成显式路由或 skip reason。

### 15.8 评测方式

Router 应评测：

1. route accuracy：人工标注问题应走哪条路；
2. clarification precision：真正缺信息时才追问；
3. unsafe execution rate：不应执行却执行的比例，目标必须接近 0；
4. unnecessary planner rate：已有 workflow 却进入自由规划的比例；
5. coverage：多少问题能映射到稳定路径；
6. latency：规则路径与 Planner 路径的延迟差。

当前代码具备可记录和可单测结构，但不能声称已经有大规模线上标注路由集。

### 15.9 当前边界

已实现：

- 四类路由；
- `RouteDecision`；
- clarification 和 data gap；
- 已知 workflow 注册；
- Planner 路径；
- preview 和自动执行门禁。

不能夸大：

- 不是训练出的专用金融 Router 模型；
- 没有已核实的大规模路由 accuracy 报告；
- 规则与触发词仍可能对长尾表达不够鲁棒；
- Planner 的语义判断仍需通过后续 evidence gate 约束。

### 15.10 面试表达

#### 30 秒

> 我没有让 LLM 一上来就自由规划，而是先做有限状态路由。空问题、缺参数、已知 workflow 和明显 data gap 由确定性规则处理，开放分析问题才进入 Planner。路由输出是结构化 `RouteDecision`，后续执行还要经过低风险、`auto_execute`、置信度大于 0.7 和无缺参等门禁，默认只 preview。这样做的目标不是让模型更自由，而是让行为可预测、可单测、可审计。

#### 2 分钟

> 金融 Agent 既有问答，也可能触发数据导入、复盘等命令路径。如果纯靠 LLM function calling，相同表达可能走不同工具，而且缺参数、高风险和低置信度都可能被一段看似合理的计划掩盖。我先把路由问题形式化成四种状态：`known_workflow`、`planner_analysis`、`data_gap`、`clarification_needed`。规则优先命中确定性强的情况，Planner 只处理长尾分析；输出包含 selected paths、plan steps、missing data checks、next action 和 warnings。命令层默认 `execute=False`，只有 argv 存在、路径声明可自动执行、风险为 low、置信度至少 0.7 且没有 skip reason 才允许执行。这样即使模型判断错了，也不会直接转化成高风险动作。

#### 追问

**问：为什么不用一个强模型直接路由？**
答：路由是有限决策和风险控制问题，不是生成质量问题。强模型可以提高语义覆盖，但不能替代参数检查、权限、风险和确定性门禁。

**问：规则越来越多会不会难维护？**
答：会，所以规则只覆盖稳定高精度意图，长尾进入 Planner；通过 route distribution 和误路由样本决定是否新增规则，而不是无限堆关键词。

**问：0.7 怎么来的？**
答：当前是工程阈值，不应说成统计校准后的最优值。正式上线应在标注集上做 reliability calibration，并按动作风险设置不同阈值。

---

## 16. Answer Orchestrator：把自然语言问题编译成研究计划

真实代码：

- `finance-workspace-private/intelligence/services/answer_orchestrator.py`
- `finance-workspace-private/intelligence/services/ask.py`

### 16.1 业务问题

即使 Router 已判断“这是分析问题”，仍然不知道：

- 是个股深挖、题材分析、市场复盘还是估值；
- 必须看哪些证据；
- 哪些来源优先；
- 是否允许快速回答；
- 数据缺失时怎样表述；
- 最终答案必须包含哪些 section。

如果直接把所有工具结果拼进 prompt：

1. 不同问题拿到相同 context，噪声很大；
2. 估值问题可能没有财务数据；
3. 市场复盘可能被历史 memory 带偏；
4. 快答可能错误地跳过关键检索；
5. 输出结构不可控。

### 16.2 第一性原理

研究型问答可以看成一个受约束查询计划：

```text
Question
→ classify intent
→ determine required evidence lenses
→ plan retrieval
→ declare quality gates
→ declare output contract
→ execute
```

这与数据库 query planner 相似：

- 用户只描述“要什么”；
- Planner 决定“要查哪些源、以什么顺序、满足什么条件”；
- 执行器负责真正取数；
- Validator 检查结果。

### 16.3 技术选型

选择 `QuestionPlan` 作为显式中间表示，而不是把规划藏在 prompt 里。

原因：

1. 可序列化、可记录、可回放；
2. 不同问题类型可复用下游执行器；
3. quality gates 与输出契约不会因模型措辞漂移；
4. 数据缺口策略可提前声明；
5. 可对 plan 本身做单测。

### 16.4 `QuestionPlan`

```python
@dataclass(frozen=True)
class QuestionPlan:
    query: str
    question_type: str
    depth: str
    confidence: float
    required_lenses: list[str]
    retrieval_plan: list[str]
    quality_gates: list[str]
    output_contract: list[str]
    missing_data_policy: list[str]
    warnings: list[str]
    research_spec: ThemeResearchSpec | None
    base_finance_mode: BaseFinanceMode | None
```

注意：

> `QuestionPlan` 不直接执行工具。它告诉下游这是什么问题、必须看什么、优先取什么证据、答案要满足什么约束。

### 16.5 问题类型

```text
stock_deep_dive
theme_analysis
market_review
market_forecast
news_impact
valuation_estimate
financial_analysis
answer_review
methodology_discussion
general_finance_qa
```

为什么要区分：

- 个股深挖要看公司本体、题材暴露、L3 兑现和同链对比；
- 市场复盘要看指数、涨跌家数、题材强度和扩散；
- 估值要看财务、假设、敏感性和数据日期；
- 新闻影响要区分事件、传导链、受益/受损对象和时间窗口；
- 方法论讨论不应假装需要实时行情。

### 16.6 `required_lenses`

它表达“必须从哪些角度看”，例如：

```text
公司本体
题材暴露
证据硬度
盘面验证
同链替代
估值
反证
验证窗口
```

作用是防止模型只沿着最显眼的叙事回答。

比如“某公司是否受益于液冷”，不能只看：

```text
公司名称和液冷同时出现在一篇文章
```

还要看：

- 公司具体产品是什么；
- 是否有订单、认证、量产等 L3；
- 题材涨但公司是否跟涨；
- 同链是否有更纯的标的；
- 估值是否已经反映预期。

### 16.7 `retrieval_plan`

它声明优先访问哪些源，而不是把全部源无差别塞入上下文。

例如：

```text
stock_deep_dive
→ S 当前盘面
→ G 公司—概念暴露
→ R 已登记证据
→ W 语义和上下游扩展
→ L 官方硬证据
→ D 财务/历史结构化数据
→ M/V 只做先验和复盘
```

### 16.8 `BaseFinanceMode`

它进一步记录：

- 是否必须有行情；
- 是否必须有历史记忆；
- 是否必须有新闻；
- 是否必须有图谱；
- 是否必须有财务；
- 是否允许 quick answer。

这里的关键设计是：

> quick answer 只缩短表达，不能跳过已经触发的必要检索。

否则“快答”会变成“少查证据但语气一样确定”。

### 16.9 `quality_gates`

质量门可以包括：

- 本地数据是否新鲜；
- 是否存在支持核心结论的证据；
- 是否区分硬事实和候选；
- 是否写出反证；
- 是否显式说明缺口；
- 是否有验证窗口；
- 是否有引用；
- 是否违反 AnswerSpec。

### 16.10 `output_contract`

输出不是任意 prose，而应包含固定语义区：

```text
结论
证据链
分歧 / 反证
缺口
后续验证点
交易含义或研究含义
引用
```

固定 section 的价值：

1. 用户能快速比较不同回答；
2. reviewer 能按字段检查；
3. 历史结果能结构化评测；
4. 缺口不会被藏在段落末尾。

### 16.11 `missing_data_policy`

真实原则：

```text
缺数字
→ 先明确缺什么
→ 如有合理替代锚点则给区间/代理变量
→ 仍不足时写：
   缺 X
   仍可判断 Y
   不能判断 Z
   验证窗口为 T
```

不能做的是：

```text
没有营收、订单或估值数据
→ 用“行业空间广阔”补成确定性结论
```

### 16.12 在 `ask.py` 中如何落地

`ask.py` 先生成 plan，再据此决定：

- 是否做 entity anchor；
- 是否查 G/R/W；
- 是否启用 compose；
- 要运行哪些 D block；
- 是否需要 L3；
- AnswerSpec 包含哪些字段；
- review 要检查什么。

所以：

```text
answer_orchestrator = 规划层
ask.py = 执行与组装层
output_review = 审稿层
```

### 16.13 异常和降级

| 情况 | 处理 |
|---|---|
| 问题类型置信低 | 加 warning，采用 general plan 或请求澄清 |
| 必要行情缺失 | 标 gap，不伪造实时判断 |
| 财务数据缺失 | 使用假设区间或停止给精确估值 |
| 图谱无实体 | 触发 entity/alias gap |
| W 失败 | S/G/R 继续，W 显式 degraded |
| L3 未开启或失败 | 结论降级为预期交易/候选，不说事实验证 |

### 16.14 评测

可以建立 plan-level gold set：

```json
{
  "query": "某公司现在贵不贵",
  "question_type": "valuation_estimate",
  "required_lenses": ["financial", "valuation", "assumption", "risk"],
  "required_sources": ["D"],
  "must_not": ["use_memory_as_current_fact"]
}
```

指标：

- question type accuracy；
- required lens recall；
- unnecessary source rate；
- missing mandatory source rate；
- plan-to-execution consistency；
- output contract compliance；
- data-gap honesty rate。

当前具备结构化 plan 和代码路径，但不能声称已经完成大规模 plan benchmark。

### 16.15 当前边界

已实现：

- 多种问题类型；
- `QuestionPlan`；
- required lenses；
- retrieval plan；
- quality gates；
- output contract；
- missing data policy；
- `BaseFinanceMode`；
- `ask.py` 消费 plan。

不能夸大：

- 不是经过强化学习训练出的 Planner；
- 不是通用 DAG optimizer；
- 部分问题分类仍依赖规则和启发式；
- plan 质量仍需真实 query set 验证。

### 16.16 面试表达

#### 30 秒

> Router 只决定走哪类路径，进入问答后我还设计了 `QuestionPlan`，相当于把自然语言问题编译成研究执行计划。它显式记录问题类型、必看视角、检索源、质量门、输出契约和缺数据策略。比如估值问题必须要财务和假设，个股深挖必须看公司本体、题材暴露、L3 兑现、盘面和反证。这样快答只能缩短表达，不能偷掉必要检索。

#### 2 分钟

> 我把问答编排拆成规划层和执行层。`answer_orchestrator.py` 产生不可变的 `QuestionPlan`，它不直接调用工具，而是声明 question type、required lenses、retrieval plan、quality gates、output contract 和 missing data policy；`ask.py` 再根据它执行 S/G/R/W/M/V/D/L 多源召回。这样做类似数据库 query plan：先明确要满足什么，再决定访问哪些数据。好处是同一个执行器可服务不同问题，缺数据时也有预先约定的降级口径。例如缺精确估值数字时，不允许模型编造，而要写清缺 X、仍可判断 Y、不能判断 Z、验证窗口是什么。

#### 追问

**问：Plan 会不会过度工程化？**
答：一次简单聊天可能不需要，但金融研究需要跨源证据、风险和回放。显式 plan 带来的可测试性和审计价值高于对象开销。

**问：为什么不用 LangChain/LangGraph？**
答：当前核心需求是轻量、确定性、可读的本地编排，现有 dataclass 和 Python 模块已足够。若工作流演进成大量持久化节点、人工中断和复杂恢复，再评估图编排框架。

---

## 17. 多源证据模型：S/G/R/W/M/V/D/L 为什么必须分开

真实代码和资料：

- `finance-workspace-private/intelligence/services/ask.py`
- `finance-workspace-private/intelligence/services/research_brief.py`
- `finance-workspace-private/intelligence/services/source_credibility.py`
- `finance-workspace-private/intelligence/services/claim_lineage.py`
- `knowledge-base-private/wiki/relations/`

### 17.1 业务问题

“某公司受益于某题材”可能来自完全不同的东西：

1. 今天股价很强；
2. 图谱中公司和题材有关联；
3. 卖方研报说它受益；
4. 公司公告已有订单；
5. 用户以前认为它会受益；
6. 历史上类似判断命中过；
7. DuckDB 显示它连续多日跑赢板块。

这些不能都叫“证据”而不标类型。

否则系统会犯三种典型错误：

- 把**市场表现**当成**基本面事实**；
- 把**研报推演**当成**公司兑现**；
- 把**用户历史观点**当成**当前市场事实**。

### 17.2 第一性原理

证据至少有三个独立维度：

```text
来源是什么？
信息硬度多高？
在当前时点是否新鲜、可得？
```

因此不能用一个无标签的 `context` 字符串承载全部信息。

### 17.3 八类来源

#### S：盘面快照

Snapshot / Screen：

- 当前市场日期；
- 题材候选；
- 强弱、涨跌、热度；
- 盘面是否验证叙事。

它回答：

> 市场现在是否在交易这个逻辑？

它不能单独回答：

> 公司是否真的有订单或产能。

#### G：图谱

Graph：

- 公司—概念；
- 实体暴露；
- 产业链关系；
- 别名与 ticker；
- 结构化候选关系。

它回答：

> 哪些实体可能有关联，关系是什么。

它不一定代表关系已被硬证据验证。

#### R：证据索引

Relations / evidence index：

- 已登记证据；
- source trace；
- evidence layer；
- 关系对应的材料。

它回答：

> 这条关系目前有哪些可追溯依据。

#### W：Wiki RAG

Wiki semantic retrieval：

- 未必已入结构图谱的相关页面；
- 同义表达；
- 上下游、同业、竞争格局；
- 反方线索。

它回答：

> 知识库里还有哪些可能相关的候选材料。

W 命中默认首先是 candidate，不应自动升级成事实。

#### M：用户记忆

Memory：

- 用户历史判断；
- 偏好；
- 纠偏；
- experience card；
- 过往关注框架。

它回答：

> 用户过去怎样理解这个问题，系统应避免重复犯什么错。

它不能回答：

> 今天的价格、订单、产能和公告是什么。

#### V：历史回检

Verification：

- 过去判断；
- checkpoint；
- hit/miss/partial/unverifiable；
- 何种条件下结论曾失败。

它回答：

> 类似推理在历史上表现如何，有什么校准信息。

#### D：DuckDB 数据块

Deterministic structured data：

- 行情；
- 财务；
- 题材热度；
- 市场宽度；
- 历史时序；
- 多日趋势；
- L2 资金等。

它回答：

> 可由 SQL 和确定性计算得到的数字事实是什么。

#### L：L3 官方证据工具

Live / L3 lookup：

- 公司公告；
- 交易所披露；
- 互动易 / e互动；
- 订单、认证、量产、扩产等官方事实。

它回答：

> 公司端兑现是否有硬证据。

### 17.4 为什么不把所有来源放进一个向量库

结构化市场数据放进向量库会损失：

- 精确数值；
- 日期过滤；
- 排序和聚合；
- PIT 截断；
- schema 约束；
- 可重算性。

用户记忆放进同一事实库会造成：

- 旧观点和新事实混召；
- 来源难区分；
- 个性化偏好污染公共事实。

官方公告和研报如果不分层，会造成：

- “券商预计”被写成“公司已经”；
- screenshot 和公告拥有相同权重。

所以你的设计不是“多拿一些 context”，而是“保留来源类型直到最终 claim”。

### 17.5 来源优先级

可以用以下口径解释：

```text
数字事实：
D / 官方结构数据 > W 文本描述 > M 历史记忆

公司兑现：
L3 官方公告/定期报告 > 交易所互动 > 深度研报 > 晨会转述 > 社媒截图

当前盘面：
S / D 当前行情 > 历史 V > M 历史观点

关系发现：
G/R 已登记关系 > W 语义候选 > M 用户假设
```

`source_credibility.py` 中的轻量先验：

```text
official_announcement 0.95
periodic_report       0.90
exchange_interaction  0.80
sellside_deep         0.60
morning_note          0.45
pdf_ocr               0.35
social_screenshot     0.20
```

注意：

> 这只是来源可信度先验，不等同于语义真伪模型，也不能替代具体 claim 核验。

### 17.6 证据层 L1/L2/L3/L4/E

在 `research_brief.py` 中，证据会按来源和文本特征分类。

可用面试口径：

| 层 | 含义 |
|---|---|
| L1 | 方向、主题、逻辑线索 |
| L2 | 产业或公司层的较具体基线/推演 |
| L3 | 公告、订单、中标、量产、认证等公司硬证据 |
| L4 | 当前市场价格与盘面验证 |
| E | 用户经验、历史判断、方法论 prior |

核心裁定：

- 有 L3：可以说“事实验证”，但仍要看时效和口径；
- 有 L1/L2、无 L3：只能说“预期交易”；
- 只有 L4：更像“情绪脉冲”；
- 没有有效证据：说“证据不足”。

真实代码原则：

```python
if has_l3:
    verdict = "事实验证"
elif has_l1_or_l2:
    verdict = "预期交易"
elif only_l4:
    verdict = "情绪脉冲"
else:
    verdict = "证据不足"
```

### 17.7 Memory 只能作为 prior

正确融合：

```text
用户历史观点：
“我之前认为 A 是液冷核心标的”

当前系统：
1. 把它作为待检验 hypothesis；
2. 查 G/R/W/L/D；
3. 若硬证据不支持，明确冲突；
4. 不能因为是用户自己的历史观点就提高为事实。
```

错误融合：

```text
M 中出现“有订单”
→ 直接在答案中写“公司已有订单”
```

### 17.8 Claim lineage

`claim_lineage.py` 将最终 claim 与 evidence refs 连接：

- evidence id；
- source catalog；
- claim manifest；
- field path；
- valid time；
- evidence refs；
- 数字事实与 narrative claim 分离。

本质：

```text
不是只在回答末尾列一堆引用，
而是尽可能知道“哪条 claim 由哪条 evidence 支持”。
```

这比 document-level citation 更强，因为一篇长文可能只支持其中一个数字，不支持整段推论。

### 17.9 数据流示例

问题：

> “某公司是不是液冷核心受益？”

系统可能得到：

```text
G：公司与液冷有 graph exposure
R：证据索引有一篇卖方深度
W：召回公司产品、上游材料和竞争对手
L：没有公告/订单/量产类 L3
S：当天股价跟随板块走强
D：过去 5 日相对强度上升
M：用户过去把它列为候选
V：历史类似判断有一次 partial
```

合理结论：

```text
它是“有产业关联、且当前盘面在交易”的候选，
但缺少 L3 公司兑现证据，不能写成已确认核心受益。
后续看公告/互动、相对强度和板块扩散。
```

不合理结论：

```text
公司是液冷核心，订单确定性高。
```

### 17.10 异常和降级

| 缺失 | 结论降级 |
|---|---|
| 无 S/D | 不判断当前市场是否验证 |
| 无 G | 可能是新词、别名或尚未入图 |
| 无 R | 关系缺可追溯证据 |
| W 失败 | 不影响已有确定性源，但减少语义扩展 |
| 无 L3 | 不写“事实验证” |
| M 缺失 | 不影响公共事实回答 |
| V 缺失 | 不能做历史校准 |
| source date 不明 | 标 freshness unknown，不作为强事实 |

### 17.11 评测

多源证据层应看：

- source hit distribution；
- 每类问题的 mandatory source coverage；
- L3 coverage；
- citation coverage；
- claim-evidence alignment；
- unsupported claim rate；
- memory-as-fact violation rate；
- stale evidence rate；
- degraded response rate；
- counterevidence coverage。

### 17.12 当前边界

已实现：

- S/G/R/W/M/V/D/L 的代码与语义分工；
- evidence audit；
- source credibility 先验；
- retrieval telemetry；
- claim lineage 框架；
- 缺 L3 时的降级口径。

不能夸大：

- 不是所有输出 claim 都已完成人工验证的 claim-level 对齐；
- source credibility 分数是启发式先验；
- L3 lookup 默认关闭，并非每次问答都实时查官方来源；
- W 命中仍是候选，检索相关不等于事实成立；
- 完整 Temporal Facts 状态边尚未贯穿 `ask` 全链。

### 17.13 面试表达

#### 30 秒

> 我把上下文按来源拆成 S/G/R/W/M/V/D/L，而不是混成一段 prompt。S 是盘面，G 是图谱，R 是证据索引，W 是 wiki RAG，M 是用户记忆，V 是历史回检，D 是 DuckDB 结构数据，L 是官方 L3 查证。然后再按 L1/L2/L3/L4/E 做证据硬度分层。这样用户记忆只能做 prior，研报推演不能升级成公司事实，盘面上涨也不能等同于基本面兑现。

#### 2 分钟

> 金融场景最大的风险不是没有信息，而是不同语义的信息被混写。例如股价上涨、图谱关联、研报判断、公司公告和用户过去观点都可能指向同一结论，但证据强度完全不同。我让每个来源保留标签直到最终 claim：结构化数字优先由 D 提供，公司兑现优先由 L3 官方证据提供，W 负责语义候选和上下游扩展，M/V 只负责个性化先验与历史校准。`research_brief.py` 再把证据分为 L1/L2/L3/L4/E：只有 L3 才能把口径提升到事实验证，只有盘面就是情绪脉冲，有产业逻辑但无 L3 只能写预期交易。最后通过 claim lineage 把 claim 与 evidence ref 连接，避免回答末尾列了引用但实际没有支持具体结论。

#### 追问

**问：多个来源冲突怎么办？**
答：先按事实类型选权威源，再按时间和 evidence layer 判断；冲突本身进入“分歧/反证”，不能由模型静默平均。

**问：可信度 0.95 是否表示 95% 正确？**
答：不是，它是来源类型先验，不是校准概率。具体 claim 仍需内容、时间和实体一致性检查。

**问：图谱和 RAG 有什么区别？**
答：图谱适合已知实体关系的确定性查询，RAG 适合语义发现和未结构化候选；RAG 可发现线索，图谱提供稳定结构，二者互补。

---

## 18. Knowledge Base RAG：从原始材料到可引用候选页

真实代码和资料：

- `knowledge-base-private/README.md`
- `knowledge-base-private/skills/material-router/SKILL.md`
- `knowledge-base-private/skills/entity-delta-ingest/SKILL.md`
- `knowledge-base-private/skills/lib/rag/chunking.py`
- `knowledge-base-private/skills/lib/rag/retrieval.py`
- `knowledge-base-private/skills/lib/rag/store.py`
- `knowledge-base-private/skills/lib/rag/embedder.py`
- `knowledge-base-private/skills/lib/rag/rerank.py`
- `knowledge-base-private/skills/lib/rag/evaluate.py`
- `knowledge-base-private/scripts/rag_index.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`

### 18.1 业务问题

金融知识库有几个难点：

1. 股票代码、公司名、产品名要求精确匹配；
2. 同一概念有中英文、简称和别名；
3. 研报会用不同措辞描述相同逻辑；
4. 一篇长报告包含多个主题，整页 embedding 噪声大；
5. 直接向量召回容易漏掉代码，纯关键词又漏同义表达；
6. 材料持续更新，旧索引可能引用已变更内容；
7. 检索命中不等于事实成立，还要保留来源和证据层。

### 18.2 第一性原理

RAG 不是：

```text
文档 → embedding → top-k → prompt
```

而是一个信息检索系统：

```text
内容治理
→ 切块
→ 索引
→ 候选召回
→ 融合
→ 扩展
→ 重排
→ 新鲜度检查
→ 引用绑定
→ 离线评测
```

检索的目标也不是“找到看起来相关的文字”，而是：

> 在有限上下文预算内，提高支持当前任务的证据被召回的概率，并保留足够元数据供后续核验。

### 18.3 从 raw 到 wiki

知识库流程：

```text
外部材料
→ raw/ 不可变归档
→ wiki/sources 来源页
→ wiki/concepts 概念页
→ wiki/entities 实体页
→ wiki/synthesis / briefings 综合页
→ wiki/relations 结构关系
→ .rag_index 派生索引
→ finance kb_rag.py 只读消费
```

`material-router` 把内容分层：

- N1：源索引；
- N2：概念层；
- N3：实体层；
- N4：信号轨；
- N5：催化池。

为什么 `raw` 不直接等于事实：

- 原始材料可能是卖方观点、OCR、转述；
- 必须保留 provenance；
- 需要判断哪些内容能进入 entity 硬事实，哪些只能进入 graph candidate；
- source note 与 entity page 的语义等级不同。

### 18.4 为什么 Markdown + YAML frontmatter

选择原因：

1. 人类可读，可在 Obsidian 审阅；
2. Git 可 diff、回滚和审计；
3. YAML 提供机器可解析元数据；
4. Markdown 标题天然适合 section chunking；
5. `[[wikilink]]` 可作为轻量图关系；
6. 不被专用向量数据库格式锁定。

frontmatter 可承载：

- title；
- tags；
- source；
- source type；
- publish/available time；
- evidence layer；
- ticker；
- revision；
- provenance。

### 18.5 Chunking 的真实实现

`Chunk`：

```python
@dataclass
class Chunk:
    id: str
    file_path: str
    page_type: str
    title: str
    tags: list[str]
    section: str
    wikilinks: list[str]
    text: str
    content_hash: str
    mtime: float
    page_id: str
```

`chunk_file(path, vault_root)`：

1. 解析 YAML frontmatter；
2. 获取 title 和 tags；
3. 提取 wikilinks；
4. 按 Markdown heading 构造 breadcrumb；
5. 按 section 切；
6. 超长 section 再按段落切；
7. 增加约 15% overlap；
8. 给正文增加 title/tags/section 前缀；
9. 计算 SHA-1 content hash；
10. 生成稳定 chunk id。

配置口径：

```text
TARGET_TOKENS ≈ 768
MAX_TOKENS ≈ 1024
OVERLAP_RATIO ≈ 15%
```

### 18.6 为什么按 section 切，而不是固定字符

固定 500 字符可能把：

```text
“风险因素”标题
```

与下一段正文拆开，或者把：

```text
公司产品、客户、风险
```

混在同一块。

按 section 的优势：

- 保留语义边界；
- breadcrumb 给 chunk 上下文；
- 引用时能指出具体 section；
- 对结构化 Markdown 友好。

过长 section 再按段落切，是为了控制 embedding 和 rerank 输入长度。

### 18.7 Dense 召回

`BGEM3Embedder`：

```python
BGEM3FlagModel
return_dense=True
return_sparse=False
return_colbert_vecs=False
```

输出：

- dense 1024 维；
- L2 normalize；
- 查询与 chunk 可用点积做 cosine 等价相似度。

为什么选择 BGE-m3：

- 中文能力较强；
- 支持较长文本；
- 本地可运行；
- 同一模型接口具备 dense/sparse 能力；
- 与 bge reranker 生态兼容。

### 18.8 必须纠正的口径：实际 lexical 是独立 BM25

虽然 `BGEM3Embedder` 实现了：

```python
encode_sparse(...)
```

但当前真实 RAG 主路径中的 lexical 召回是：

```python
rank_bm25.BM25Okapi
```

即：

```text
BGE-m3 dense
+
独立 rank_bm25 lexical
```

不能说成：

> 当前生产链路已经使用 BGE-m3 dense+sparse 联合检索。

准确说法：

> BGE-m3 提供 dense embedding；代码预留了 sparse 接口，但实际 hybrid 的关键词支路由独立 `rank_bm25` 实现。

这是项目深挖时很能体现诚实度的细节。

### 18.9 为什么保留 BM25

Dense 擅长语义，但对以下内容不总稳定：

- `002636`；
- 特定产品型号；
- 生僻公司名；
- 精确公告术语；
- 缩写和 ticker。

BM25 利用词频和逆文档频率，适合精确 lexical signal。

中文 tokenizer 采用：

- 汉字单字；
- bigram；
- 拉丁和数字段保留；
- 不依赖 jieba。

优点：

- 确定性；
- 零额外词典；
- 股票代码不会被破坏；
- CI 可离线运行。

### 18.10 Hybrid pipeline

真实链路：

```text
dense top-80
∪
BM25 top-80
→ exact entity/code/wikilink boost
→ RRF
→ page aggregation
→ one-hop wikilink neighbor expansion
→ optional cross-encoder rerank top-50
→ top-k pages
```

关键配置：

```text
DENSE_TOPN = 80
BM25_TOPN = 80
RRF_K = 60
BOOST_WEIGHT = 0.5
NEIGHBOR_DISCOUNT = 0.25
RERANK_CANDIDATES = 50
```

### 18.11 为什么用 RRF，而不是直接相加分数

Dense score 和 BM25 score 不在同一量纲：

- dense 可能在 cosine 范围；
- BM25 分值取决于语料和词频；
- 不同查询分布也不同。

直接：

```text
dense_score + bm25_score
```

需要复杂归一化。

RRF 只依赖排名：

\[
RRF(d)=\sum_i \frac{1}{k+r_i(d)}
\]

真实代码：

```python
scores[idx] += 1.0 / (RRF_K + rank + 1)
```

优点：

- 简单；
- 对不同分数量纲鲁棒；
- 同时被多个召回器排前的结果自然加权；
- 适合 POC 和中小规模系统。

### 18.12 Exact-match boost

`_query_entities` 会识别：

- `[[wikilink]]`；
- 六位股票代码；
- query 中直接出现的 page id / title。

然后对匹配 title、tag、wikilink 的 chunk 加 boost。

第一性原因：

> 精确实体命中是强先验，不应该被语义相似但主体错误的文档压过。

### 18.13 Wikilink 一跳邻居

Hybrid 先找到 seed pages，再沿 `[[wikilink]]` 扩展一跳。

用途：

- 公司页链接到概念页；
- 概念页链接到产业链；
- source page 链接到 entity；
- 可以补回 lexical/dense 没直接命中的结构相关页。

邻居分数：

```text
seed.score × NEIGHBOR_DISCOUNT
```

为什么只做一跳：

- 多跳很快引入图扩散噪声；
- 一跳保留直接语义关系；
- 计算和解释更简单。

### 18.14 Reranker

默认模型：

```text
BAAI/bge-reranker-v2-m3
```

实现：

```python
AutoModelForSequenceClassification
query + passage
→ single logit
→ sigmoid
```

只重排 hybrid 前 50 个候选。

为什么不是全库 cross-encoder：

- cross-encoder 要对每个 query-document pair 联合编码；
- 精度更高但成本远高于 bi-encoder；
- 先召回再重排是典型两阶段架构。

为什么 rerank 不提高 recall ceiling：

> 它只能重排已召回候选；如果正确页面根本不在候选池，reranker 无法创造它。

### 18.15 两种索引模式

`kb_rag.py` 支持：

```text
structured
  .rag_index
  hybrid

full
  .rag_index_full
  rerank
```

结构版：

- 主要索引结构化 wiki；
- 速度较快；
- 日常问答默认。

全文版：

- 可包含 raw 全文；
- 候选多、噪声大；
- 适合“深挖、看原文、权威、全文”等请求；
- 默认建议 rerank。

### 18.16 索引存储

`.rag_index/`：

```text
chunks.jsonl
dense.npy
meta.json
bm25_tokens.jsonl.gz
```

为什么当前没用专用向量数据库：

- 万级 chunk 可用 NumPy 暴力点积；
- 本地个人工作台；
- 简化依赖和运维；
- 索引是可重建派生产物；
- JSONL/NumPy 易检查。

什么时候应换：

- chunk 到百万级；
- 多用户并发；
- 需要分布式 ANN；
- 需要在线增删与 metadata filter SLA；
- 需要多租户隔离。

### 18.17 增量更新

`store.py` 按：

```text
chunk id + content_hash
```

复用未变化向量，只重嵌新增或变化 chunk。

为什么不能只看 mtime：

- 文件复制可能改变 mtime 但内容不变；
- Git checkout 可能重置 mtime；
- content hash 更接近真实内容变化。

### 18.18 索引新鲜度

新版本使用参与索引文件的 manifest revision：

```text
manifest:v1:<hash>
```

当前内容与 index build 时内容不一致：

```text
stale
```

旧指纹无法安全判定：

```text
unknown
```

原则是 fail-closed：

> 无法证明 fresh，不返回可能错误的 fresh。

`rag_index.py query` 支持：

```text
--stale-policy fail
--stale-policy warn
--stale-policy ignore
```

`kb_rag.retrieve(..., require_fresh=True)` 在正式问答中会：

- 丢弃 stale；
- 丢弃 unknown；
- 只让 fresh hit 进入证据；
- 记录 degraded warning。

### 18.19 跨仓调用

Finance Workspace 不复制 RAG 实现，而是：

```text
kb_rag.py
→ subprocess
→ knowledge-base/scripts/rag_index.py query --json
```

为什么这样做：

- 知识库拥有索引和 chunking 的 single source of truth；
- 金融仓只做消费；
- 两个仓可独立演进；
- 失败可以局部降级，不破坏 S/G/R。

代价：

- subprocess 有启动延迟；
- 环境和路径需配置；
- JSON 协议必须稳定；
- 多次 aperture 检索会重复启动进程。

### 18.20 真实失败处理

`kb_rag.py` 显式处理：

- 知识库路径缺失；
- `rag_index.py` 缺失；
- index 不存在；
- subprocess timeout；
- non-zero exit；
- stdout 非 JSON；
- JSON 不是列表；
- hit 缺 `chunk_id`；
- hit 缺 `content_hash`；
- hit 缺 revision；
- revision 混杂；
- freshness 非法；
- stale / unknown；
- 无 fresh hit。

这些失败不会伪装成 W 成功。

输出会包含：

- `ok`
- `warning`
- `hits`
- `telemetry.status`
- `latency_ms`
- `hit_count`
- `neighbor_hits`
- score max/min/mean
- index revision/freshness。

### 18.21 为什么不能“W 失败就让 LLM 自己答”

因为这会把：

```text
检索失败
```

伪装成：

```text
没有相关证据，但模型凭参数知识生成了一个答案
```

正确行为是：

- S/G/R 等来源照常使用；
- W 标 degraded；
- 如果问题依赖 W，则降低置信；
- 明确“语义知识库检索未成功”；
- 不补造引用。

### 18.22 评测

`evaluate.py` 支持：

- Recall@k；
- hit@k；
- MRR；
- BM25 / dense / hybrid / rerank 对比；
- aliases；
- 逻辑卡 suffix normalization；
- recall ceiling。

#### Recall@k

\[
Recall@k = \frac{|Relevant \cap TopK|}{|Relevant|}
\]

适合一个问题有多个应召回页面。

#### Hit@k

Top-k 只要命中至少一个相关页记 1。

适合判断：

> 系统是否至少找到了一个可用入口。

#### MRR

\[
MRR = \frac{1}{N}\sum_i \frac{1}{rank_i}
\]

衡量第一个相关结果是否靠前。

#### Recall ceiling

如果一题有 20 个 expected pages，而 `k=5`：

```text
完美排序的 recall@5 上限也只有 5/20
```

把 ceiling 显式算出，避免错误解读指标。

### 18.23 评测集为什么比模型选择更重要

如果 expected pages 是自动生成或错误标注：

- hybrid “提升”可能只是对标签过拟合；
- aliases 可能把不同概念误合并；
- suffix normalization 可能虚增命中；
- 真实用户问题分布没有被覆盖。

因此正式结论需要：

1. 真实用户 query；
2. 人工判断哪些页面真正支持答案；
3. 区分必需页和可选页；
4. 记录标注分歧；
5. 按问题类型切片；
6. 对检索失败做 error analysis。

### 18.24 当前边界

已实现：

- raw/wiki/relations 分层；
- section-aware chunking；
- BGE-m3 dense；
- 独立 BM25；
- exact boost；
- RRF；
- wikilink neighbor；
- optional cross-encoder rerank；
- content hash 增量；
- index freshness；
- subprocess timeout/non-zero/JSON 校验；
- Recall/hit/MRR 评测框架。

不能夸大：

- README 明确写的是 **Hybrid 检索 POC**；
- BGE sparse 接口存在，但实际主检索 lexical 是 `rank_bm25`；
- HashEmbedder / HashReranker 只是 CI 冒烟，不能证明质量；
- 没有充分证据证明当前参数对真实金融问题最优；
- 需要人工标注 query set 才能宣称 hybrid 或 rerank 的真实收益；
- 不是大规模生产向量服务。

### 18.25 面试表达

#### 30 秒

> 我的 RAG 不是单向量 top-k，而是从 Markdown/YAML 知识治理开始：按 section 切块，BGE-m3 做 dense，独立 `rank_bm25` 做关键词召回，再用 RRF 融合，对公司名、股票代码和 wikilink 精确命中加 boost，沿 wikilink 扩一跳，必要时用 bge cross-encoder 重排。索引按 content hash 增量更新，并要求 hit 绑定 chunk、content hash、source revision 和 freshness；过期或无法证明新鲜的结果不会进入正式证据。

#### 2 分钟

> 金融检索既要语义，又要精确实体。纯 BM25 会漏同义表达，纯 dense 又可能漏股票代码和专有名词，所以我做了两阶段 hybrid：dense top-80 与 BM25 top-80 合并，用 RRF 避免不同分数量纲的归一化问题，再给实体、代码和 wikilink 精确匹配加 boost，并沿知识库双链做一跳邻居扩展。全文索引噪声更大时，对前 50 个候选用 bge-reranker-v2-m3 重排。工程上索引是 JSONL、NumPy 和 gzip token corpus，按 chunk id + content hash 增量更新；Finance Workspace 通过 subprocess 调知识库 CLI，显式处理超时、非零退出、坏 JSON、revision 混杂和 stale/unknown freshness。评测支持 Recall@k、hit@k、MRR 和 recall ceiling，但 README 仍把它定义为 POC，真实收益要用人工标注 query set 验证。

#### 追问

**问：为什么 RRF 的 k 是 60？**
答：这是常用经验值和当前配置，不应宣称是最优；应在标注集上搜索，并观察不同 query slice。

**问：为什么不用 FAISS？**
答：当前万级 chunk、本地单机，NumPy 暴力搜索足够简单；规模和并发上升后再引入 ANN。

**问：如何评测 reranker？**
答：先固定召回候选池，比较 rerank 前后的 MRR/nDCG/Recall@k；还要看延迟和错误类型，避免只看均值。

---

## 19. Closed-loop Retrieval：为什么检索要有 narrow、broad、counter

真实代码：

- `finance-workspace-private/intelligence/services/closed_loop_retrieval.py`
- `finance-workspace-private/intelligence/services/ask.py`

### 19.1 业务问题

一次 query 往往只能找到“最像用户问题”的材料，但研究任务还需要：

- 主体的精确证据；
- 上下游和同业；
- 替代表达；
- 宏观需求与竞争格局；
- 风险和证伪。

只做一次 top-k 容易产生确认偏误：

```text
用户问“为什么看好 A”
→ 检索器只找“看好 A”的材料
→ 模型总结成更强的看好结论
```

### 19.2 第一性原理

研究不是“找到支持材料”，而是：

```text
提出假设
→ 找直接证据
→ 扩展相关变量
→ 主动寻找反证
→ 决定结论强度
```

所以检索本身也要反映研究方法。

### 19.3 三个孔径

#### narrow

目标：找到主体的精确证据。

有 entity anchor 时会构造：

```text
公司名 + ticker
公司名 + 原始六位代码
graph_query
```

没有 anchor 时尝试：

```text
原 query
query + 实体 代码
query + 公司 题材
```

#### broad

目标：扩展上下文和替代解释。

查询：

```text
subject + context + 上下游 同业
subject + context + 产业链 替代表达
subject + context + 宏观 需求 竞争格局
```

其中 context 会吸收：

- anchor concepts；
- narrow hits 中抽取的高信息词。

#### counter

目标：主动找反方。

查询：

```text
subject + terms + 风险 证伪 不及预期
subject + terms + 替代 竞争 受损
subject + terms + 反方 下滑 失败
```

### 19.4 核心对象

```python
@dataclass(frozen=True)
class RetrievalAttempt:
    aperture: Literal["narrow", "broad", "counter"]
    query: str
    status: str
    hit_count: int
```

```python
@dataclass(frozen=True)
class BucketedHit:
    aperture: ...
    hit: WikiHit
```

```python
@dataclass
class ClosedLoopRetrievalResult:
    conclusion: list[BucketedHit]
    clues: list[BucketedHit]
    discarded: list[BucketedHit]
    counter_clues: list[BucketedHit]
    attempts: list[RetrievalAttempt]
    warnings: list[str]
    telemetry: RetrievalTelemetry | None
```

### 19.5 为什么要记录 attempt

最终没命中可能有不同原因：

- query 写得差；
- narrow 为空，但 broad 有结果；
- 索引超时；
- 索引 stale；
- 有 hit 但被 freshness gate 丢弃；
- 反证孔径没有任何材料。

只记录最终 `hits=[]` 无法排障。

`RetrievalAttempt` 让系统知道：

```text
哪个 aperture
用了什么 query
retriever status 是什么
命中了几条
```

### 19.6 最多三次空尝试

```python
MAX_EMPTY_ATTEMPTS = 3
```

每个孔径会按候选 query 尝试，命中后返回；连续空结果最多尝试三个。

这在 recall 和 latency 之间做了工程折中：

- 一次失败不立即放弃；
- 也不无限改写 query。

### 19.7 分桶逻辑

结果不是全部进入 conclusion。

#### counter hit

正分 counter hit：

```text
counter_clues
同时进入 clues
```

不会作为主结论支持证据。

#### conclusion

需要：

- score > 0；
- 且 hard source 或与相关词直接重叠。

hard source 可以来自：

- `fact_hardness` 为 hard/verified/canonical；
- `evidence_layer` 为 L3/L4/canonical。

#### clues

有正分但不满足硬度/直接相关条件。

#### discarded

无有效分数或不足以作为候选。

### 19.8 为什么“相关”还不够

Dense retrieval 的相关可能只是：

```text
都在谈服务器散热
```

但用户问的是：

```text
某公司的液冷订单是否兑现
```

所以 conclusion 还要求：

- 主体直接重叠；
- 或证据硬度足够。

### 19.9 `ask.py` 中的真实调用

```python
loop = retrieve_closed_loop(
    options.query,
    anchor=anchor,
    retrieve=lambda retrieval_query: kb_rag.retrieve(
        retrieval_query,
        resolved_kb_wiki,
        k=options.wiki_rag_k,
        mode=options.wiki_rag_mode,
        timeout=options.wiki_rag_timeout,
        excerpt_chars=options.wiki_rag_excerpt,
        index_dir=options.wiki_rag_index_dir,
        require_fresh=True,
    ),
)
```

注意：

- 每个 aperture 都继承 freshness gate；
- warning 不被丢弃；
- hit 保留 aperture；
- counter clues 单独进入反证区域。

### 19.10 数据流

```text
原 query
→ entity anchor
→ narrow query candidates
→ W retriever
→ narrow hits
→ 从 narrow hit 抽取概念词
→ broad queries
→ broad hits
→ counter queries
→ counter hits
→ dedupe
→ conclusion / clue / counter / discarded
→ AnswerSpec 和反证计划
```

### 19.11 异常和降级

| 情况 | 行为 |
|---|---|
| narrow 三次为空 | warning，继续 broad/counter |
| broad 为空 | 缺少上下游/同业扩展 |
| counter 为空 | 明确反证检索未命中，不等于没有风险 |
| retriever timeout | attempt status=timeout，记录 warning |
| stale hits 被丢弃 | degraded，不进入正式证据 |
| hit 相关但硬度不足 | 进入 clue，不进 conclusion |
| 同一 chunk 重复 | 按 aperture/path/chunk 去重 |

关键口径：

> “没有找到反证”不等于“反证不存在”，只能说当前知识库和检索查询未命中。

### 19.12 评测

除了普通 Recall@k，还应按 aperture 评测：

- narrow entity precision；
- narrow evidence recall；
- broad novelty；
- broad useful expansion rate；
- counterevidence hit rate；
- conclusion precision；
- clue-to-evidence promotion rate；
- discarded false-negative rate；
- 每个 aperture latency；
- empty-after-3-attempts rate。

需要人工判断：

- broad 结果是否真正增加决策信息；
- counter 是否构成有效反证，而非只含“风险”字样。

### 19.13 当前边界

已实现：

- narrow/broad/counter；
- query expansion；
- 三次尝试；
- attempt 记录；
- conclusion/clue/counter/discarded 分桶；
- warning 和 telemetry；
- 与 `ask.py` 集成。

不能夸大：

- query expansion 主要是启发式词模板，不是训练出的 multi-hop retriever；
- counter retrieval 不能保证找到真实最强反证；
- 分桶依赖 score、字符串重叠和 metadata，仍需人工评测；
- 当前 subprocess 多次查询可能带来明显延迟。

### 19.14 面试表达

#### 30 秒

> 我没有把 RAG 做成一次 top-k，而是实现了 narrow、broad、counter 三孔径闭环。narrow 找公司和代码的直接证据，broad 根据 anchor 和初始命中扩展上下游、同业、宏观和替代表达，counter 主动搜风险、证伪和竞争。每次尝试都记录 query、status 和 hit count，结果再分成 conclusion、clue、counter clue 和 discarded，避免所有语义相关文本都直接支持结论。

#### 2 分钟

> 单次 RAG 很容易强化用户原始假设，所以我把研究流程编码进检索。先用实体和 ticker 做 narrow，确保主体正确；再从 narrow hits 抽取概念，扩展产业链、同业和竞争格局；最后构造风险、失败和替代类 counter query。每个 aperture 最多尝试三个 query，并保存 `RetrievalAttempt`。命中后也不直接全进 context：有硬证据或直接实体重叠的才进入 conclusion，相关但证据弱的进入 clue，反方结果单独进入 counter clues。这样检索失败、证据不足和反证缺失都能被显式看到，而不是在 LLM 的答案里消失。

#### 追问

**问：这算 multi-hop RAG 吗？**
答：有基于前一阶段 hit 抽词再检索的迭代特征，但当前主要是启发式闭环，不应夸成复杂训练式 multi-hop reasoning。

**问：怎样证明 counter 有用？**
答：构造带已知反证的人工集，评估 counter hit rate 和最终 unsupported confidence 是否下降；同时人工判断反证质量。

---

## 20. DuckDB 与结构化市场数据：为什么数字事实不应该只进向量库

真实代码和资料：

- `finance-workspace-private/market_feature_store/`
- `finance-workspace-private/intelligence/services/ask.py`
- `finance-workspace-private/intelligence/services/ask_planner.py`
- `finance-workspace-private/intelligence/services/market_timeseries.py`
- `finance-workspace-private/intelligence/services/market_midterm.py`
- `finance-workspace-private/intelligence/services/market_financials.py`
- `finance-workspace-private/intelligence/services/market_analogs.py`
- `finance-workspace-private/intelligence/services/market_moneyflow.py`
- `finance-workspace-private/intelligence/services/valuation_estimate.py`
- `finance-workspace-private/intelligence/services/valuation_gap.py`

### 20.1 业务问题

以下问题需要精确结构化计算：

- 近 20 日涨幅；
- 某题材连续几天进入强势队列；
- 市场上涨家数、涨停数；
- 估值分位；
- 财报季度趋势；
- 同链股票相对强度；
- T 日之前可用的行情。

如果把表格转成文本 embedding：

- 数字近似相似不等于相等；
- 很难 `WHERE date <= T`；
- 很难 group by、排序、窗口函数；
- 更新后旧 chunk 可能残留；
- 模型容易算错。

### 20.2 第一性原理

数据形态决定存储和查询方式：

```text
精确、规则化、可聚合的事实
→ relational / columnar engine

语义、多义、非结构化材料
→ lexical/dense retrieval
```

LLM 不应承担数据库职责。

### 20.3 为什么选择 DuckDB

当前是本地个人研究工作台，DuckDB 的优势：

1. 嵌入式，无独立数据库服务；
2. 列式执行，适合分析查询；
3. 对 Parquet/CSV 友好；
4. SQL 支持完整；
5. 单文件便于本地快照；
6. Python 集成简单；
7. 比 pandas 手写聚合更可审计。

为什么当前不直接用 PostgreSQL：

- 没有多用户并发写需求；
- 不需要长驻数据库服务；
- DuckDB 更适合本地 OLAP 和文件分析。

什么时候要迁移：

- 多用户并发；
- 在线事务写入；
- 权限和租户隔离；
- 高可用；
- 多节点服务。

### 20.4 典型事实表

项目中可见：

```text
fact_sector_daily
fact_theme_limit_heat_daily
fact_limit_advance_daily
```

它们分别承载：

- 板块日度；
- 题材涨停热度；
- 涨停晋级结构。

面试时不需要背全部 schema，而要讲清：

> 表存储可由确定性查询复算的事实；结论和叙事不直接写进事实表。

### 20.5 D0-D9 数据块

`ask` 的 compose/deep-dive 路径按问题需要生成数据块：

| Block | 语义 |
|---|---|
| D0 | 盘面时序直查 |
| D1 | 市场价值与替代队列 |
| D2 | 客户证据硬度 |
| D3 | 二阶导研究队列 |
| D4 | 主线题材结构 |
| D5 | 估值数据 |
| D6 | 多日中期趋势 |
| D7 | 逐季财报 |
| D8 | 历史类比 |
| D9 | L2 大单资金流 |

并非每个问题都运行全部 D block。

例如：

- 方法论问答不需要 D0-D9；
- 快速实体解释可能只用 G/R/W；
- 估值问题需要 D5/D7；
- 市场复盘更依赖 D0/D4/D6。

### 20.6 Planner-worker 并行

独立数据块通过：

```python
ask_planner.run_block_tasks(..., parallel=...)
```

并行执行。

为什么可以并行：

- D0、D1、D4、D5 等读不同工具或查询；
- 彼此没有数据依赖；
- 并行可降低总等待时间。

如果每块耗时 \(t_i\)：

串行约为：

\[
T_{serial}=\sum_i t_i
\]

理想并行约为：

\[
T_{parallel}\approx \max_i t_i + overhead
\]

### 20.7 为什么 D3 串行

D3 是二阶导研究队列，需要使用前面数据块形成的 `evidence_text`。

因此：

```text
D0/D1/D2/D4... 并行
→ 汇总 evidence_text
→ D3 串行生成
```

这是一个真实依赖关系，而不是所有任务盲目并行。

面试可说：

> 我先构建 DAG，再只并行无依赖节点；D3 依赖前序证据汇总，所以作为 barrier 之后的串行收尾。

### 20.8 数据缺口显式化

每个 block 需要区分：

```text
not attempted
empty
error
ok
```

否则：

- 没有数据；
- 没运行；
- SQL 失败；
- 条件无匹配；

都会被错误地解释成同一个空列表。

telemetry 应记录：

- block attempted；
- row count；
- latency；
- error / warning；
- source date；
- freshness。

### 20.9 `ask` 默认不强依赖 DuckDB

项目 README 和代码口径：

> `ask` 默认可以在不依赖 DuckDB 的情况下运行 S/G/R/W 等基础路径；compose、深挖或特定问题才会选择 D block。

不能在面试中说：

> 所有问题都实时查询完整 DuckDB。

准确说法：

> DuckDB 是结构化事实源；是否访问由 QuestionPlan 和 compose path 决定。

### 20.10 结构化数据与 RAG 如何合并

错误方式：

```text
SQL 结果 + wiki chunk + 用户记忆
→ 无标签拼成一个长 prompt
```

正确方式：

```text
D block：
  标明表、日期、字段、计算口径

W hit：
  标明 page、section、chunk、revision、freshness

M：
  标明 user prior / historical

→ 统一进入 evidence audit
→ 按 claim 类型选择合适来源
```

数字 claim 应优先绑定 D evidence，而不是 W 文本中的二手数字。

### 20.11 异常和降级

| 情况 | 行为 |
|---|---|
| DB 不存在 | 对需要 D 的问题标 data gap |
| 表不存在 | block error，不伪造空市场 |
| 查询无行 | empty，并说明日期/实体范围 |
| 某 block 失败 | 其他独立 block 继续 |
| D3 前置 evidence 不足 | 降级或跳过二阶导 |
| 财务字段缺失 | 不给精确估值 |
| 默认 ask 未运行 D | telemetry 写 not attempted |

### 20.12 评测

结构化数据层应评测：

- SQL correctness；
- row-level PIT correctness；
- schema contract；
- 数据完整率；
- 每个 block empty/error rate；
- latency p50/p95；
- 数字 claim match rate；
- 同一输入可复现性；
- 并行前后 wall time；
- D3 是否只在前置完成后执行。

### 20.13 当前边界

已实现：

- DuckDB 特征库；
- 多类事实表；
- D0-D9 数据块；
- planner-worker 并行；
- D3 依赖后置；
- block 级 telemetry；
- 特定问题按需访问。

不能夸大：

- 不是所有 ask 都查 DuckDB；
- 不是实时交易系统；
- 不是流式 tick 级基础设施；
- 数据覆盖依赖 fupanhui、iFinD、AKShare 等上游；
- 上游缺失时仍需要显式 data gap；
- 没有证据证明所有 D block 已在大规模历史集上完全校验。

### 20.14 面试表达

#### 30 秒

> 实时和历史市场数据没有放进向量库，而是进入 DuckDB，因为行情、财务和题材热度需要精确日期过滤、聚合和窗口计算。问答按计划选择 D0-D9 数据块，独立块并行执行，依赖汇总证据的 D3 在 barrier 后串行。每块都区分 not attempted、empty、error 和 ok，避免把没运行或查询失败伪装成“没有数据”。

#### 2 分钟

> 我的系统把非结构文本和结构化事实分开。知识材料走 RAG，行情、财务、题材强度和历史时序走 DuckDB。原因是向量相似度不能替代精确数值、日期截断、group by 和窗口函数。`ask.py` 根据 QuestionPlan 和 compose 模式选择 D0-D9，例如 D0 查盘面时序、D5 查估值、D7 查季度财报。无依赖的数据块通过 planner-worker 并行，D3 需要前面 evidence_text 才能生成二阶导研究队列，因此串行收尾。默认 ask 不一定依赖 DuckDB，所以我会明确说它是按需结构化事实源，而不是每次请求都跑完整数据库。

#### 追问

**问：为什么 DuckDB 而不是 pandas？**
答：SQL 口径更显式、聚合和窗口能力更强、对列式分析更高效，也更易回放；pandas 可用于局部处理，但不作为主要事实查询接口。

**问：怎样避免数字被 LLM 改写错？**
答：数字 claim 绑定 D evidence，经过 AnswerSpec 和 claim fidelity 校验；模型主要解释，不重新计算。

---

## 21. Output Review：为什么生成后还要有确定性审稿

真实代码：

- `finance-workspace-private/intelligence/services/output_review.py`
- `finance-workspace-private/intelligence/services/answer_model.py`
- `finance-workspace-private/intelligence/services/ask.py`

### 21.1 业务问题

即使检索正确，LLM 仍可能：

- 忽略数据新鲜度；
- 把 L1/L2 写成 L3；
- 忘记反证；
- 隐藏数据缺口；
- 给出无法验证的泛化结论；
- 把弱证据写成强结论；
- 修订时破坏原有引用和结构。

所以检索质量不等于最终答案质量。

### 21.2 第一性原理

生成模型优化的是：

```text
下一个 token 的条件概率
```

不是：

```text
金融证据契约是否满足
```

因此需要独立 reviewer，检查可形式化的输出要求。

### 21.3 为什么 reviewer 不直接再用同一个 LLM

如果生成和审核都只靠同一模型、同一上下文：

- 会共享盲点；
- 审核结论难以稳定；
- 不能保证检查顺序；
- 容易产生“看起来认真”的空泛自评。

当前做法是：

```text
确定性 review 先发现具体 violation
→ 可选把 violation 回灌 LLM 修订
→ 再由 AnswerSpec 校验
```

### 21.4 固定检查顺序

`CHECK_ORDER`：

1. 本地数据新鲜度；
2. 证据分层；
3. 反证；
4. 缺口显式化；
5. 可验证假设；
6. 弱证据硬写。

顺序有意义：

- 数据已经过期时，后面再讨论表达完整性价值有限；
- 证据层错误会影响结论强度；
- 有了主结论后必须看反证；
- 最后检查是否把弱证据写硬。

### 21.5 `review_output(...)`

输入通常包括：

- answer text；
- evidence audit；
- gap lines；
- freshness；
- counterevidence；
- question plan；
- AnswerSpec。

输出：

- PASS/WARN；
- 每项检查结果；
- warning；
- revision guidance。

### 21.6 Advisory gate

当前：

```text
blocking = False
WARN 不直接阻断输出
```

为什么：

- 个人研究工作台需要在部分数据缺失时仍给草稿；
- 某些 warning 是信息性；
- 完全阻断可能导致系统不可用。

但 advisory 不等于忽略：

- warning 必须展示；
- 有 LLM 时可触发定向修订；
- 修订后再验证。

### 21.7 WARN 修订链路

```text
初始 answer
→ review_output
→ WARN:
   把具体缺陷加入同一对话
→ LLM 定向修订
→ validate_llm_answer
→ 合格则使用修订版
→ 不合格则保留安全模板或 warning
```

为什么是“定向修订”：

错误：

```text
请重新回答得更好
```

正确：

```text
你把 L2 卖方推演写成了公司已确认事实；
请降级措辞，并补充缺失的 L3 验证点和反证。
```

### 21.8 AnswerSpec 的角色

Reviewer 告诉模型哪里错；
AnswerSpec 检查修订结果是否仍满足：

- 固定 section；
- 必要引用；
- 禁止项；
- 缺口和反证；
- claim 类型；
- 格式契约。

这避免模型修一处又破坏另一处。

### 21.9 Review 与自动预测裁判的区别

Output Review 判断：

- 证据和表达是否合规；
- 是否诚实；
- 是否可验证。

它不判断：

- 预测未来最终会不会命中；
- 股票明天会不会涨；
- 当前 thesis 是否一定正确。

后者需要历史 outcome 和 checkpoint verdict。

所以不能说：

> 我实现了自动金融预测裁判。

准确说：

> 我实现了回答的 advisory quality gate，以及独立的历史 checkpoint/verdict 框架。

### 21.10 异常和降级

| 情况 | 行为 |
|---|---|
| 无 LLM | 保留模板答案和 review warning |
| LLM 修订失败 | 不采用坏修订 |
| 修订后结构不合格 | AnswerSpec 拒绝 |
| 数据 stale | 答案降级并显示 freshness warning |
| 无 counter | 明确未找到，不说无风险 |
| gap 未写 | reviewer 触发 warning |
| 弱证据硬写 | 要求降级措辞 |

### 21.11 评测

Reviewer 要单独建立 violation set：

```text
把研报预计写成已实现
引用过期数据
没有反证
没有缺口
数字无来源
把用户 memory 当事实
```

指标：

- violation detection precision/recall；
- false block rate；
- revision success rate；
- post-revision contract pass rate；
- unsupported claim reduction；
- citation coverage improvement；
- review latency；
- 用户是否认为 warning 有用。

### 21.12 当前边界

已实现：

- 固定检查顺序；
- PASS/WARN；
- advisory gate；
- WARN 回灌 LLM；
- AnswerSpec 校验；
- 输出中展示 review。

不能夸大：

- `blocking=False`，当前不是硬阻断安全系统；
- review 规则不能覆盖所有语义幻觉；
- 不是独立训练的 critic model；
- 没有充分大规模数据证明 detection precision/recall；
- 不负责自动判定预测 hit/miss。

### 21.13 面试表达

#### 30 秒

> 检索正确不代表生成正确，所以我在答案后加了确定性 Output Review。它按固定顺序检查数据新鲜度、证据分层、反证、缺口、可验证假设和弱证据硬写。当前是 advisory gate，WARN 不直接阻断，但会把具体 violation 回灌给 LLM 定向修订，再用 AnswerSpec 校验修订版。它审的是证据和表达合规，不是自动判断预测会不会命中。

#### 2 分钟

> LLM 很容易在最后一步把弱证据写强，比如把卖方推演写成公司已确认，或者有主结论却忘了反证。我把 reviewer 从生成 prompt 中拆出来，`review_output` 先用确定性检查按顺序审数据新鲜度、evidence layer、counterevidence、gap、可验证假设和 unsupported strong claim。当前 gate 是 advisory，因为个人研究场景允许在部分缺数据时输出带 warning 的草稿。有模型时，系统不会泛泛地要求“重写”，而是把具体 violation 回灌，比如“请把 L2 口径降级，并补 L3 验证点”；修订后再用 AnswerSpec 校验 section、引用和禁止项。这样把 reviewer、reviser 和 validator 分开。

#### 追问

**问：为什么不直接 blocking？**
答：当前规则尚未充分校准，硬阻断会有较高误杀；先 advisory 收集 violation 和用户反馈，达到可靠阈值后再对高风险规则分级阻断。

---

## 22. Agent Memory：从聊天流水到可治理的长期记忆

真实代码和资料：

- `agent-memory/README.md`
- `agent-memory/30_conventions/frontmatter-spec.md`
- `agent-memory/30_conventions/trust-boundary.md`
- `agent-memory/30_conventions/maintenance.md`
- `agent-memory/40_playbooks/devin-writeback.md`
- `agent-memory/40_playbooks/preflight.md`
- `agent-memory/50_agents/claude-hooks.md`
- `agent-memory/preflight.sh`
- `finance-workspace-private/intelligence/userspace.py`
- `finance-workspace-private/intelligence/services/user_memory.py`
- `finance-workspace-private/intelligence/services/corrections.py`
- `finance-workspace-private/intelligence/services/checkpoints.py`
- `finance-workspace-private/intelligence/services/experience_cards.py`
- `finance-workspace-private/intelligence/users/<user>/`

### 22.1 业务问题

把所有历史对话塞进 prompt 有四个问题：

1. 成本随历史线性增长；
2. 旧信息和当前事实混淆；
3. 聊天中有大量寒暄、试错和过期计划；
4. 多个 Agent 之间无法稳定共享同一上下文。

金融场景更危险：

- 半年前的价格、订单、市场判断会过期；
- 用户主观看法可能与当前硬数据冲突；
- 历史预测不能被重新包装成当时已知事实。

### 22.2 第一性原理

Memory 不是“保存所有 token”，而是：

> 从历史交互中提炼对未来任务有用、可追溯、可更新的状态。

需要区分：

```text
原始对话
稳定事实
项目状态
方法论
用户偏好
一次性纠错
预测与回检
```

不同类型必须有不同生命周期。

### 22.3 为什么 Git + Markdown + YAML + Obsidian

选择理由：

- Markdown：人类可读；
- YAML：机器可解析；
- Git：版本、diff、作者、回滚；
- Obsidian：双链、MOC、人工审阅；
- shell/hooks：低成本自动加载和门禁；
- 无专有格式锁定。

没有一开始上向量数据库或记忆服务，是因为：

- 当前规模和协作方式更需要透明审阅；
- 记忆质量问题先于 ANN 性能；
- Git 对项目决策和方法论更适合；
- 事实时效和 trust boundary 需要明确治理。

### 22.4 分层目录

```text
00_inbox       原始、短期、待整理
10_knowledge   稳定事实与结论
20_projects    项目 MOC、任务和交接
30_conventions 跨 Agent 规范与信任边界
40_playbooks   可复用流程
50_agents      Agent 接入约定卡
60_dialogues   外部 AI 原始对话
70_tutor       经用户批准的学习笔记
_templates     标准模板
```

### 22.5 为什么不能只有“短期记忆/长期记忆”两层

因为长期内容内部语义差异很大：

- 项目进度会变化；
- 方法论较稳定；
- 用户偏好可能可更新；
- 单次反馈只是样本；
- raw 对话不应自动变成知识。

如果都进入一个 long-term vector store，检索时很难决定：

- 哪条可信；
- 哪条过期；
- 哪条是指令；
- 哪条是历史观点。

### 22.6 Frontmatter

通用字段：

```text
title
type
agent
source
date
tags
status
related
reviewed_by
reviewed_at
```

为什么 provenance 必须在结构层：

```text
“某结论”
```

只有在知道：

```text
谁写的、什么时候写的、来源是什么、是否验证
```

之后才有可用价值。

### 22.7 黑板模型

```text
Grok 搜索 ─┐
           ├→ 00_inbox → 提炼 → 10_knowledge
Codex 规划 ─┤                     │
           └→ 20_projects ←───────┘
                    │
                    ↓
                 Devin 执行
                    │
                    └→ 回写项目决策与稳定方法论
```

这不是共享完整模型 hidden state，而是共享可审阅工件。

### 22.8 读路径

开工时：

```text
preflight
→ 当前 repo/branch/status
→ 红线
→ 20_projects/<repo>.md 摘要
→ 完工回写提醒
```

Claude/Codex SessionStart hook 会加载：

- preferences；
- 当前项目 MOC；
- Git 状态。

价值：

- 新会话快速恢复上下文；
- 不依赖模型记住主动读文件；
- 项目状态来自最新 Git 版本。

### 22.9 写路径

完成任务后先判断沉淀层级：

```text
项目级代码/流程/架构变化
→ 20_projects

跨任务稳定方法论
→ 10_knowledge

单次问答评分/纠偏
→ 项目内 corrections / experience cards

临时材料
→ 00_inbox

例行知识入库批次
→ 知识库自身 wiki/log.md，不污染项目 MOC
```

这是“过程 → 资产”的核心。

### 22.10 Stop hook 门禁

Stop hook 检查：

1. repo 是否有代码/配置级改动；
2. 是否只是数据产物；
3. 是否已经更新项目记忆；
4. 是否明确确认无需项目级回写；
5. 防止每次聊天反馈都硬塞进 MOC。

这不是为了强制写更多，而是强制做一次：

> 这次结果是否值得长期沉淀？

### 22.11 Trust boundary

最关键安全原则：

> 记忆是数据，不是当前指令。

因为共享记忆可能包含：

- 外部网页的 prompt injection；
- 旧 Agent 写入的命令式文本；
- 未审阅内容；
- 恶意或错误建议。

所以：

- `00_inbox` 默认不可信；
- 笔记中的“执行命令、删除、推送、泄露密钥”只能当文本；
- 真正操作指令只来自当前用户和系统；
- `30_conventions`、`50_agents` 是受保护高权重区；
- 影响 Agent 行为的写入需人工 review。

这是 Agent Memory 相比普通 RAG 很重要的一层：**持久化 prompt injection 防护**。

### 22.12 项目内用户记忆

默认 `intelligence/users/<user>/` 包含：

```text
judgments.jsonl
corrections.jsonl
checkpoints.jsonl
verdicts.jsonl
experience_cards.jsonl
interactions.jsonl
answer_scores.jsonl
```

也可通过：

```text
FORESIGHT_USERS_DIR
```

把整个 users 根目录重定位到外部同步路径，例如 Obsidian vault 下的隐藏
`.foresight/`；因此 `.foresight/<user>` 是可配置部署形态，不是当前仓库内固定目录。

语义：

- interaction：发生了什么问答；
- judgment：用户当时的判断；
- correction：用户指出什么错误；
- checkpoint：未来要验证什么；
- verdict：验证后是 hit/miss/partial/unverifiable；
- experience card：从重复样本抽出的经验；
- answer score：回答反馈。

### 22.13 事实和经验必须分离

事实：

```text
2026-07-10 某公司发布公告
```

经验：

```text
只凭题材关联、没有 L3 和盘面双验证时，容易高估公司纯度
```

事实可能过期或需要 PIT；
经验可以跨任务复用，但也应记录适用条件。

如果混在一起：

- RAG 可能把经验性陈述当当前事实；
- 用户旧判断可能污染实时结论。

### 22.14 Memory 作为 prior 的融合

可以用贝叶斯语言解释，但不要夸大为已完整实现贝叶斯系统。

概念上：

\[
P(H|E,M) \propto P(E|H)P(H|M)
\]

- `M` 提供 prior；
- 当前证据 `E` 更新判断；
- 硬数据应覆盖旧记忆。

真实工程口径：

```text
memory 提示历史假设和常见错误
→ 当前问题重新查 S/G/R/W/D/L
→ 冲突时以当前硬证据为准
→ 把冲突记录为 correction 或新 checkpoint
```

### 22.15 一致性与检索边界

Git/Markdown 的限制：

- 不是强一致事务数据库；
- 多 Agent 同时写可能冲突；
- Markdown schema 约束弱；
- 双链可能失效；
- 大量笔记的检索效率会下降；
- TTL、superseded 状态不一定自动维护。

当前通过：

- append-only；
- frontmatter lint；
- protected areas；
- writeback discipline；
- Git review；
- 分层目录；

降低风险，但不是完全解决。

### 22.16 评测

Memory 系统不能只看“召回了几条”，还应看：

- useful memory precision；
- stale memory rate；
- memory-as-fact violation；
- contradiction detection；
- repeated-error reduction；
- correction adoption rate；
- experience card hit rate；
- user-specific answer improvement；
- provenance completeness；
- writeback quality；
- dead link / duplicate rate。

### 22.17 当前边界

已实现：

- Git/Markdown/YAML/Obsidian 底座；
- 分层目录；
- frontmatter；
- preflight；
- SessionStart/Stop hook；
- writeback playbook；
- trust boundary；
- per-user JSONL；
- judgments/corrections/checkpoints/verdicts/experience cards；
- 事实与经验分离原则。

不能夸大：

- 不是强一致记忆数据库；
- 不是所有 memory 都有 TTL；
- 不是完整自动贝叶斯仲裁；
- 增强语义检索和冲突消解仍在演进；
- 旧 synthesis 被直接引用的风险仍需治理；
- memory 不等于当前市场事实。

### 22.18 面试表达

#### 30 秒

> 我没有把所有历史对话塞进 prompt，而是把记忆分成 Git/Markdown/YAML 的长期协作资产和项目内 per-user JSONL 学习层。`00_inbox`、knowledge、projects、conventions、playbooks 等目录承担不同生命周期；用户的 judgments、corrections、checkpoints、verdicts 和 experience cards 也分开。Memory 只作为 prior，当前行情和公司事实必须重新检索。另一个重点是 trust boundary：记忆内容是数据，不是可执行指令，防止持久化 prompt injection。

#### 2 分钟

> 多 Agent 项目最大的问题不是模型没有上下文，而是上下文无法治理。我用 Git + Markdown + YAML frontmatter + Obsidian 做共享黑板：原始内容进 inbox，稳定知识进 knowledge，项目状态进 projects，方法流程进 playbooks；SessionStart hook 自动读当前项目记忆，Stop hook 强制判断是否需要分层回写。单次用户反馈不污染项目 MOC，而是进入 corrections、checkpoints、verdicts 和 experience cards。金融场景里 memory 只能提供历史先验，不能直接证明当前订单、价格或产能；冲突时以当前 D/L3 等硬证据为准。另外我明确把 vault 当数据源而不是指令源，未审阅外部内容不能改变 Agent 行为，这也是防持久化 prompt injection。

#### 追问

**问：为什么不直接用 Mem0/向量记忆？**
答：当前首要问题是可读、可审计、分层和信任边界，不是向量搜索性能。以后可在现有 source of truth 上加派生检索层，而不是让黑盒向量库存唯一事实。

**问：怎样删除错误记忆？**
答：不应简单静默覆盖；用 correction、status、superseded/deprecated 和 Git 历史保留审计，再让检索优先当前有效版本。

---

## 23. PIT 与防前视：防止“用未来解释过去”

真实代码和资料：

- `knowledge-base-private/docs/conventions.md`
- `knowledge-base-private/scripts/pit_lib.py`
- `knowledge-base-private/scripts/pit_truncate.py`
- `knowledge-base-private/scripts/audit_pit_timestamps.py`
- `knowledge-base-private/scripts/audit_backfill_embargo.py`
- `finance-workspace-private/intelligence/services/fidelity_contract.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`
- `finance-workspace-private/scripts/bitemporal_history_eval.py`
- `finance-workspace-private/scripts/pit_snapshot_inventory.py`

### 23.1 业务问题

假设你在 3 月 1 日做判断，3 月 10 日有一份公告证实逻辑。

如果历史回放时把 3 月 10 日公告喂给 3 月 1 日模型：

- 回测会显著变好；
- 解释看起来非常合理；
- 但这不是当时可做出的判断。

金融系统中，这叫 look-ahead bias。

### 23.2 第一性原理

“事实何时发生”和“系统何时知道”是两个时间：

```text
valid time / event time
  事实适用于何时

available time / known_at / system time
  系统最早何时可使用
```

还可能有：

```text
publish_time
  来源对外发布时间

ingest_time
  系统实际入库时间
```

决策时点 \(T\) 的证据必须满足：

\[
available\_time \le T
\]

### 23.3 `publish_time` 与 `available_time`

知识库约定：

```yaml
publish_time: YYYY-MM-DD
available_time: YYYY-MM-DD
```

原则：

\[
available\_time \ge publish\_time
\]

默认：

\[
available\_time = \max(publish\_time, ingest\_time)
\]

即：

> 就晚不就早。宁可保守认为晚一点知道，也不能把信息提前。

### 23.4 `pit_lib.py`

核心：

```python
def source_available_time(path):
    available_time
    → publish_time
    → created
    → source_updated
```

```python
def is_available(available, as_of, include_undated=False):
    return available <= as_of
```

```python
def as_of_filter(items, as_of, get_time, include_undated=False):
    return kept, masked
```

无日期来源默认：

```text
exclude
```

这是保守策略，因为无法证明它在 T 时已可得。

### 23.5 `pit_truncate.py`

给定：

```text
--as-of 2026-03-01
```

输出：

- usable；
- masked；
- undated。

它是只读工具，不修改知识库。

### 23.6 时间戳审计

`audit_pit_timestamps.py` 检查：

A. 缺 `publish_time/available_time`；
B. `available_time < publish_time`；
C. 正文证据日期晚于 available time。

为什么 C 很重要：

即使 frontmatter 日期看起来合法，正文可能后来追加了新证据。

例如：

```text
available_time: 2026-03-01
正文却写“2026-03-10 公司公告……”
```

这仍是未来信息污染。

### 23.7 回填 embargo

历史材料回填时：

- delta 的归属日期不得早于 publish time；
- 违例时夹回 publish time；
- 标 `embargo_violation=true`；
- 保留 `embargo_original_date`；
- 不静默修改。

这解决：

> 后来读到一篇老研报，不能把其中结论伪装成系统在更早日期已经知道。

### 23.8 Finance Fidelity Contract

`fidelity_contract.py` 定义：

```text
report_generated_at
evidence_cutoff
decision_cutoff
snapshot_captured_at
generator_commit
run_id
artifact_sha
manifest_sha
```

检查：

```text
evidence_cutoff <= decision_cutoff
evidence_cutoff <= snapshot_captured_at
decision_cutoff <= report_generated_at
snapshot_captured_at <= report_generated_at
```

还把：

- code commit；
- artifact hash；
- manifest hash；
- run id；

绑定到报告。

这让回放不仅知道“用了哪些数据”，还知道“由哪版代码生成”。

### 23.9 Bitemporal replay

严格回放要保存两套视图：

```text
final history
  事后完整、可能有修订

PIT history
  当时真实可见
```

如果只保留最终数据库：

- 后续修正会覆盖当时错误值；
- 回测会用修订后数据；
- 无法证明当时输入。

`bitemporal_history_eval.py` 和 PIT snapshot 相关代码用于构建和比较物理隔离的 PIT 输入。

### 23.10 Claim-level cutoff

`claim_fidelity.py` 为 claim 保存：

- report date；
- location；
- claim type；
- source ref；
- cutoff timestamp；
- verification status；
- cutoff violation。

推荐阈值中：

```text
cutoff_violation_rate == 0
```

说明防前视是硬约束，不是平均指标。

### 23.11 为什么 `unverifiable` 不能算正确或错误

如果历史时点缺乏可验证数据：

```text
unverifiable
```

不能：

- 当 hit；
- 当 miss；
- 为了提高胜率从分母中任意删除；
- 用事后数据补判。

当前回检框架中，`unverifiable` 不计入胜率分母，但仍保留在 due queue 或报告中。

### 23.12 `ask` 当前真实边界

这里必须非常诚实。

知识库和 fidelity/replay 层已经有：

- publish/available time；
- PIT truncate；
- snapshot；
- contract；
- claim cutoff 检查。

但 `ask.py` 当前部分路径仍主要用：

```text
source_date
```

标注 freshness，并明确写出：

> Temporal Facts 层尚未接入；正式版应把会过期/被证伪的事实建成 active/superseded/invalidated 时序边。

所以不能说：

> 整个在线 ask 链路已经完整实现严格 bitemporal retrieval。

准确说法：

> 项目已实现 PIT 工具、时间戳治理、快照和 fidelity contract；但 ask 的所有来源尚未统一贯穿 Temporal Facts，部分仍以 source_date freshness 为主。

### 23.13 异常和降级

| 情况 | 行为 |
|---|---|
| available_time > T | mask |
| 无日期 | 历史回放默认 exclude |
| available < publish | hard issue |
| 正文含未来证据 | audit issue |
| source time > cutoff | cutoff violation |
| 无 PIT source row | unverifiable |
| snapshot/hash 不一致 | contract failure |
| 只有 final history | 不能冒充 PIT |

### 23.14 评测

- timestamp completeness；
- available >= publish violation count；
- future evidence count；
- cutoff violation rate；
- PIT/final partition errors；
- PIT source row coverage；
- snapshot reproducibility；
- artifact/manifest hash validation；
- claim evidence coverage；
- unverifiable rate；
- same input + commit replay consistency。

### 23.15 当前边界

已实现：

- publish/available time 约定；
- audit；
- PIT truncate；
- embargo；
- snapshot；
- fidelity contract；
- bitemporal eval 工具；
- claim cutoff violation；
- unverifiable 语义。

不能夸大：

- ask 全链未完全 Temporal Facts 化；
- 不是所有历史材料都有完整 PIT 快照；
- 后补数据不能自动证明当时可见；
- 完整 valid-time/system-time revision log 仍在演进；
- 有框架不等于所有历史样本都已充分回放。

### 23.16 面试表达

#### 30 秒

> 金融 Agent 必须防前视，所以我区分 `publish_time`、`available_time` 和事实的 valid time。历史决策点 T 只能使用 `available_time <= T` 的来源，无日期默认保守屏蔽。项目里有 PIT truncate、时间戳审计、回填 embargo、每日 snapshot 和 fidelity contract，报告还绑定 code commit、artifact hash 和 evidence cutoff。需要诚实说明：这些能力已在知识库和回放层落地，但在线 ask 还没有把所有来源统一成完整 Temporal Facts。

#### 2 分钟

> 历史研究最容易出现“事后正确、事前不可得”。我先把材料发布时间和系统可得时间分开，要求 available time 不早于 publish time；回放时只保留 available time 小于等于决策点 T 的来源，无日期默认排除。审计不仅看 frontmatter，还检查正文是否后来追加了晚于 available time 的证据。回填历史材料时有 embargo，不能把研报结论归属到发布前。Finance 侧进一步用 fidelity contract 绑定 evidence cutoff、decision cutoff、snapshot time、code commit、run id 和 artifact hash，并在 claim 级检查 cutoff violation。当前边界是 ask 仍有部分路径主要按 source_date 做 freshness，完整 active/superseded/invalidated Temporal Facts 还没有贯穿所有在线来源。

#### 追问

**问：publish time 和 available time 为什么不同？**
答：材料可以早已发布但系统后来才获取；历史回放应按系统真正可使用时间，而不是对外发布时间。

**问：只保存日期够吗？**
答：日频研究可先用日期，但更严格场景要 timestamp、交易时段、时区和 snapshot captured time。

---

## 24. 可观测性与回放：怎样知道一次回答到底发生了什么

真实代码：

- `finance-workspace-private/intelligence/services/run_store.py`
- `finance-workspace-private/intelligence/api/app.py`
- `finance-workspace-private/intelligence/api/stream_events.py`
- `finance-workspace-private/intelligence/services/agent.py`
- `finance-workspace-private/intelligence/services/research_brief.py`
- `finance-workspace-private/intelligence/services/kb_rag.py`
- `finance-workspace-private/intelligence/services/closed_loop_retrieval.py`
- `finance-workspace-private/intelligence/webapp/src/App.tsx`
- `finance-workspace-private/intelligence/webapp/src/api.ts`

### 24.1 业务问题

用户只看到一段答案时，系统故障可能来自：

- Router 选错；
- Planner 漏了必要来源；
- DuckDB 查询失败；
- RAG timeout；
- index stale；
- entity anchor 错；
- LLM 调用失败；
- reviewer 发现 warning；
- 用户取消；
- 进程重启导致中断。

如果不记录中间过程，只能猜。

### 24.2 第一性原理

可观测性至少要回答：

```text
发生了什么？
什么时候发生？
由哪个输入触发？
调用了什么工具？
用了哪版数据和代码？
哪里降级？
最终输出对应哪次运行？
```

对于 Agent，还要区分：

- model decision；
- tool execution；
- final answer；
- user feedback。

### 24.3 Run 目录、append-only Trace 与 Stream

`RunStore` 使用：

```text
intelligence/users/<id>/runs/<run_id>/
  run.json
  trace.jsonl
  stream.jsonl
  answer.md / summary.json / report.json ...
```

其中：

- `run.json` 是当前 run 元数据和 artifacts 清单，由单写入者更新；
- `trace.jsonl` append-only 保存模块步骤；
- `stream.jsonl` append-only 保存有 seq 和 event id 的流事件；
- answer、summary、report 等作为 artifact 保存并记录 SHA-256。

为什么 trace/stream append-only：

- 崩溃后历史仍在；
- 不覆盖旧状态；
- 易审计；
- 每次状态转换有 trace。

为什么 `run.json` 采用当前状态快照：

- 单个 run 的元数据很小；
- 获取当前终态无需扫描整条事件流；
- 详细过程仍由 append-only trace/stream 保留。

### 24.4 状态恢复

如果服务启动时发现：

```text
queued / running
```

`requeue_incomplete_runs(...)` 会：

```text
标记 degrade reason = service_restarted
→ 状态改回 queued
→ 追加 run_recovered stream event
→ 尝试恢复 conversation run
→ 否则重新提交任务
```

因此当前真实语义是“可重排队恢复”，不是简单标成 `interrupted`。

### 24.5 SSE

API：

```text
GET /api/runs/{run_id}/events
```

以 SSE 推送：

```text
trace events
run snapshot
```

前端 `App.tsx`：

- 打开 `EventSource`；
- 解析事件；
- 更新结构化消息和 run；
- 收到 completed/failed/cancelled 后关闭；
- 同时每 2 秒 polling reconcile；
- SSE error 时标记 reconnecting，并立即做状态对账。

为什么 SSE 而不是 WebSocket：

- 当前主要是服务端单向推送；
- HTTP 语义简单；
- 浏览器原生 EventSource；
- 自动重连能力；
- 比双向 WebSocket 更轻。

什么时候需要 WebSocket：

- 双向实时交互；
- 高频控制消息；
- 多路复用复杂协议；
- 更低延迟交互。

### 24.6 Workbench step trace 与 Agent tool-call trace

Workbench 的 `api/app.py` 用：

```text
append_step(
  step_id,
  name,
  status,
  input_summary,
  output_summary,
  warnings,
  retrieval
)
```

记录：

- `ask_retrieve_compose`；
- `render_artifacts`；
- `foresight_followups`；
- 每步开始/结束、warning、retrieval 摘要。

独立的 `AgentSession` 则在工具调用循环中保存：

```text
AgentStep(
  tool,
  args,
  result_preview
)
```

默认：

```python
DEFAULT_MAX_STEPS = 6
```

每轮把 assistant tool call 和 tool result 加回 messages。步数用完后，系统会发送 tool-free final nudge 强制收尾。

步数限制的意义：

- 防止工具循环；
- 控制成本；
- 明确失败。

### 24.7 Retrieval telemetry

W 源 telemetry：

- mode；
- recall description；
- index kind；
- index dir；
- latency；
- status；
- hit count；
- neighbor hits；
- score max/min/mean；
- index built time；
- revision；
- freshness；
- degraded；
- warning。

Research telemetry：

- source distribution；
- wiki pages；
- top/mean score；
- L3 lookup items；
- L3 coverage；
- final verdict。

Closed-loop telemetry：

- aperture；
- query；
- attempt status；
- hit count；
- bucket counts；
- warnings。

D block telemetry：

- attempted；
- empty/error/ok；
- rows；
- latency；
- warning。

### 24.8 决策与最终输出分离

必须保存：

```text
QuestionPlan / route / tool calls / evidence audit
```

而不仅是最终文本。

原因：

同一证据可能被两个模型写成不同答案；
同一答案也可能来自不同证据。

如果只存文本，无法做：

- planner error analysis；
- retrieval replay；
- model A/B；
- reviewer evaluation；
- source-level attribution。

### 24.9 日志中不能有什么

不能记录：

- PAT；
- LLM API key；
- cookie；
- 完整敏感 header；
- 用户不应持久化的隐私内容。

tool args 也应做脱敏。

### 24.10 异常和降级

| 情况 | 行为 |
|---|---|
| 服务重启 | active run requeue，记录 `run_recovered`，尝试恢复/重提 |
| SSE 断开 | 标 reconnecting，同时 polling reconcile |
| 用户取消 queued run | future.cancel + cancelled |
| 用户取消 running run | cancellation signal + status cancelled |
| backend exception | run failed + error trace |
| trace/stream JSONL 坏行 | 视为数据完整性错误；当前读取并非逐行容错 |
| LLM 达到默认 6 步上限 | 强制 tool-free 收尾；无答案才失败 |
| retriever degraded | telemetry 记录，不伪装 ok |

### 24.11 评测

可观测性本身也要测：

- trace completeness；
- run terminal-state correctness；
- restart recovery；
- SSE reconnect；
- polling fallback；
- event ordering；
- correlation id coverage；
- secret leakage scan；
- telemetry schema stability；
- replay reproducibility。

### 24.12 当前边界

已实现：

- per-run `run.json` + append-only `trace.jsonl` / `stream.jsonl`；
- incomplete run requeue/resume；
- SSE；
- polling reconciliation；
- tool-call trace；
- retrieval telemetry；
- D block 统计；
- degraded reason。

不能夸大：

- JSONL 不是高并发日志数据库；
- 没有完整分布式 tracing backend；
- 没有证据表明所有内部操作都已统一 OpenTelemetry；
- 多进程并发写入和 retention 仍需更强治理；
- Workbench 默认本地，不是生产可观测平台。

### 24.13 面试表达

#### 30 秒

> 我把 Agent 运行过程作为一等数据保存，而不是只存最终答案。每个 run 有 `run.json` 当前状态、append-only 的 `trace.jsonl` 和 `stream.jsonl`，以及带 hash 的 answer/report artifacts；服务重启后未完成 run 会重新排队并记录 `run_recovered`。前端通过 SSE 看实时事件，同时用 polling 对账。这样可以区分是规划错、检索失败、模型失败还是 reviewer 降级。

#### 2 分钟

> Agent 的难点是错误会跨越路由、工具和生成多个阶段，所以最终文本不足以排障。我的 RunStore 为每个 run 保存当前 `run.json`，把模块步骤 append 到 `trace.jsonl`，把带 seq/event id 的实时事件 append 到 `stream.jsonl`，artifacts 记录 SHA-256。服务重启时 queued/running 会 requeue，并尝试恢复 conversation 或重提任务，同时追加 `run_recovered`。API 用 SSE 推送 trace 和结构化事件，前端同时定时 polling 做状态对账。检索侧还记录 mode、index revision、freshness、延迟、score、neighbor hits 和每个 narrow/broad/counter attempt，D block 记录 attempted/empty/error/ok。

---

## 25. L3 官方证据、Research Judge 与 Research Queue

真实代码：

- `finance-workspace-private/intelligence/services/l3_evidence.py`
- `finance-workspace-private/intelligence/services/research_judge.py`
- `finance-workspace-private/intelligence/services/research_queue.py`
- `finance-workspace-private/intelligence/services/forecast_preflight.py`

### 25.1 业务问题

知识库中命中“某公司受益”不代表公司已经兑现。

研究需要进一步判断：

- 是否有公告、订单、中标、量产、认证；
- 目前证据层到哪；
- 下一步最值得补什么；
- 是否可以生成正式复盘；
- 还是只能输出草稿。

### 25.2 L3 lookup 的设计

接口：

```python
def lookup_l3_evidence(
    query: str,
    plan: QuestionPlan,
    local_evidence_text: str,
    *,
    config: L3LookupConfig | None = None,
) -> L3EvidenceBundle:
```

配置：

```python
@dataclass(frozen=True)
class L3LookupConfig:
    enabled: bool = False
    company_cmd: str | None = ...
    cninfo_cmd: str | None = None
    sse_einteract_cmd: str | None = None
    timeout: int = 480
    limit: int = 5
    days: int = 30
```

### 25.3 为什么默认关闭

官方查证可能：

- 需要外部命令和环境；
- 延迟高；
- 上游不稳定；
- API 覆盖不完整；
- 不适合所有问题。

因此采用 opt-in：

- `ask --l3-lookup`；
- 或环境变量开启。

没有开启时，系统应降级结论，而不是假装查过。

### 25.4 “查不到 L3”不等于“题材没有驱动”

L3 lookup 主要判断：

> 公司端兑现度。

题材驱动可能来自：

- 行业政策；
- 上游价格；
- 竞争格局；
- 主题资金；
- 预期变化。

所以：

```text
没有公司公告
≠
没有题材逻辑
```

正确口径：

```text
题材可能存在，但公司端缺少官方兑现证据。
```

### 25.5 Research Judge

`judge_research_target(...)`：

- 查 entity exposure；
- 读取 evidence；
- 可注入 L4 market signal；
- 归类 L0-L4；
- 计算已有/缺失层；
- 给不可升级原因；
- 给下一步动作。

它不是预测裁判，而是：

> 研究成熟度和证据状态判断器。

### 25.6 Research Queue

队列：

```text
today_do_ima
today_find_official_evidence
today_wait_market_validation
today_downgrade_or_watch
```

典型逻辑：

```text
有盘面、没有基础证据
→ today_do_ima

有 L1，缺 L2/L3
→ today_find_official_evidence

有 L2/L3，缺 L4
→ today_wait_market_validation

生命周期转弱
→ today_downgrade_or_watch
```

这把“下一步研究什么”从自然语言建议变成队列。

### 25.7 Forecast Preflight

状态：

```text
ready
needs_deepdive
missing_daily_agent
```

如果：

- 没有 daily-agent research queue；
- 或仍有 `today_do_ima`；
- 或仍有 `today_find_official_evidence`；

则：

```text
can_generate_formal = False
can_generate_draft = True
```

即：

> 可以生成带缺口的草稿，但不能生成正式复盘。

### 25.8 为什么这是好的 Agent 设计

普通聊天模型会：

```text
证据不足
→ 仍给完整结论
```

Research Queue 会：

```text
证据不足
→ 转化成明确任务
→ 补证据
→ 等市场验证
→ 再升级结论
```

这使 Agent 从“答案机器”变成“研究流程系统”。

### 25.9 异常和降级

L3 subprocess 处理：

- timeout；
- OSError；
- non-zero；
- parse failure；
- no evidence；
- cache；
- warning。

Research Judge 缺关系或证据时：

- 输出 blocking reason；
- 不升级研究阶段。

Preflight 缺 daily-agent 时：

- 阻止 formal；
- 允许 gap-aware draft。

### 25.10 评测

- L3 lookup coverage；
- L3 false-positive rate；
- judge layer accuracy；
- queue action usefulness；
- formal report gate precision；
- draft-to-formal promotion time；
- unresolved blocking gap；
- 同一 target 的状态转移正确性。

### 25.11 当前边界

已实现：

- opt-in L3 lookup；
- timeout/cache/degrade；
- Research Judge；
- Research Queue；
- Forecast Preflight；
- formal vs draft gate。

不能夸大：

- L3 默认关闭；
- 外部官方数据覆盖不完整；
- Judge 不是自动预测正确性裁判；
- Queue 分类仍有启发式；
- formal gate 不代表投资结论正确，只代表研究前置条件满足。

### 25.12 面试表达

#### 30 秒

> 我把“有没有证据”进一步转成研究状态机。L3 工具可选查公告和交易所互动，用来验证公司端兑现；Research Judge 判断当前有 L1/L2/L3/L4 哪些层，Research Queue 再把缺口转成今天做 IMA、找官方证据、等盘面验证或降级观察。Forecast Preflight 在关键任务未完成时只允许生成带缺口草稿，不允许正式复盘。

#### 2 分钟

> RAG 命中只是线索，金融研究还要判断证据是否成熟。我把公司官方证据做成 opt-in L3 lookup，因为它延迟高且依赖外部命令，失败时只 warning，不影响其他来源；同时明确“查不到公告”只表示公司端未确认，不等于题材没驱动。之后 Research Judge 对目标做证据层盘点，Research Queue 把缺口转成可执行任务，比如有盘面无基础证据就做 IMA，有 L1 但缺 L2/L3 就找官方材料，有硬证据但无盘面就等市场验证。正式复盘前还有 Forecast Preflight，阻塞项未清时只能出草稿。这样系统不会把证据不足包装成完整结论。

---

## 26. 编排与风险门控：金融 Agent 为什么不能完全自由执行

真实代码：

- `finance-workspace-private/intelligence/workflows/agent_orchestrator.py`
- `finance-workspace-private/intelligence/api/app.py`
- `finance-workspace-private/intelligence/services/agent.py`
- `finance-workspace-private/intelligence/services/run_store.py`

### 26.1 业务问题

Agent 工具可能：

- 读本地文件；
- 运行脚本；
- 调外部 API；
- 生成数据；
- 导入知识；
- 修改状态。

自然语言理解出错时，如果直接执行：

- 可能使用错日期；
- 运行耗时命令；
- 写错目标；
- 重复导入；
- 产生不可逆影响。

### 26.2 第一性原理

模型的置信度不是权限。

执行权应由：

```text
意图
∩ 参数完整
∩ 工具声明
∩ 风险等级
∩ 策略阈值
∩ 用户授权
```

共同决定。

### 26.3 默认 preview

`OrchestratorOptions`：

```python
execute: bool = False
```

默认只：

- 生成计划；
- 展示命令；
- 标记风险；
- 说明 skip reason。

这是 safe-by-default。

### 26.4 自动执行门

```python
MIN_AUTO_EXECUTION_CONFIDENCE = 0.7
```

且要求：

```text
argv 存在
auto_execute = true
risk_level = low
confidence >= 0.7
skip_reason 为空
```

任何一项不满足都不执行。

### 26.5 为什么不能只看 confidence

模型可能对错误工具高度自信；
低风险工具和高风险工具也不应共用一个决策。

例如：

```text
读取只读市场快照
```

与：

```text
写知识库、删除数据、触发外部动作
```

风险完全不同。

### 26.6 Tool schema

工具有：

- name；
- description；
- JSON schema；
- handler。

schema 负责：

- 参数类型；
- required fields；
- enum；
- 默认值。

模型只产生结构化 args，真正执行前仍由程序解析。

### 26.7 取消与可恢复

Run API 支持：

- queued 取消；
- running 设置 cancellation signal；
- run 终态立即写 cancelled；
- 尝试 `future.cancel()` 取消尚未开始的任务；
- 最终 cancelled/failed/completed；
- 重启后 active run requeue/resume。

为什么不是强杀线程：

- Python 线程强杀不安全；
- 工具可能正持有文件或 subprocess；
- cooperative cancellation 更可控。

### 26.8 金融系统的风险分层建议

| 风险 | 例子 | 建议 |
|---|---|---|
| read-only low | 查询行情、读 wiki | 可在高置信时自动 |
| compute medium | 大规模重建索引、长回测 | preview + 资源限制 |
| write medium/high | 写 relations、写记忆 | dry-run + schema + review |
| external high | 发消息、交易、资金动作 | 明确人工确认 |

当前项目仍处研究员阶段，没有接交易执行。

### 26.9 当前边界

已实现：

- preview/dry-run；
- `execute=False`；
- low risk gate；
- auto_execute；
- confidence threshold；
- skip reason；
- tool schema；
- cooperative cancel。

不能夸大：

- 0.7 未必经过统计校准；
- 不是完整 RBAC/ABAC；
- 没有生产级 sandbox；
- 没有交易执行；
- 不能把研究建议说成可自动下单动作。

### 26.10 面试表达

#### 30 秒

> 我把模型规划和执行权限分开。Orchestrator 默认 `execute=False`，先输出 preview；只有工具有 argv、声明可自动执行、风险为 low、置信度至少 0.7 且没有缺参或 skip reason 时才执行。高风险或写操作需要更强的人工确认。当前系统停留在研究员层，不接交易，所以不会把自然语言观点直接转成下单。

#### 2 分钟

> Agent 的模型置信度不能等同于权限。我让每条路径有风险等级、auto_execute 声明和参数 schema，Orchestrator 默认只生成计划和命令。自动执行必须同时满足低风险、置信度阈值、参数完整和无 skip reason；用户也可取消，running 任务通过 cooperative flag 停止。这个设计把“模型认为应该做”与“系统允许做”分开。尤其金融场景里，研究、写入和交易必须是不同权限层级；当前只实现研究工作台，没有自动下单。

---

## 27. 评测与学习闭环：从一次回答到长期改进

真实代码和数据：

- `knowledge-base-private/skills/lib/rag/evaluate.py`
- `finance-workspace-private/intelligence/eval/claim_fidelity.py`
- `finance-workspace-private/intelligence/services/checkpoints.py`
- `finance-workspace-private/intelligence/services/checkpoint_resolvers.py`
- `finance-workspace-private/intelligence/services/checkpoint_recall.py`
- `finance-workspace-private/intelligence/services/corrections.py`
- `finance-workspace-private/intelligence/services/experience_cards.py`
- `finance-workspace-private/intelligence/services/user_memory.py`
- `finance-workspace-private/intelligence/users/<user>/*.jsonl`

### 27.1 业务问题

一个回答“看起来不错”无法证明：

- 检索找对了；
- 引用支持 claim；
- 没用未来信息；
- 预测后来命中；
- 用户纠偏被吸收；
- 系统没有重复犯错。

必须按层评测。

### 27.2 分层评测框架

```text
Router evaluation
→ Plan evaluation
→ Retrieval evaluation
→ Evidence evaluation
→ Generation/review evaluation
→ Historical outcome evaluation
→ Memory calibration
```

如果只看最终用户评分，无法知道改哪里。

### 27.3 检索评测

已有：

- Recall@k；
- hit@k；
- MRR；
- BM25/dense/hybrid/rerank；
- aliases；
- suffix normalization；
- recall ceiling。

建议再补：

- nDCG；
- aperture-specific recall；
- L3 source recall；
- stale hit rate；
- latency；
- no-hit reason distribution。

### 27.4 回答评测

可以看：

- citation coverage；
- citation correctness；
- evidence layer coverage；
- unsupported claim rate；
- faithfulness；
- answer spec compliance；
- counterevidence coverage；
- gap disclosure；
- output review violation rate。

### 27.5 Claim fidelity

Claim 类型：

```text
number
entity
classification
fact
inference
forecast
```

verification status：

```text
matched
mismatch
missing
unverifiable
needs_review
```

推荐阈值示例：

```text
numeric_match_rate >= 0.99
entity_classification_accuracy >= 0.95
evidence_coverage_rate >= 0.95
cutoff_violation_rate == 0
fact_inference_confusion_rate <= 0.05
```

这些是推荐契约目标，不等于当前所有历史样本已经达到。

### 27.6 历史盲测

正确盲测：

```text
冻结 T 时点输入
→ 生成 prediction/checkpoint
→ 等待 T+1/T+3/T+5
→ 获取真实 outcome
→ 记录 verdict
```

不正确：

```text
先看到结果
→ 再选择当时“看起来合理”的证据
```

### 27.7 Checkpoint

Checkpoint 应包含：

- claim；
- metric；
- operator；
- threshold；
- target date/window；
- data source；
- status。

例如：

```text
T+3 板块相对强度仍为正
T+5 出现 L3 公告或互动确认
若跌破某相对强度条件则 thesis 降级
```

可验证假设比：

```text
“后续继续关注”
```

更有评测价值。

### 27.8 Verdict

```text
hit
miss
partial
unverifiable
```

`unverifiable`：

- 数据缺失；
- 指标无法获得；
- 条件定义不清；
- PIT 无法证明。

它不应进入胜率分母。

### 27.9 Experience Card

从多次结果提炼：

```text
trigger
context
mistake pattern
evidence
lesson
applicable conditions
counterexamples
```

好的 experience card：

> 当题材强、公司只有 graph exposure 而无 L3 时，把它写成核心受益容易产生 miss；下次必须同时检查公司兑现和相对强度。

坏的 experience card：

> 不要犯错，要多看数据。

### 27.10 Correction calibration

用户纠错不应只保存原句，还要判断：

- 属于事实错误；
- 口径错误；
- 用户偏好；
- 过度自信；
- 缺反证；
- 时效问题。

然后观察后续相同 error tag 是否下降。

### 27.11 Checkpoint calibration

检查：

- checkpoint 是否按时到期；
- metric 是否可取得；
- 自动 resolver 是否可靠；
- `unverifiable` 是否过多；
- threshold 是否过宽/过窄；
- hit/miss 是否存在口径漂移。

### 27.12 评测闭环

```text
query
→ plan/retrieval/answer
→ user score/correction
→ checkpoint
→ outcome verdict
→ experience card
→ 更新 prompt/rule/retrieval/queue
→ 下一轮对比
```

注意：

> 写入 experience card 不等于系统已经自动学会。还要确保检索和策略实际会消费它。

### 27.13 指标不能混用

高 Recall@k 不等于回答可靠：

- 可能召回对页但模型没用；

高 faithfulness 不等于结论正确：

- 可能忠实复述了一篇错误研报；

高历史 hit rate 不等于无前视：

- 可能用了未来证据；

用户喜欢不等于事实正确：

- 可能只是表达符合偏好。

必须同时看：

```text
检索
× 来源质量
× claim fidelity
× PIT
× outcome
```

### 27.14 当前边界

已实现：

- RAG eval；
- output review；
- claim fidelity；
- cutoff violation；
- checkpoints；
- verdicts；
- experience cards；
- correction/checkpoint calibration 框架；
- historical replay 脚本。

不能夸大：

- 有评测框架不等于已有充分样本；
- RAG 真实效果仍需人工标注；
- 预测胜率没有充分、无偏、长期统计证明；
- 自动 verdict 只适合可确定解析的条件；
- 大量语义判断仍需人工 gold；
- unverifiable 不能被隐藏。

### 27.15 面试表达

#### 30 秒

> 我按层评测，而不是只看最终回答。检索层有 Recall@k、hit@k、MRR 和 BM25/dense/hybrid/rerank 对比；答案层看引用覆盖、证据层、claim fidelity 和 output review；历史层把结论转成 T+1/T+3/T+5 checkpoint，再记录 hit、miss、partial、unverifiable，其中 unverifiable 不进胜率分母。用户纠偏会进入 correction 和 experience card，但我会区分“已实现闭环框架”和“已有充分统计证明”。

#### 2 分钟

> Agent 评测必须拆层。Router 错和 retriever 错需要不同修复；检索命中也不代表生成忠实。因此知识库用 Recall@k、hit@k、MRR 和 recall ceiling 比较 BM25、dense、hybrid、rerank；生成侧把文本拆成 number/entity/fact/inference/forecast claim，检查证据覆盖、数字匹配和 cutoff violation；研究结论再转成有指标、阈值和窗口的 checkpoint，未来记录 hit/miss/partial/unverifiable。用户纠偏按错误类型校准，重复模式再提炼 experience card。当前我有这套工程框架，但不会声称已经有足够大的无偏样本证明预测 alpha。

---

## 28. 一道真实问题的全链路拆解

问题示例：

> “A 公司最近为什么强？是液冷核心受益，还是只在跟题材？”

### 28.1 澄清

需要确认：

- A 公司具体名称/ticker；
- “最近”是 3 日、5 日还是 20 日；
- 用户要快速判断还是深挖；
- 是否关心交易时点。

如果 ticker 唯一且默认窗口可接受，系统可继续；否则请求澄清。

### 28.2 Router

这是：

```text
planner_analysis
```

而不是命令型 known workflow。

### 28.3 QuestionPlan

```text
question_type = stock_deep_dive
required_lenses:
  - company_identity
  - theme_exposure
  - market_validation
  - evidence_hardness
  - peer_comparison
  - counterevidence
  - verification_window

retrieval_plan:
  S/G/R/W/D
  L3 optional
  M/V as prior/calibration
```

### 28.4 Entity Anchor

输出：

```text
entity = A公司
ticker = 000000.SZ
concepts = [液冷, 数据中心...]
graph_query = ...
```

如果只识别到简称但多个公司冲突：

```text
clarification
```

### 28.5 S

查看：

- 当天是否进入题材候选；
- 相对板块强弱；
- 是否连续；
- 是个股独立强还是板块共振。

S 只能证明盘面在交易。

### 28.6 G/R

G：

- 是否有公司—液冷 exposure；
- 关系是 direct、indirect 还是 graph_only。

R：

- 关系对应什么 source；
- evidence layer；
- source trace。

如果只有 graph_only：

```text
只能作为候选，不直接作为基本面依据。
```

### 28.7 W closed-loop

narrow：

```text
A公司 + ticker
```

broad：

```text
A公司 液冷 上下游 同业
A公司 数据中心 竞争格局
```

counter：

```text
A公司 液冷 风险 证伪 不及预期
A公司 替代 竞争 受损
```

结果分为：

- conclusion；
- clues；
- counter clues；
- discarded。

### 28.8 D

可能运行：

- D0：近几日走势和相对强度；
- D1：同链替代队列；
- D4：题材结构；
- D6：多日趋势；
- D7：财务趋势；
- D5：估值；

按问题深度决定。

### 28.9 L3

如果开启：

- 查公告；
- 互动易；
- 公司命令；
- 最近 30 日、limit 5。

没有官方证据时：

```text
不能说公司订单已兑现。
```

### 28.10 M/V

M：

```text
用户过去曾认为 A 是核心
```

作为 hypothesis。

V：

```text
过去类似“graph exposure + 盘面强、无 L3”的判断结果如何
```

用于校准语气，不覆盖当前事实。

### 28.11 Evidence Audit

假设得到：

```text
L1：题材逻辑存在
L2：卖方认为公司有相关产品
L3：无
L4：盘面连续强于板块
E：用户过去看好
```

结论只能是：

```text
预期交易 + 盘面验证
```

不能是：

```text
公司核心受益已确认
```

### 28.12 Counter Plan

最强反证：

- 同链更纯标的更强；
- A 仅跟涨、板块退潮即掉队；
- 公司无订单/量产；
- 估值已经抢跑；
- 客户证据不足。

验证：

```text
T+1：相对强度、是否掉队
T+3：板块扩散和边际量
T+5：是否出现 L3、超额是否维持
```

### 28.13 AnswerSpec

必须输出：

```text
结论：候选/预期交易，不是事实确认
证据链：S/G/R/W/D 分开
反证：至少最强一条
缺口：无 L3
验证点：T+1/T+3/T+5
引用：chunk/revision/source
```

### 28.14 Output Review

Reviewer 检查：

- 是否写成“核心受益已确认”；
- 是否忘记 L3 缺口；
- 是否把用户 memory 当事实；
- 是否没有反证；
- 是否使用 stale W；
- 是否给不可验证泛话。

### 28.15 最终回答示例

> **结论**：当前更适合定义为“液冷链条的预期交易候选，且盘面已有验证”，还不能定义为“公司端兑现已确认的核心受益”。
> **支持**：公司与液冷存在图谱暴露，知识库有产品关联材料，近 5 日相对板块强度提升。
> **关键缺口**：尚未命中订单、量产、认证或公告类 L3，公司纯度和收入弹性仍待验证。
> **反证**：若同链更纯标的持续更强、A 在板块回落时快速掉队，则当前上涨更可能是题材跟随。
> **验证**：T+1 看相对强度；T+3 看板块扩散和量价持续；T+5 查官方证据与超额收益。

### 28.16 这道题体现的系统能力

- Router 没有自由乱跑工具；
- Planner 确保看公司、盘面、硬度和反证；
- 多源标签防止 memory/研报/盘面混写；
- RAG 负责发现，不负责直接认证；
- DuckDB 负责数字；
- L3 负责公司兑现；
- Review 负责降级口径；
- Checkpoint 负责未来验证。

---

## 29. 项目选型的核心 trade-off

### 29.1 自研轻量编排 vs Agent 框架

选择当前 Python dataclass/module：

- 调试透明；
- 依赖少；
- 控制风险；
- 本地工具适配直接。

代价：

- 状态机和持久化要自己写；
- DAG 可视化弱；
- 节点规模增大后维护成本上升。

何时考虑 LangGraph 等：

- 大量持久化节点；
- 复杂人工中断；
- 多分支恢复；
- 跨进程 worker；
- 图级可观测性。

### 29.2 Markdown/Git vs 数据库知识管理

选择 Markdown/Git：

- 人工审阅和审计强；
- 与 Obsidian 协作；
- 适合低并发。

代价：

- schema 弱；
- 并发写冲突；
- 查询效率有限。

### 29.3 NumPy RAG vs 向量数据库

选择 NumPy：

- 当前规模足够；
- 简单可重建；
- 零服务运维。

代价：

- 全量暴力搜索；
- metadata filter 能力弱；
- 并发和水平扩展弱。

### 29.4 Subprocess 跨仓调用 vs Python package

选择 subprocess：

- 仓库解耦；
- CLI 是稳定边界；
- 环境隔离；
- 易 graceful degrade。

代价：

- 启动开销；
- JSON 协议；
- 路径和依赖复杂；
- 多次 aperture 重复加载模型/索引风险。

改进方向：

- 长驻 retrieval service；
- 或将知识库 RAG 发布为版本化 Python package；
- 批量接收 narrow/broad/counter queries；
- 缓存模型和 index。

### 29.5 Rule-first vs LLM-first

Rule-first 用于：

- 风险；
- schema；
- 日期；
- freshness；
- evidence gate。

LLM-first 用于：

- 开放语义；
- 解释；
- query rewrite；
- synthesis。

代价：

- 规则可能漏长尾；
- LLM 路径仍需维护。

混合方式是当前更合理平衡。

### 29.6 Advisory vs blocking review

当前 advisory：

- 可用性高；
- 便于收集误报。

代价：

- warning 后仍可能输出；
- 高风险场景不够强。

演进：

```text
规则分级
→ 高精度硬错误 blocking
→ 语义弱告警 advisory
```

### 29.7 本地个人工作台 vs 生产 SaaS

当前适合：

- 单人研究；
- 本地数据；
- 快速迭代；
- 可审阅。

生产化仍需要：

- auth；
- tenant isolation；
- secret management；
- rate limit；
- job queue；
- durable database；
- object storage；
- observability backend；
- SLO；
- disaster recovery；
- data license/compliance。

---

## 30. 面试官高频项目追问与标准回答

### 30.1 “你的项目里 LLM 到底负责什么？”

> LLM 负责开放语义理解、问题改写、证据组织、反证表达和最终语言；事实查询、风险门禁、日期、新鲜度、数值、证据层和输出契约由确定性代码负责。默认 ask 甚至可以不依赖外部 LLM，用模板输出真实检索结果；LLM synthesis 是可选增强。

### 30.2 “如果不用 LLM，为什么还叫 Agent？”

> Agent 的关键是目标驱动的规划、工具调用、记忆和反馈，不是每一步都必须由 LLM。我的系统有规则/Planner 路由、按计划调用多源工具、保存运行状态、review 和回检；LLM 是其中的概率推理组件，不是系统全部。

### 30.3 “你的 RAG 比普通向量库强在哪里？”

> 它包括内容治理、section chunking、BM25+dense、RRF、精确实体 boost、wikilink 邻居、可选 cross-encoder、新鲜度和 snapshot binding；并且 W 只作为候选源，后面还有证据层、反证和 claim lineage。

### 30.4 “怎么防止幻觉？”

> 不靠一句“请勿幻觉”的 prompt，而是分层：事实来自 D/G/R/L，W 是候选，M 是 prior；缺 L3 就降级措辞；引用绑定 chunk/hash/revision；Output Review 检查弱证据硬写；数字 claim 做 fidelity；检索失败显式 degraded。

### 30.5 “怎么防止前视？”

> 区分 publish time、available time 和 valid time，T 时点只用 available time 不晚于 T 的来源；无日期默认排除；保存 PIT snapshot 和 evidence cutoff，并检查 claim source time 是否越界。当前边界是在线 ask 尚未把所有来源统一成完整 Temporal Facts。

### 30.6 “Memory 怎么避免污染事实？”

> Memory 的 provenance 和类型必须保留；用户 judgment、experience card 只作 prior，当前行情和公司事实重新查 D/L3；冲突时硬证据优先，并把冲突写 correction。

### 30.7 “为什么不微调一个模型解决？”

> 项目主要问题是实时事实、工具、PIT、引用和审计，不是仅靠参数知识能解决。微调可改善风格、分类或工具选择，但不能替代不断变化的数据和 deterministic control。当前也没有已核实的 LoRA/QLoRA 训练。

### 30.8 “项目最大技术难点是什么？”

> 不是接一个模型 API，而是让多源证据在语义上不混写：盘面、图谱、研报、官方事实、用户记忆和历史 outcome 都可能支持同一叙事，但权限和时效不同。我通过 source tag、evidence layer、freshness、PIT、review 和 claim lineage保持边界。

### 30.9 “怎样证明项目有价值？”

> 当前最能证明的是工程可审计性：可以看到每个来源、检索尝试、warning、引用、反证和回放；RAG 有离线指标框架，回答有 claim fidelity 和 review，预测有 checkpoint/verdict。不能声称已经证明持续投资 alpha，真实效果仍需更长历史盲测和人工标注。

### 30.10 “如果给你三个月继续做，会做什么？”

优先顺序：

1. 建真实 query + evidence 人工 gold set；
2. 把 ask 所有来源统一接入 PIT/Temporal Facts；
3. 校准 Router、Review 和自动执行阈值；
4. 把跨仓 subprocess RAG 改为长驻服务或批量接口；
5. 建 claim-level citation correctness eval；
6. 扩展严格历史盲测；
7. 建 memory TTL/superseded/conflict resolution；
8. 再考虑生产 auth、queue 和 observability。

---

## 31. 真实实现证据速查表

| 能力 | 关键文件 | 面试可说 | 不能说 |
|---|---|---|---|
| Question Router | `intelligence/services/question_router.py` | 四类路由、clarification/data gap/planner | 已训练专用 Router |
| Answer Planner | `intelligence/services/answer_orchestrator.py` | `QuestionPlan`、lenses、gates、contract | 通用自主 DAG 优化器 |
| Ask 主链 | `intelligence/services/ask.py` | 多源检索、组装、review | 每次都运行全部来源 |
| 风险门控 | `intelligence/workflows/agent_orchestrator.py` | preview、low risk、0.7、execute false | 完整生产权限系统 |
| Hybrid RAG | `skills/lib/rag/retrieval.py` | BGE dense + 独立 BM25 + RRF | BGE dense+sparse 已联合生产 |
| Chunking | `skills/lib/rag/chunking.py` | section、breadcrumb、overlap、hash | 自动保证事实正确 |
| Rerank | `skills/lib/rag/rerank.py` | bge cross-encoder top-50 | 提高候选池召回上限 |
| KB bridge | `intelligence/services/kb_rag.py` | subprocess、timeout、freshness | W 失败时仍算成功 |
| Closed loop | `intelligence/services/closed_loop_retrieval.py` | narrow/broad/counter | 已训练 multi-hop retriever |
| Evidence audit | `intelligence/services/research_brief.py` | L1/L2/L3/L4/E | 自动判投资结论正确 |
| L3 lookup | `intelligence/services/l3_evidence.py` | opt-in、公告/互动、降级 | 每次问答都查官方 |
| Research Judge | `intelligence/services/research_judge.py` | 研究成熟度 | 自动预测裁判 |
| Research Queue | `intelligence/services/research_queue.py` | 缺口转任务 | 自动完成所有研究 |
| Output Review | `intelligence/services/output_review.py` | advisory WARN + revision | 已硬阻断所有幻觉 |
| DuckDB | `market_feature_store/`、`db/` | 结构数据和时序分析 | 所有 ask 都查 DB |
| Run/Trace | `intelligence/services/run_store.py`、`intelligence/api/app.py` | run snapshot、append-only trace/stream、recovery、SSE | 分布式 tracing 平台 |
| Claim lineage | `intelligence/services/claim_lineage.py` | evidence id、claim manifest | 所有历史答案均人工核验 |
| PIT KB | `scripts/pit_lib.py` | available_time <= T | 在线全链已 bitemporal |
| Fidelity | `intelligence/services/fidelity_contract.py` | cutoff、hash、commit | 已证明全部历史正确 |
| Memory vault | `agent-memory/README.md` | 分层 Git/Markdown 黑板 | 强一致数据库 |
| User memory | `.foresight/<user>/*.jsonl` | correction/checkpoint/verdict | memory 是当前事实 |

---

## 32. 面试中必须主动声明的实现边界

### 32.1 已实现但仍需要更多验证

- Question Router 和 QuestionPlan；
- S/G/R/W/M/V/D/L 多源分工；
- Hybrid RAG 工程链路；
- closed-loop retrieval；
- DuckDB 数据块；
- evidence audit；
- output review；
- run/trace；
- Agent Memory；
- PIT 与 claim fidelity 框架；
- checkpoint/verdict/experience card。

这些可以说“已实现代码和基本工作流”，但评测充分性要分开说。

### 32.2 POC 或原型属性

- Knowledge Base README 明确称 RAG 为 POC；
- `ask` 是可运行原型和研究工作台；
- Workbench 默认本地；
- L3 是 opt-in；
- Review 是 advisory；
- 自动执行阈值尚未充分校准。

### 32.3 尚未完整落地

- 全链 Temporal Facts；
- 每个事实的 active/superseded/invalidated；
- 所有历史日期的严格 PIT snapshot；
- 充分人工标注的 RAG query set；
- 大规模无偏历史盲测；
- 完整生产 auth、多租户、SLO；
- 强一致 Memory 和自动冲突仲裁；
- 生产交易执行。

### 32.4 明确没有核实的能力

- 基础模型预训练平台；
- RLHF；
- DPO；
- GRPO；
- LoRA/QLoRA 微调；
- FSDP/ZeRO 分布式训练；
- vLLM/SGLang/TensorRT-LLM/LMDeploy 生产服务；
- 自动化交易下单；
- 已证明持续 alpha。

这些属于你应掌握的面试知识，不属于当前金融 Agent 的真实落地。

---

## 33. V3 项目讲解的四种长度

### 33.1 15 秒

> 我做了一个可审计的 A 股研究 Agent：规则和 Planner 负责路由，DuckDB、图谱、Hybrid RAG、用户记忆和官方证据负责多源检索，LLM 负责组织表达，最后再做 evidence layer、反证、PIT、output review 和历史 checkpoint。

### 33.2 30 秒

> 我的金融 Agent 不是一次 LLM 调用。问题先经过 clarification、Router 和 `QuestionPlan`，再按需访问 S/G/R/W/M/V/D/L：盘面、图谱、证据索引、wiki RAG、用户记忆、历史回检、DuckDB 和官方 L3。RAG 采用 BGE dense、独立 BM25、RRF、实体 boost、wikilink 和可选 rerank；最终结论还要经过证据分层、反证、PIT、新鲜度和 Output Review。当前是个人研究工作台，框架已实现，但 RAG 和预测效果仍需更充分人工评测和历史盲测。

### 33.3 2 分钟

> 我做的是一个面向 A 股题材研究的本地 Agent 工作台。最初的问题是，大模型可以生成很流畅的结论，但会把行情、研报、用户观点和公司事实混在一起，也无法解释检索失败和历史前视。
>
> 所以我先做控制层：Question Router 把请求分成已知 workflow、Planner、data gap 和 clarification，命令默认 preview，只有低风险、可自动执行、置信度大于 0.7 且无缺参才执行。进入问答后，Answer Orchestrator 生成 `QuestionPlan`，规定问题类型、必看视角、检索源、质量门和输出契约。
>
> 数据层分成 S/G/R/W/M/V/D/L。结构化行情和财务走 DuckDB；知识材料走 Hybrid RAG，真实链路是 BGE-m3 dense 加独立 BM25，经 RRF、实体 boost、wikilink 一跳扩展和可选 cross-encoder rerank；用户记忆只做 prior，官方 L3 用于验证公司兑现。W 还做 narrow、broad、counter 三孔径，主动找上下游和反证。
>
> 最后 evidence audit 区分 L1/L2/L3/L4/E，没有 L3 就不能把研报推演写成公司事实；Output Review 检查 freshness、evidence layer、反证、缺口和弱证据硬写；历史研究按 available time 做 PIT，结论转成 T+1/T+3/T+5 checkpoint。当前系统已具备可运行链路和评测框架，但 RAG README 仍是 POC，在线 ask 的 Temporal Facts 也没有完全贯穿，我不会夸大成已证明预测 alpha 的生产系统。

### 33.4 5 分钟白板

按以下顺序画：

```text
User
  ↓
Clarify
  ↓
Question Router
  ├─ known workflow
  ├─ planner
  ├─ data gap
  └─ clarification
  ↓
QuestionPlan
  ↓
Entity Anchor
  ↓
┌───────────────────────────────────────┐
│ S  G  R  W  M  V  D  L               │
│       W: narrow/broad/counter          │
│       D: parallel blocks → D3 barrier  │
└───────────────────────────────────────┘
  ↓
Evidence Audit + Telemetry
  ↓
Counter Plan + AnswerSpec
  ↓
Template / Optional LLM
  ↓
Output Review → Revision → Validation
  ↓
Answer + Citation + Trace
  ↓
Checkpoint → Verdict → Experience
```

画完主动补三条：

1. Memory 不是事实源；
2. W 命中不是事实确认；
3. PIT 和 Temporal Facts 尚未完全贯穿在线 ask。

---

## 34. V3 学习与模拟面试清单

### 34.1 必须能不看稿讲出的 12 项

1. Question Router；
2. QuestionPlan；
3. S/G/R/W/M/V/D/L；
4. raw→wiki→relations→RAG；
5. BM25 + dense + RRF；
6. narrow/broad/counter；
7. DuckDB D blocks；
8. evidence layer；
9. Output Review；
10. Agent Memory；
11. PIT；
12. checkpoint/verdict 闭环。

### 34.2 每项都问自己

- 当时遇到什么业务问题？
- 为什么 LLM 单次调用不够？
- 为什么选这个技术？
- 替代方案是什么？
- 代码入口在哪里？
- 输入输出是什么？
- 失败怎样降级？
- 用什么指标评测？
- 现在最大的边界是什么？

### 34.3 最容易被抓住的夸大

- 把 BGE sparse 说成已用于 hybrid；
- 把 W 相关命中说成事实；
- 把 L3 说成默认开启；
- 把所有 ask 说成都查 DuckDB；
- 把 Output Review 说成自动预测裁判；
- 把 PIT 工具说成在线全链完整 Temporal Facts；
- 把 RAG POC 说成生产质量；
- 把 memory 说成自动贝叶斯学习；
- 把通用 P1 训练/Serving 知识说成项目实装。

### 34.4 最能体现工程深度的主动表达

> 我会区分框架是否实现、是否跑通、是否有评测、是否有充分统计证据。这四件事不是一回事。

---

## 35. V3 总结

你的金融 Agent 最值得在面试中讲的，不是“用了很多技术”，而是以下因果链：

```text
金融事实会变化、来源会冲突
→ 不能让 LLM 直接做事实源

问题类型不同、动作有风险
→ 先 Router 和 QuestionPlan

数字与文本形态不同
→ DuckDB 与 RAG 分工

关键词与语义各有盲区
→ BM25 + dense + RRF + rerank

单次召回会确认偏误
→ narrow + broad + counter

来源相关不代表事实硬
→ S/G/R/W/M/V/D/L + evidence layer

模型会把弱证据写强
→ AnswerSpec + Output Review

历史容易用未来信息
→ publish/available time + PIT + fidelity

Agent 会跨会话遗忘
→ 分层 Memory + provenance + writeback

系统需要真正改进
→ checkpoint + verdict + correction + experience
```

最标准的项目定位：

> 这是一个把 LLM 放在受约束研究流程中的个人金融 Agent。它已经实现多源检索、结构化规划、证据分层、反证、输出质检、运行追踪和回检框架；但它不是基础模型训练平台，不是生产交易系统，也还没有充分证据证明稳定预测收益。项目当前最强的价值是把金融研究从不可审计的聊天，推进到有来源、有时间边界、有失败降级、可回放的工程流程。

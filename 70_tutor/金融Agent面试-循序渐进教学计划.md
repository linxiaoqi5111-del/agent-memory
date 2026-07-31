---
title: 金融 Agent 面试循序渐进教学计划
type: tutor-note
agent: devin
source: "Devin Session deebe5e092fe49579a9983ee14ca02d3"
date: 2026-07-14
tags: [llm, interview, finance-agent, curriculum, study-plan]
status: verified
related: ["[[大模型面试-金融Agent项目第一性原理复习手册-V3]]", "[[金融Agent面试学习]]"]
reviewed_by: human
reviewed_at: 2026-07-14
---

# 金融 Agent 面试：循序渐进教学计划

> 配套教材：
> [[大模型面试-金融Agent项目第一性原理复习手册-V3]]
>
> 默认方案：8 周，每周 5 天，每天 60–90 分钟。
> 目标不是“读完 9000 行”，而是达到：能解释、能画图、能指代码、能比较方案、能扛追问。

---

## 1. 什么叫“真正掌握”

每个技术点都要通过五级门槛。

### L1：直觉

不用术语，能向非技术同学解释：

- 业务问题是什么；
- 为什么一次 LLM 调用不够；
- 这个模块解决什么。

### L2：原理

能从第一性原理回答：

- 输入是什么；
- 输出是什么；
- 系统边界是什么；
- 哪部分是确定性的；
- 哪部分是概率性的。

### L3：实现

能指出：

- 真实文件；
- 核心函数或 dataclass；
- 控制流；
- 数据流；
- 异常和降级。

### L4：选型

能比较：

- 当前方案为什么合适；
- 替代方案是什么；
- 当前方案牺牲了什么；
- 在什么规模或约束变化后应该换方案。

### L5：面试

能完成：

- 15 秒一句话；
- 30 秒标准答案；
- 2 分钟展开；
- 5 分钟白板；
- 连续三轮追问；
- 主动声明真实边界。

只有达到 L5，才算一个主题真正掌握。

---

## 2. 学习顺序：不要按手册页码从头背到尾

正确顺序：

```text
先建立项目全局地图
→ 再理解控制链
→ 再理解证据链
→ 再理解生成和质检
→ 再理解记忆、回放和评测
→ 最后补 Transformer/训练/推理理论
→ 把理论映射回项目
→ 模拟面试
```

原因：

1. 先知道系统为什么存在，技术细节才有挂载点；
2. 先理解自己的项目，再学通用理论，更容易形成长期记忆；
3. 面试最终考的是“原理 + 实现 + 取舍”，不是孤立名词；
4. Transformer、训练和推理很重要，但不是这个项目故事的起点。

---

## 3. 四阶段课程

### 阶段一：建立系统心智模型

目标：

- 能画出三仓和四条链；
- 能讲清 LLM 在系统中的职责；
- 能解释为什么不能只用一个 prompt。

覆盖：

- 三仓职责；
- 控制链、证据链、生成链、学习链；
- Question Router；
- QuestionPlan；
- 风险门控。

### 阶段二：掌握核心工程实现

目标：

- 能追踪一个问题如何穿过真实代码；
- 能解释 RAG、DuckDB、多源证据和 Output Review；
- 能讲清失败和降级。

覆盖：

- S/G/R/W/M/V/D/L；
- raw → wiki → relations → `.rag_index`；
- chunking；
- BGE-m3 dense；
- 独立 BM25；
- RRF；
- exact boost；
- wikilink；
- rerank；
- narrow/broad/counter；
- D0-D9；
- L3；
- evidence audit；
- AnswerSpec；
- Output Review。

### 阶段三：掌握可靠性与学习闭环

目标：

- 能解释系统如何防幻觉、防前视和防记忆污染；
- 能解释如何知道系统是否进步。

覆盖：

- Agent Memory；
- provenance；
- trust boundary；
- PIT；
- bitemporal；
- claim fidelity；
- Run/Trace/SSE；
- Recall@k、hit@k、MRR；
- checkpoint/verdict；
- correction/experience card。

### 阶段四：面试迁移

目标：

- 把项目实现映射到大模型通用知识；
- 能做系统设计、项目深挖和 P1 理论题；
- 能诚实说明未实现能力。

覆盖：

- Transformer；
- 训练与对齐；
- LoRA/QLoRA；
- 显存和分布式；
- KV Cache；
- 量化；
- Serving；
- 项目 STAR；
- 白板；
- 连续追问。

---

## 4. 默认 8 周课程表

## 第 0 周：诊断与全局地图

### 目标

- 知道自己目前会什么、不会什么；
- 能画出三仓；
- 建立统一术语。

### 课程

1. 项目一句话定位；
2. 三仓职责；
3. 四条链；
4. 一道问题的端到端旅程；
5. 第一次 2 分钟项目讲解。

### 产出

- 一张手绘总架构；
- 15 秒、30 秒、2 分钟三版介绍；
- 第一份知识缺口清单。

### 通过标准

不看稿回答：

1. 为什么 LLM 不是事实源？
2. 三个仓分别负责什么？
3. S/G/R/W/M/V/D/L 是什么？
4. 为什么 Router 在 RAG 前？
5. 为什么最终还要 Output Review？

---

## 第 1 周：Question Router、Planner 与风险门控

### 目标

能讲清：

```text
自然语言
→ 澄清
→ 路由
→ QuestionPlan
→ 工具计划
→ 是否允许执行
```

### 课程

1. `clarify_for_query`；
2. `route_question` 四类路由；
3. 规则优先与 Planner 长尾；
4. `QuestionPlan`；
5. `required_lenses`；
6. `retrieval_plan`；
7. `quality_gates`；
8. `output_contract`；
9. `MIN_AUTO_EXECUTION_CONFIDENCE = 0.7`；
10. preview、dry-run 和 low-risk gate。

### 核心问题

- 为什么不直接让 LLM 选择所有工具？
- 规则 Router 和模型 Router 各自擅长什么？
- 为什么 confidence 不是权限？
- 为什么快答也不能跳过必要检索？

### 代码地图

- `intelligence/services/question_router.py`
- `intelligence/services/answer_orchestrator.py`
- `intelligence/workflows/agent_orchestrator.py`

### 通过标准

给出三个用户问题，能：

- 判断 route；
- 写出 QuestionPlan；
- 指出缺参；
- 判断是否允许自动执行；
- 解释失败时如何降级。

---

## 第 2 周：多源证据与 Knowledge Base RAG

### 目标

能解释：

- 为什么不同来源不能混成一个 context；
- 为什么 hybrid retrieval 优于单路；
- 为什么检索命中不等于事实。

### 课程

1. S/G/R/W/M/V/D/L；
2. evidence layer L1/L2/L3/L4/E；
3. raw、source、concept、entity、relations；
4. YAML frontmatter；
5. section-aware chunking；
6. BGE-m3 dense；
7. 独立 `rank_bm25`；
8. RRF；
9. exact-match boost；
10. wikilink 一跳扩展；
11. cross-encoder rerank；
12. index revision 和 freshness；
13. timeout、non-zero、坏 JSON、stale 降级。

### 必须掌握的纠错

不能说：

> 当前 RAG 用的是 BGE-m3 dense+sparse 双路。

必须说：

> BGE-m3 当前负责 dense；lexical 路径由独立 `rank_bm25` 实现。代码虽有 sparse 接口，但没有接入主检索链。

### 代码地图

- `skills/lib/rag/chunking.py`
- `skills/lib/rag/retrieval.py`
- `skills/lib/rag/embedder.py`
- `skills/lib/rag/rerank.py`
- `skills/lib/rag/store.py`
- `scripts/rag_index.py`
- `intelligence/services/kb_rag.py`

### 通过标准

白板写出：

```text
dense top-N ∪ BM25 top-N
→ exact boost
→ RRF
→ wikilink neighbor
→ page aggregation
→ optional rerank
→ freshness gate
```

并解释每一步解决什么错误。

---

## 第 3 周：Closed-loop Retrieval 与 DuckDB

### 目标

能讲清语义检索和结构化查询如何协作。

### 课程

1. narrow；
2. broad；
3. counter；
4. `RetrievalAttempt`；
5. conclusion/clue/counter/discarded；
6. 为什么没有反证命中不等于没有风险；
7. 为什么数值事实不能只放向量库；
8. DuckDB 的选型；
9. 典型事实表；
10. D0-D9；
11. planner-worker 并行；
12. D3 为什么必须后置串行；
13. not attempted/empty/error/ok。

### 代码地图

- `intelligence/services/closed_loop_retrieval.py`
- `intelligence/services/ask.py`
- `intelligence/services/ask_planner.py`
- `market_feature_store/schema.sql`
- `intelligence/services/market_timeseries.py`
- `intelligence/services/market_financials.py`

### 通过标准

回答：

- 为什么一次 top-k 会产生确认偏误？
- broad 和 counter 各增加什么信息？
- 为什么 D3 不能与所有数据块同时并行？
- 什么情况下用 PostgreSQL 替代 DuckDB？
- SQL 结果和 Wiki chunk 如何避免混写？

---

## 第 4 周：Evidence Audit、L3、Output Review 与 PIT

### 目标

能讲清系统如何限制结论强度。

### 课程

1. 来源可信度先验；
2. claim lineage；
3. L1/L2/L3/L4/E；
4. L3 官方证据；
5. Research Judge；
6. Research Queue；
7. Forecast Preflight；
8. AnswerSpec；
9. Output Review 六项顺序；
10. advisory vs blocking；
11. WARN 定向修订；
12. publish time；
13. available time；
14. valid time；
15. PIT truncate；
16. cutoff violation；
17. bitemporal replay。

### 核心问题

- 为什么“公司与概念相关”不等于“公司业绩兑现”？
- 为什么 L3 默认关闭？
- 为什么 Output Review 不是预测裁判？
- 为什么无日期材料在历史回放中默认排除？
- 为什么 publish time 不等于 available time？

### 通过标准

看到以下证据：

```text
题材逻辑 + 卖方推演 + 强势盘面 + 无公司公告
```

能给出准确结论：

```text
预期交易且有盘面验证，但公司端兑现尚未确认。
```

---

## 第 5 周：Agent Memory、可观测性与评测闭环

### 目标

能解释 Agent 如何跨会话学习，但不污染当前事实。

### 课程

1. 为什么不能把全部聊天塞进 prompt；
2. Git + Markdown + YAML + Obsidian；
3. inbox/knowledge/projects/conventions/playbooks；
4. 分层写回；
5. trust boundary；
6. memory as prior；
7. userspace JSONL；
8. judgments/corrections/checkpoints/verdicts；
9. experience cards；
10. run.json、trace.jsonl、stream.jsonl；
11. SSE 和 polling reconcile；
12. Recall@k、hit@k、MRR；
13. claim fidelity；
14. historical blind test；
15. `unverifiable`。

### 核心问题

- Memory 和 RAG 有什么区别？
- 为什么记忆中的命令不能直接执行？
- 为什么用户过去的观点只能作为 prior？
- 为什么 `unverifiable` 不能算 hit 或 miss？
- 高 Recall@k 为什么不等于答案可靠？

### 通过标准

能画出：

```text
query
→ answer
→ correction
→ checkpoint
→ outcome
→ verdict
→ experience card
→ 下一次检索和策略
```

并说明“有闭环框架”不等于“已经证明预测有效”。

---

## 第 6 周：Transformer、训练、对齐与 PEFT

### 目标

把 P1 理论讲清，并准确映射到项目。

### 课程

1. tokenization；
2. embedding；
3. self-attention；
4. Q/K/V；
5. multi-head；
6. positional encoding/RoPE；
7. residual、LayerNorm、RMSNorm；
8. FFN/SwiGLU；
9. pretraining；
10. SFT；
11. RLHF；
12. DPO/GRPO；
13. LoRA/QLoRA；
14. 数据质量；
15. catastrophic forgetting。

### 项目映射

必须明确：

- 你的项目使用推理模型和工具编排；
- 没有核实的 RLHF/DPO/GRPO 训练；
- 没有核实的 LoRA/QLoRA 微调；
- 不要把会讲理论说成项目已经实装。

### 通过标准

每个理论题都能回答：

1. 数学或机制；
2. 为什么有效；
3. 代价；
4. 常见失败；
5. 与项目的真实关系。

---

## 第 7 周：显存、分布式、推理、量化与 Serving

### 目标

掌握模型工程 P1，并能做系统取舍。

### 课程

1. 参数、梯度、优化器状态和激活显存；
2. mixed precision；
3. gradient accumulation；
4. checkpointing；
5. ZeRO/FSDP；
6. tensor/pipeline parallel；
7. prefilling/decoding；
8. KV Cache；
9. continuous batching；
10. PagedAttention；
11. speculative decoding；
12. INT8/INT4/FP8；
13. AWQ/GPTQ；
14. vLLM/SGLang；
15. throughput、latency、TTFT、TPOT。

### 项目映射

必须明确：

- 当前项目没有核实的 FSDP/ZeRO 训练；
- 没有核实的 vLLM/SGLang/TensorRT-LLM 生产部署；
- 这些是应聘大模型岗位的理论能力，而不是当前项目成果。

### 通过标准

能完成两道白板：

1. 估算一个模型训练或推理显存；
2. 设计高并发 LLM Serving，并说明吞吐与延迟取舍。

---

## 第 8 周：项目深挖与模拟面试

### 目标

从“我懂”变成“面试官能确认我懂”。

### 训练

1. 15 秒项目定位；
2. 30 秒系统介绍；
3. 2 分钟完整故事；
4. 5 分钟白板；
5. STAR；
6. RAG 深挖；
7. Agent 深挖；
8. Memory 深挖；
9. PIT 深挖；
10. 评测深挖；
11. 系统设计改进；
12. 压力追问。

### 模拟面试轮次

#### 第一轮：基础

- 什么是 RAG？
- 什么是 Agent？
- 什么是 Memory？
- 为什么用 DuckDB？

#### 第二轮：项目实现

- 代码入口在哪里？
- 一次请求的数据流是什么？
- 检索失败怎么办？
- LLM 失败怎么办？

#### 第三轮：批判性追问

- 为什么不用 LangGraph？
- 为什么不用向量数据库？
- RRF 为什么是 60？
- 0.7 置信度如何校准？
- 怎样证明 counter retrieval 有用？

#### 第四轮：真实性

- 哪些只是 POC？
- 哪些指标尚未充分验证？
- Temporal Facts 哪部分没贯穿？
- 如何证明不是用了未来信息？

### 最终通过标准

- 90 分钟模拟面试；
- 关键问题正确率 ≥ 85%；
- 项目题不出现事实性夸大；
- 连续三轮追问不丢失主线；
- 能主动指出两项当前设计缺陷和改进路线。

---

## 5. 每一课固定教学流程

每课 60–90 分钟。

### 第一步：闭卷诊断，5–10 分钟

我先问 3–5 个问题。

你必须先回答；即使不会，也说出当前理解。

目的：

- 激活已有知识；
- 发现误解；
- 避免“看答案时觉得自己会”。

### 第二步：第一性原理讲解，15–20 分钟

我按下面顺序讲：

```text
业务问题
→ 问题本质
→ 系统边界
→ 选型
→ 代价
```

不先堆术语。

### 第三步：真实代码走读，15–25 分钟

每次只看最小必要代码：

- 一个入口；
- 一个核心数据结构；
- 一条主控制流；
- 一个失败分支。

不一次读完整文件。

### 第四步：费曼复述，5–10 分钟

你用自己的话回答：

> 假设我是一个不懂这个模块的同事，你怎么解释？

我会指出：

- 逻辑跳步；
- 术语堆砌；
- 因果倒置；
- 不准确表述；
- 项目夸大。

### 第五步：面试表达，10–15 分钟

你依次回答：

- 15 秒；
- 30 秒；
- 2 分钟。

我按标准打分并给更精确版本。

### 第六步：追问和迁移，10–15 分钟

我会问：

- 为什么不用另一种方案？
- 规模扩大后怎么办？
- 这个指标怎么测？
- 失败时怎么办？
- 当前实现边界是什么？

### 第七步：课后卡片，5 分钟

每课生成四张卡：

1. 原理卡；
2. 代码卡；
3. 错误卡；
4. 面试表达卡。

---

## 6. 每日训练模板

### 60 分钟版

```text
10 分钟：闭卷复习旧卡片
20 分钟：新概念
15 分钟：真实代码
10 分钟：口头回答
 5 分钟：错误卡
```

### 90 分钟版

```text
15 分钟：间隔复习
25 分钟：第一性原理
20 分钟：代码走读
15 分钟：白板/数据流
10 分钟：面试问答
 5 分钟：错误卡
```

### 30 分钟版

```text
 5 分钟：旧题
10 分钟：一个概念
 5 分钟：一个代码对象
 5 分钟：30 秒回答
 5 分钟：纠错
```

---

## 7. 间隔复习机制

每个主题在以下时间复习：

```text
当天
第 1 天
第 3 天
第 7 天
第 14 天
第 30 天
```

复习不是重读，而是闭卷输出：

- 画图；
- 解释；
- 写伪代码；
- 比较选型；
- 回答追问。

只有答错后才回看手册。

---

## 8. 掌握度评分

每个主题 100 分：

| 维度 | 分值 |
|---|---:|
| 业务问题与第一性原理 | 20 |
| 架构和数据流 | 20 |
| 真实代码与输入输出 | 20 |
| 选型、替代方案和 trade-off | 15 |
| 异常、降级和评测 | 15 |
| 面试表达与真实性边界 | 10 |

等级：

```text
< 60：只见过
60–69：能复述
70–79：基本理解
80–89：可以面试
90–100：可以扛深挖
```

课程中的主题必须达到 80 分才进入“已掌握”。

低于 80 分：

- 记录错因；
- 24 小时后重答；
- 不靠重读直接判定掌握。

---

## 9. 我作为老师的教学规则

1. 一次只推进一个核心概念；
2. 你先答，我再讲；
3. 不用“听懂了”作为完成标准；
4. 每课必须输出，而不是只阅读；
5. 我会严格纠正不精确和夸大的表述；
6. 每个项目结论都要对应真实文件或代码；
7. 原理题必须回答“为什么”和“代价”；
8. 面试题必须经过追问；
9. 错题会在后续课程中随机重现；
10. 你没有通过掌握门槛时，我不会假装已经掌握。

---

## 10. 你在课程中要维护的五类笔记

### 1. 系统地图

只保留架构图和关键数据流。

### 2. 原理卡

格式：

```text
问题：
本质：
方案：
为什么：
代价：
```

### 3. 代码卡

格式：

```text
文件：
入口：
输入：
输出：
主流程：
失败分支：
```

### 4. 错误卡

格式：

```text
我的错误答案：
错误原因：
正确答案：
下次识别信号：
```

### 5. 面试卡

格式：

```text
15 秒：
30 秒：
2 分钟：
追问：
边界：
```

---

## 11. V3 手册的使用方法

V3 是参考书，不是每天从头阅读的教材。

### 上课前

只看老师指定的 10–30 行或一个小节。

### 上课中

闭卷回答和画图。

### 上课后

只用 V3：

- 核对真实代码；
- 修正错误；
- 补充边界；
- 生成卡片。

### 周末

再通读本周对应完整章节。

这样可避免：

> 看了大量内容，却无法脱离文本回答。

---

## 12. 第一课安排：为什么你的项目不是“LLM + Prompt”

### 第一课目标

学完后能回答：

1. 你的金融 Agent 解决什么问题？
2. 为什么不能把所有内容拼进 prompt？
3. 确定性系统和概率模型如何分工？
4. 三仓分别做什么？
5. 四条链是什么？

### 第一课阅读

V3：

- 第 0 章；
- 第 13 章；
- 第 14 章；
- 第 33 章的 15 秒、30 秒和 2 分钟版本。

### 第一课闭卷诊断题

#### 题 1

一句话介绍你的项目，不超过 50 字。

#### 题 2

为什么 LLM 不能作为金融事实源？

#### 题 3

`agent-memory`、`knowledge-base-private`、`finance-workspace-private`
分别负责什么？

#### 题 4

控制链、证据链、生成链、学习链分别解决什么问题？

#### 题 5

如果去掉 Question Router，直接让 LLM 自由选择工具，会出现哪三类风险？

### 第一课白板

闭卷画：

```text
User
→ Clarify
→ Router
→ QuestionPlan
→ Evidence Sources
→ Audit
→ AnswerSpec
→ LLM
→ Review
→ Trace/Checkpoint
```

### 第一课课后作业

1. 录一段 2 分钟项目介绍；
2. 不看稿画出三仓和四条链；
3. 回答“LLM 在项目中负责什么、不负责什么”；
4. 写出两个当前项目边界。

---

## 13. 推荐执行方式

默认推荐：

```text
8 周标准班
每周 5 课
每课 60–90 分钟
```

如果面试很近：

```text
4 周冲刺班
每天 2–3 小时
前两周项目
第三周 P1
第四周模拟面试
```

如果工作很忙：

```text
12 周轻量班
每天 30–45 分钟
每周一次 60 分钟复盘
```

无论选择哪种，教学顺序和掌握门槛不变，只改变每天的内容量。

---

## 14. 最终毕业标准

你需要能独立完成：

1. 一张完整系统架构图；
2. 一个真实问题的端到端代码追踪；
3. RAG、Agent、Memory、PIT、评测五个专题深挖；
4. 两道 Transformer 白板；
5. 两道训练/显存/推理计算题；
6. 一次 90 分钟模拟面试；
7. 一份项目不足和三个月演进计划；
8. 全程不把 POC、roadmap 或理论知识夸成已上线实现。

达到这些标准，才算真正掌握这份手册。

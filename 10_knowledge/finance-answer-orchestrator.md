---
title: 金融问答编排层
type: knowledge
agent: codex
source: finance-workspace-private implementation
date: 2026-06-30
tags: [finance-agent, qa, orchestration, rag, reasoning]
status: verified
related: ["[[finance-answer-self-review-framework]]"]
---

# 金融问答编排层

## 核心原则

金融 Agent 不能在用户提问后直接生成答案，应先把自然语言问题解析成结构化任务，再决定证据来源、分析视角、输出深度和质检门槛。

这层编排不是输出模板，而是回答前的“研究主管”：

1. 识别问题类型：个股深挖、题材分析、行情前瞻、新闻/公告冲击、回答质检、方法论讨论、通用问答。
2. 判断回答深度：quick / standard / deep。
3. 绑定必需视角：市场结构、板块生命周期、公司本体、证据硬度、逻辑生命周期、二阶导、反证、条件化结论。
4. 规划证据来源：DuckDB、wiki entity/concept、hybrid RAG、evidence_index、experience_cards、disclosure/interaction API。
5. 将计划注入 compose prompt，再由 LLM 基于证据链生成并经过影子用户反驳/重写。

## 技术取舍

当前优先采用“规则编排 + LLM 生成”的混合路线：

- 纯规则：稳定、便宜、可测，但灵活性弱。
- 纯 LLM planner：理解力强，但成本高、稳定性差，仍可能拍脑袋。
- 混合编排：规则负责关键路径，LLM 负责自然表达和复杂推理，是当前阶段最合适的 P0/P1 方案。

## 可迁移知识

这套模式适用于所有垂直行业 Agent：先把用户请求变成结构化 `QuestionPlan`，再做检索、生成、质检和沉淀。它比单纯写 prompt 或堆 skill 更稳定，因为 skill 解决高频入口，编排层解决默认思维方式。

## 后续演进

- P0：计划只注入 prompt，不反向控制检索。
- P1：计划控制 RAG k 值、DuckDB 查询块、是否调用公告/互动易 API。
- P2：计划绑定评分器，低分自动二次重写。
- P3：行情前瞻类计划接入“假设 -> 盘后验证 -> 经验卡沉淀”闭环。

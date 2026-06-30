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

## 行情前瞻四源合议

`market_forecast` 类问题不能只靠盘面外推。次日研判要先合并四类当时可得信息：

1. 全量盘面复盘：市场阶段、量价、涨家数 MA5、涨跌停、申万一级容量、双红、新高和涨停热度。
2. 晚间卖方/机构胜率：判断信息权重、覆盖密度、证据硬度和共识兑现风险。
3. 复盘会外盘市场：优先读取 fupanhui `/reviews/global-market` 结构化接口，观察纳指、标普、恒科、AI 硬件链、海外核心股和中概/港股映射对 A 股题材的顺逆风；web search 只作为接口缺失时的兜底。
4. 晨汇/早间材料：抽取新增事件、产业变量和盘中待验证方向。

策略一二三四在行情前瞻里要还原成市场状态语言：分歧时比较策略三的主流题材强势股回流和策略二的流动性切换；上涨时区分结构性上涨与普涨，再映射策略一的主线流动性池和策略四的强趋势/强者恒强；高位拥挤时用核心新高、涨停扩散和成交承接判断是主线再确认还是共识兑现。

## 后续演进

- P0：计划只注入 prompt，不反向控制检索。
- P1：计划控制 RAG k 值、DuckDB 查询块、是否调用公告/互动易 API。
- P2：计划绑定评分器，低分自动二次重写。
- P3：行情前瞻类计划接入“假设 -> 盘后验证 -> 经验卡沉淀”闭环。

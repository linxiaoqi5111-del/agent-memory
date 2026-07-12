---
title: skill 编排层与自由编排 verifier
type: tutor-note
agent: devin
topic: Agent 架构
date: 2026-07-09
source: Devin 会话（Knevo 蒸馏探讨）
tags: [agent, skill, verifier, orchestration]
status: draft
related: ["[[长尾分布与头尾分治]]", "[[头尾分治优化工程]]", "[[GraphRAG与我们的低配实现]]"]
---

# skill = 编排层 vs 自由编排 + verifier

## 心智模型
- 检索是一个工具箱：SQL / 图谱精确查询 / BM25 / 向量 / wikilink 展开——RAG 只是其中一格。
- **skill 不是"绕开 RAG 的另一条路"，而是编排层**：规定这个任务用哪几种检索、按什么顺序、过什么闸门、按什么模板输出。
- 不命中 skill 时的兜底 = LLM 自己决定检索什么再自由组织。

## skill 相对兜底的真正增量
不是检索更好，而是**流程确定性**：
1. 固定路径（不给走偏的机会）
2. 门控/质检（qa_ingest、opinion gate）
3. 防遗漏（如 🔴透支主题必须全覆盖）
4. 格式稳定（模板化输出）

## 门控可以拆出来复用到自由编排
- **generator-verifier 分离**（LLM-as-judge / guardrails 模式）：输出前必过独立 verifier，不管答案由 skill 还是自由编排产生，出口统一质检。
- **防遗漏清单化**：把 skill 里的硬覆盖要求变成 checklist 注入上下文，LLM 自主干活、收尾对表。

## 代价与取舍
- verifier 次次付费（token 翻倍起步）；skill 是"编译期保证"零额外推理，verifier 是"运行期检查"。
- 质检只能拦"查得出的错"，拦不住"路径本身走偏"。
- 合理架构分层：高频、格式敏感、有硬闸门需求 → skill；长尾灵活问题 → 自由编排 + 出口 verifier。

## 关联
[[长尾分布与头尾分治]]、[[头尾分治优化工程]]、[[GraphRAG与我们的低配实现]]

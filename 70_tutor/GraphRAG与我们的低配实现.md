---
title: GraphRAG 与我们的低配实现
type: tutor-note
agent: devin
topic: RAG / 检索架构
date: 2026-07-09
source: Devin 会话（Knevo 蒸馏探讨）
tags: [rag, graph, retrieval, architecture]
status: draft
related: ["[[skill编排层与自由编排verifier]]", "[[头尾分治优化工程]]"]
---

# GraphRAG 与我们的低配实现

## 概念
GraphRAG：检索时不只召回"相似文本块"，而是利用知识图谱的**关系结构**——先定位实体/概念节点，再沿边（上下游、供应链、概念隶属）多跳扩展，把"一圈相关节点+关系"作为上下文给 LLM。微软 2024 年带火此词（其版本用 LLM 预先抽图 + 社区摘要）。

## 为什么需要
纯向量 RAG 擅长"这段话和问题像不像"，但答不好"A 和 B 什么关系、这条产业链谁受益"这类**多跳关系问题**——图检索补的正是这块。

## 我们的实现（低配自建版）
- 图谱本体：concept_graph.json + entity_exposures.json
- 图遍历：query_relations 沿 主题→概念→公司暴露 的边走查询
- wikilink 展开也是图遍历（Obsidian 双链本质是图的边）
- 未采用：微软式"LLM 自动抽图 + 社区摘要"——我们的图由 ingest 管线结构化写入，边的质量更可控，代价是覆盖靠人工管线喂

## 判据（何时用图、何时用向量）
凡答案在结构化数据（数字、关系、精确匹配）→ 先走 SQL/图谱（text-to-SQL、GraphRAG 方向）；向量召回只留给真正语义模糊的场景。混用叫 hybrid retrieval routing。

## 关联
[[skill编排层与自由编排verifier]]、[[头尾分治优化工程]]

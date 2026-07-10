---
title: 结论 TTL 与 delta-only 跟踪契约
type: tutor-note
agent: devin
source: Devin 会话（Knevo 蒸馏探讨）
date: 2026-07-09
tags: [tracking, ttl, delta, reporting]
status: draft
related: ["[[记忆prior化与贝叶斯仲裁]]"]
---

# 结论 TTL 与 delta-only 跟踪契约

## 概念
两个让"持续跟踪型输出"不腐烂、不注水的契约：
- **结论 TTL**：每个判断自带有效期（跟踪类 30 天复查、深度报告 90 天）——过期结论必须复核才能再引用。
- **delta-only**：以上期基线为锚，只报"变了什么"；无变化的指标直接跳过，不复述。每期强制做**观点四态对照**：上期判断今天是被"支持/削弱/无变化/信息不足"。收尾产出"下期关注+触发条件"，成为下一轮的输入，报告之间成链。

## 为什么
LLM 天然爱把每次回答写成自足的完整文章（凑字数、重复背景），跟踪场景里这是噪音。显式契约把"新信息密度"变成可检查的输出要求。TTL 则解决"陈旧结论被当新鲜事实引用"——和缓存过期是同一个问题。

## 实现对照
- Knevo：finance-industry-track 的输出骨架第 4 段就是观点四态（q8）。
- 我们：daily-ops/concept-delta 已是 delta 型，但缺①判断级 TTL 字段（证据有 45 天复核，结论没有）②四态显式判定字段③"下期关注清单"次日强制读取。

## 跨域同构
缓存 TTL / 增量 ETL（CDC）vs 全量刷新 / 周报文化里的"only exceptions"原则。

相关：[[记忆prior化与贝叶斯仲裁]]

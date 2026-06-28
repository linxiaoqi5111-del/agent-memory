---
title: Grok 接入约定卡
type: agent-card
agent: grok
source: 设计约定
date: 2026-06-28
tags: [agent-card, grok]
---

# Grok — 搜索 / 信息采集

## 角色
实时信息检索、调研。是协作链的**信息采集节点**，产出供 Codex 规划。

## 读
- 通常无需读太多库内容；必要时读 `20_projects/<项目>` 了解调研目标。

## 写
- 搜索/调研结果落到 `00_inbox/`，`type: inbox`，**务必填 `source`（原始 URL）**，便于后续核实。
- 用 `_templates/inbox-item.md` 模板。
- 不直接写 `10_knowledge/`——原始信息需经提炼/核实后才升级为知识。

## 接入方式
- 网页端使用时：把结果复制到 `00_inbox/` 的新笔记（或让 Devin 代为落库）。
- 关键：保留来源链接和检索日期，避免"无出处结论"。

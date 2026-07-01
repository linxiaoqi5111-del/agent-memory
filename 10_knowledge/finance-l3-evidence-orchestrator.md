---
title: 金融 Agent L3 官方证据工具编排
type: knowledge
agent: codex
source: finance-workspace-private L3 evidence orchestrator implementation
date: 2026-07-01
tags: [金融Agent, L3证据, 工具编排, RAG, 证据分层]
status: verified
related: ["[[finance-answer-orchestrator]]", "[[finance-stock-analysis-entrypoint-framework]]"]
---

# 金融 Agent L3 官方证据工具编排

## 核心原则

公告、问询函、互动易这类 L3 官方证据不适合无脑全量向量化：信息量大、时效快、噪音多，容易污染长期知识库。更稳的路径是“运行时工具补查 + 价值事实沉淀”。

数据分工：

- 金融 DuckDB：回答盘面、强度、周期、风格和验证。
- 知识库 wiki/RAG：回答稳定产业结构、公司基础画像、历史研报和概念关系。
- L3 工具：回答最新官方披露、互动易、问询函、风险提示等硬证据边界。
- evidence_index/entity：只沉淀可复用的订单、合同、客户验证、量产、产能、问询函关键回复等事实。

## 通用编排模式

`问题解析 -> 证据缺口检测 -> 工具路由 -> 工具适配器 -> 证据归一 -> 回答注入 -> 价值事实沉淀`

在金融问答里，个股深挖和新闻/公告影响题最容易触发：

- P0：缺客户、订单、合同、中标、量产、产能、投产、认证、问询函、风险提示。
- P1：产业逻辑成立但主要来自研报/观点，需要官方口径验证。
- P2：纯市场风格、策略方法论、双红题材讨论，通常不需要实时查 L3。

## 技术选型

当前优先 CLI 适配器，因为它能复用已有外接公告工具，测试时可以 mock 子进程，不要求常驻服务。

已验证默认入口：

```bash
{python} -m disclosure_lookup.cli company 瑞华泰 --days 30 --source cninfo,sse_einteract
```

默认 `{python}` 应使用当前 finance CLI 的 `sys.executable`，避免 macOS 环境没有 `python` 命令导致 `No such file or directory: 'python'`。如果 disclosure_lookup 安装在独立 venv，用 `FINANCE_L3_PYTHON=/path/to/.venv/bin/python` 覆盖。

验证结论（2026-07-01）：`cninfo` 单源约 1.4 秒；`sse_einteract` 首跑会构建 `sse_uids.json`，2304 条映射，`688323 -> 201868`，实测静默 411.5 秒；缓存后约 24 秒返回大量互动问答，含 `[P1] / [P2]`。因此金融 repo 默认 L3 查询超时应覆盖首跑缓存构建，不能用 30 秒误判失败。后续工程改进方向是给 SSE uid 缓存构建加逐页进度日志，或按股票代码定向解析 uid，减少全市场扫描。

替代方案：

- HTTP API：更适合 Claude、Codex、finhot、网站后端共享调用；代价是要维护服务和权限。
- MCP/tool plugin：更贴近 LLM 原生 tool use；代价是工具注册和运行时更复杂。

推荐路线：CLI 先打通闭环，稳定后抽象成 API/MCP。

## 可迁移性

这套模式能迁移到舆情监控、法律检索、医学文献、企业内网知识库、代码审查等领域。关键不是“有什么工具”，而是先判断回答缺哪类证据，再让工具补证据边界，最后只把高价值事实沉淀进长期知识库。

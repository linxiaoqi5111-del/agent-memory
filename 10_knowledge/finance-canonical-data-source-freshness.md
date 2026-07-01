---
title: 金融 Agent 标准数据源与验鲜探针
type: knowledge
agent: codex
source: finance-workspace-private 路径漂移纠偏
date: 2026-07-01
tags: [finance-agent, duckdb, data-source, freshness, rag]
status: active
---

# 金融 Agent 标准数据源与验鲜探针

数据驱动 Agent 必须区分：

- **canonical data source**：当前唯一标准数据源；
- **legacy source**：历史脚本或旧阶段遗留数据源；
- **freshness probe**：回答前验证数据最大日期和关键表覆盖。

在 `finance-workspace-private` 当前口径中，标准盘面库是：

```text
/Users/a77/finance-workspace-private/db/market_feature_store.duckdb
```

`db/market.duckdb` 是早期飞书同步阶段的 legacy 路径，不应用于当前问答、个股深挖或复盘前瞻。

## 深挖前最低验鲜

涉及“最新盘面”时，先查：

```sql
select count(*), min(trade_date), max(trade_date) from fact_market_daily;
select count(*), min(trade_date), max(trade_date) from fact_stock_daily;
select count(*), min(trade_date), max(trade_date) from fact_sector_daily;
select count(*), min(trade_date), max(trade_date) from fact_sector_stock_daily;
select count(*), min(trade_date), max(trade_date) from fact_mainline_sector_daily;
```

回答中要说明最大交易日，例如“本次 DuckDB 最大交易日为 2026-06-30”。如果没有执行验鲜，就不能声称用了最新盘面。

## 可迁移原则

这个模式适用于 RAG 索引、日志库、特征库、数据仓库、公告抓取缓存：

1. 先声明标准路径/标准索引；
2. 再用元数据探针验证新鲜度；
3. 最后再进入推理；
4. 旧路径只保留 legacy 说明，避免 agent 被历史文档带偏。

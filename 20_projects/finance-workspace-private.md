---
title: 金融项目 (finance-workspace-private)
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/finance-workspace-private (README/AGENTS)
date: 2026-06-28
tags: [project, 金融, 量化, duckdb, 复盘, python]
status: active
related: ["[[knowledge-base-private]]"]
---

# 金融项目 — 项目 MOC

## 概述
- **是什么**：A股**量化复盘 + 研究工具集**。
- **数据来源**：fupanhui.com API（浏览器内 XHR / CDP 代理抓取）、iFinD、AKShare、飞书 Bitable。
- **仓库**：`linxiaoqi5111-del/finance-workspace-private`（private，Python，分支 `main`）

## 目录导览
- `db/` — DuckDB：`schema.sql` 表定义、`market.duckdb` 本地列存分析库
- `scripts/` — `sync_to_local.py`（飞书→DuckDB）、`detect_turning_points.py`（MA5峰谷+放量信号）、`backfill_sector_marginal.py`（板块边际量回填，CDP代理）、`backtest_sector.py`（板块回测）
- `intelligence/` `market_feature_store/` `research/` `evolution/` `复盘/`
- `skills/` — 各分析模块 SKILL.md（注：ingest 类 skill 已于 2026-06-12 迁至 [[knowledge-base-private]] 的 `skills/`）
- `shared/` → 软链到 `~/.claude/shared`（飞书工具库）
- `CLAUDE.md` / `AGENTS.md` — AI agent 项目指令；`UBIQUITOUS_LANGUAGE.md` — 术语

## 数据流
```
fupanhui API ─(CDP proxy)→ backfill_sector_marginal.py → DuckDB / 飞书 Bitable / 飞书表格
飞书 Bitable ─(API)→ sync_to_local.py → DuckDB
DuckDB → detect_turning_points.py / backtest_sector.py → 信号+板块边际量策略分析
```

## 环境要求
- Python 3.9+（duckdb）；Chrome（fupanhui 登录态）；CDP Proxy；飞书凭证 `~/.claude/shared/feishu_config.json`

## 关键约定
- **错误教训唯一沉淀地**：`finance-workspace-private/.claude/lessons_learned.md`（知识库的教训用 `[kb]` 前缀也记到这里）。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
|  |  |  |  |

## 交接记录
- 2026-06-28 · devin · 初次建档（基于 README/仓库结构）

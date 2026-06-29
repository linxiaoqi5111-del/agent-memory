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

# 金融项目 — 项目 MOC（Map of Content，内容地图/目录页）

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
- 2026-06-29 · codex · 新增金融 -> 知识库闭环出口：`agent-daily` 现在基于 `research_queue` 生成 `YYYY-MM-DD-kb-ingest-queue.json`，将概念入库、官方证据、公司边际变化、来源回溯等缺口交给知识库 repo 接收处理；任务包默认 `requires_human_review=true`、`auto_apply=false`。
- 2026-06-29 · codex · 提升问答质量层：新增回答阶段判断与反方审稿上下文，区分“预期交易 / 事实验证 / 兑现分歧”等 A 股阶段；`ask --compose` 会把该上下文注入 LLM 合成提示，`agent` 系统提示也要求主动质疑旧预期、提前交易、一阶/二阶受益、报表弹性和硬事实缺口。
- 2026-06-29 · codex · 新增金融回答质量 rubric：在既有 `agent-eval` 工程门禁之上，增加 `answer-score` 单答案评分器，按本地数据优先、L1-L4 证据分层、盘面阶段、产业推导、反方审稿、结论可用性、双红/流动性等个人方法论贴合度打 100 分；第一版为确定性评分，后续可叠 LLM-as-judge。

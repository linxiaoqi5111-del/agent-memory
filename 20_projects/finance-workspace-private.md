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
- 2026-06-29 · codex · 读取复盘会体系说明 `https://fupanhui.com/workspace/academy/system`，将“资金推动价格，量能决定周期”、20日量能回归、量能/情绪/结构/行业聚散度四维复盘、六段市场周期、板块成交占比环比、市场→板块→个股资金流动路径沉淀进 `intelligence/foresight_methodology.md`，并同步进 agent/compose 提示与 `answer-score` 个人方法论评分项。
- 2026-06-29 · codex · 优化问答质量上下文：`AnswerQualityContext` 新增 `methodology_checks`，把每日全量复盘数据映射成“市场量能、市场情绪、行业聚散度、板块承接、个股确认”五步复盘会路径；`ask` 的分歧反证与后续验证点会显式保留这些检查/缺口，`compose` 提示也注入该路径，避免个股问答直接从公司逻辑跳上涨空间结论。
- 2026-06-29 · codex · 落地问答经验卡片闭环：新增 `users/<id>/experience_cards.jsonl`（gitignore）作为机器学习层，`answer-score --save-card` 可把评分/扣分/修正原则写成卡片；`ask/chat --compose --user <id>` 会检索相关卡片并注入 LLM 合成提示。新增 `docs/learning/README.md` 说明“机器卡片在金融 repo、人类方法论在 agent-memory、事实证据在知识库 repo”的三层边界；同时把潜意识与 checkpoint 回检日志默认 vault 改为显式路径/env/`~/agent-memory`/回退路径。
- 2026-06-29 · codex · 读取策略一/策略四生成逻辑并沉淀为问答方法论：策略一是“主线流动性池内的启动/回流核心确认”，以成交前三行业、双红题材、开根加权强度、新高/多题材命中筛 T1CORE6；策略四是“强者恒强候选池 + 主线 regime 开关”，引擎A 抓加权 Top20 且涨停/重复入榜的大容量动量，引擎B 抓长周期新高且近 8 日多次新高的趋势股。后续问答要把二者当作市场结构语言：先判断主线扩张/拥挤/回流，再判断个股是启动核心、趋势延续、补涨还是高位兑现。
- 2026-06-29 · codex · 读取策略三生成与验证逻辑：策略三是“前期强势核心的分歧回踩/Touch UP 反抽”，不是追高；生成器先限定近 15 个交易日进过单日加权 Top20 的强势池，再用 UP=MA26+0.764×STD26、dev/pdev 判断首次 Touch 或 Touch 后窗口，并把 SELL/RISK 从入选样本中剔除。方法论重点是：先确认核心品种和题材记忆，再看 UP 附近回踩；浅破 -1.5%~0 可容忍，深破<-1.5% 剔除；E1 冰点不等于无脑买，touch 日最多 1/3 底仓，次日首阳或不破 touch 低点再加；共振主线过滤优先，脱离共振的新高/回踩容易是陷阱。
- 2026-06-29 · codex · 补充策略二与策略总原则：策略二是弱市三路径/多周期题材确认，覆盖策略四主升开关关闭时的环境；弱市日优先看跨 1/3/5/10 日周期>=3 的题材且当日未高潮，个股新买入优先题材内低位滞涨补涨腿，弹性腿需 T+1 承接确认，双红穿越核心更多是持仓延续而非新买。用户强调四类策略都是“概率×时间窗口”的方法论，不是静态标签；个股问答必须结合市场环境、板块生命周期、相对强度、位置/筹码、公司事实和反证，输出可审计路径：观察 -> 假设 -> 证据 -> 反证 -> 概率 -> 时间窗口 -> 触发/失效。
- 2026-06-29 · codex · 裕太微问答复盘：用户指出“深挖”不能从题材/策略倒推公司，必须先说清公司本体、主营产品、产业链上下游位置、客户/收入验证、同链相关公司和炒作逻辑生命周期，再把盘面/策略作为辅助视角。已写入 `intelligence/users/linxiaoqi5111/corrections.jsonl`，并新增知识卡 [[finance-stock-deep-dive-first-principles]]；后续个股深挖默认顺序为：公司本体 -> 产业链位置 -> 客户/产品/收入验证 -> 同链对比 -> 炒作逻辑与生命周期 -> 板块主支线与市场环境 -> 反证与后续验证。

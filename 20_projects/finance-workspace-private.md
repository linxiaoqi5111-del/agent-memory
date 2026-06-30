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
- 2026-06-29 · codex · 读取全量盘面体系说明 `https://fupanhui.com/workspace/academy/system`，将“资金推动价格，量能决定周期”、20日量能回归、量能/情绪/结构/行业聚散度四维复盘、六段市场周期、板块成交占比环比、市场→板块→个股资金流动路径沉淀进 `intelligence/foresight_methodology.md`，并同步进 agent/compose 提示与 `answer-score` 个人方法论评分项。
- 2026-06-29 · codex · 优化问答质量上下文：`AnswerQualityContext` 新增 `methodology_checks`，把每日全量复盘数据映射成“市场量能、市场情绪、行业聚散度、板块承接、个股确认”五步市场结构推演路径；`ask` 的分歧反证与后续验证点会显式保留这些检查/缺口，`compose` 提示也注入该路径，避免个股问答直接从公司逻辑跳上涨空间结论。
- 2026-06-29 · codex · 落地问答经验卡片闭环：新增 `users/<id>/experience_cards.jsonl`（gitignore）作为机器学习层，`answer-score --save-card` 可把评分/扣分/修正原则写成卡片；`ask/chat --compose --user <id>` 会检索相关卡片并注入 LLM 合成提示。新增 `docs/learning/README.md` 说明“机器卡片在金融 repo、人类方法论在 agent-memory、事实证据在知识库 repo”的三层边界；同时把潜意识与 checkpoint 回检日志默认 vault 改为显式路径/env/`~/agent-memory`/回退路径。
- 2026-06-29 · codex · 读取策略一/策略四生成逻辑并沉淀为问答方法论：策略一是“主线流动性池内的启动/回流核心确认”，以成交前三行业、双红题材、开根加权强度、新高/多题材命中筛 T1CORE6；策略四是“强者恒强候选池 + 主线 regime 开关”，引擎A 抓加权 Top20 且涨停/重复入榜的大容量动量，引擎B 抓长周期新高且近 8 日多次新高的趋势股。后续问答要把二者当作市场结构语言：先判断主线扩张/拥挤/回流，再判断个股是启动核心、趋势延续、补涨还是高位兑现。
- 2026-06-29 · codex · 读取策略三生成与验证逻辑：策略三是“前期强势核心的分歧回踩/Touch UP 反抽”，不是追高；生成器先限定近 15 个交易日进过单日加权 Top20 的强势池，再用 UP=MA26+0.764×STD26、dev/pdev 判断首次 Touch 或 Touch 后窗口，并把 SELL/RISK 从入选样本中剔除。方法论重点是：先确认核心品种和题材记忆，再看 UP 附近回踩；浅破 -1.5%~0 可容忍，深破<-1.5% 剔除；E1 冰点不等于无脑买，touch 日最多 1/3 底仓，次日首阳或不破 touch 低点再加；共振主线过滤优先，脱离共振的新高/回踩容易是陷阱。
- 2026-06-29 · codex · 补充策略二与策略总原则：策略二是弱市三路径/多周期题材确认，覆盖策略四主升开关关闭时的环境；弱市日优先看跨 1/3/5/10 日周期>=3 的题材且当日未高潮，个股新买入优先题材内低位滞涨补涨腿，弹性腿需 T+1 承接确认，双红穿越核心更多是持仓延续而非新买。用户强调四类策略都是“概率×时间窗口”的方法论，不是静态标签；个股问答必须结合市场环境、板块生命周期、相对强度、位置/筹码、公司事实和反证，输出可审计路径：观察 -> 假设 -> 证据 -> 反证 -> 概率 -> 时间窗口 -> 触发/失效。
- 2026-06-29 · codex · 裕太微问答复盘：用户指出“深挖”不能从题材/策略倒推公司，必须先说清公司本体、主营产品、产业链上下游位置、客户/收入验证、同链相关公司和炒作逻辑生命周期，再把盘面/策略作为辅助视角。已写入 `intelligence/users/linxiaoqi5111/corrections.jsonl`，并新增知识卡 [[finance-stock-deep-dive-first-principles]]；后续个股深挖默认顺序为：公司本体 -> 产业链位置 -> 客户/产品/收入验证 -> 同链对比 -> 炒作逻辑与生命周期 -> 板块主支线与市场环境 -> 反证与后续验证。
- 2026-06-29 · codex · 用户进一步确立问答总原则：所有金融问答必须从第一性原理出发，策略一二三四只是底层市场结构方法论的衍生产物，不代表绝对收益率或正确率；agent 要学习其设计思路并能迁移生成新假设/新策略。个股深挖除目标公司外，还要进入二阶导：沿产业链暴露、客户、瓶颈、替代环节和同链公司发散，像 Serenity Alpha 一样寻找可能更好的投资机会和可验证产业瓶颈。已同步更新 [[finance-stock-deep-dive-first-principles]]。
- 2026-06-29 · codex · 精智达问答纠偏：用户认可产业第一性原理层可到 80 分，但指出缺少每日全量复盘/市场结构推演路径。后续个股深挖必须在“公司本体、产业链瓶颈、客户/订单/收入传导”之后，显式补上大盘阶段、情绪阶段、容量前三行业、双红题材、涨停热度、题材平行关系、高低切/补涨/主线延续、板块发展周期和个股逻辑生命周期；结论要同时回答“产业上为什么成立”和“盘面上现在处于什么生命周期”。已写入 `intelligence/users/linxiaoqi5111/corrections.jsonl` 并更新 [[finance-stock-deep-dive-first-principles]]。
- 2026-06-29 · codex · 精智达市场结构推演路径二次纠偏：用户指出上一版仍像字段 checklist，只能 60 分。新的要求是从策略一二三四抽象市场生命周期推理：大盘层判断初步走强/主升/上升后第一次分歧/反弹/反弹后兑现/探底/冰点修复，并用量能、涨家数、涨跌停、MA5 情绪拐点和市场风格验证；板块层判断双红/涨停热度/容量/平行题材关系下的主线启动、主升扩散、分歧承接、二阶段回流、补涨扩散或高位兑现；个股层判断是否在对应阶段表现出同步强度、相对强度、抗跌回踩、补涨跟随或高位兑现。已更新 [[finance-stock-deep-dive-first-principles]] 与 `corrections.jsonl`。
- 2026-06-29 · codex · 统一 Agent Memory 分层沉淀规则：新增共享 Stop hook `/Users/a77/agent-memory/40_playbooks/check-writeback.sh`，各 repo 的 Claude/Codex `check-writeback.sh` 改为代理到共享策略；四个项目的 `AGENTS.md`/`CLAUDE.md` 与 SessionStart 提示统一为“项目级决策进 `20_projects`、稳定方法论进 `10_knowledge`、单次问答评分/用户纠偏/经验样本进项目学习层”。后续不再把每次对话反馈默认写入项目交接记录，只有升格为项目级规则或稳定方法论时才进入 Agent Memory。
- 2026-06-29 · codex · 修复经验卡片“记了但问答没命中”的问题：`experience_cards.select_relevant_cards()` 新增轻量意图映射，`深挖某股/怎么看某股` 会自动匹配“个股深挖、第一性原理、产业链分析、二阶导、市场结构推演路径”等样板卡；新增单测覆盖 `深挖汇成股份` 命中裕太微/精智达/汇成样板规则。汇成股份这次纠偏本身写入项目学习层 `experience_cards.jsonl` 与 `corrections.jsonl`，不作为 Agent Memory 聊天流水沉淀。
- 2026-06-29 · codex · 将市场结构盘面分析升级为硬性视角：`AnswerQualityContext` 新增 `market_review_checklist`，要求个股深挖/上涨空间回答必须覆盖大盘阶段、量价/20日量能/周均线偏离、MA5情绪与未来5日方向、市场风格、容量前三申万一级与成交占比环比、题材到申万映射、同题材/同行业新高、所属一级涨停结构、双红演变、个股流动性/相对强度/加权涨幅和生命周期身份；缺数据必须显式列缺口。同步新增经验卡片与测试，避免市场结构推演路径退化成可选字段。
- 2026-06-29 · codex · 术语统一：用户要求回答中不再出现“复盘会路径”等措辞，运行时提示、经验卡片、纠偏台账和问答测试统一改为“市场结构推演路径 / 全量盘面推演”；同时把“生命周期身份”明确为“个股逻辑生命周期”，要求输出逻辑从发现、发酵、加速、分歧承接、二阶段回流到兑现退潮中的位置。
- 2026-06-30 · codex · 将 `daily-agent` 底层逻辑并入普通问答入口：`AnswerQualityContext` 新增 daily-agent 推理约束，要求“怎么看/深挖/上涨空间”先判断旧逻辑唤醒/新逻辑候选/数据缺口/噪音，再用生命周期（新出现→旧逻辑唤醒→升温验证→加速定价→高位分歧→衰退观察→证伪退出）、盘面验证强弱、priority/强势股/触发信号变化、历史有效性与研究队列落点组织回答；`llm_refine` 合成提示同步要求市场→板块→个股资金传导、逻辑生命周期、二阶导/产业瓶颈和缺失 daily-agent 数据显式说明，并新增回归测试。
- 2026-06-30 · codex · 将“盘面反向解读”升级为问答硬约束：在保留公司本体/产业链暴露/逻辑生命周期骨架的基础上，普通问答必须从全量盘面数据做正反推导，解释成交额/20日量能回归、涨家数MA5、容量前三、双红、新高、涨停、加权强度分别支持什么、反证什么；尤其要解释强板块弱个股、个股反弹但市场缩量/情绪回落时，市场正在奖励谁、抛弃谁、犹豫谁。已写入 `AnswerQualityContext`、compose 提示、经验卡片意图映射和回归测试。
- 2026-06-30 · codex · 固化晚间卖方与机构胜率发散框架：`AnswerQualityContext` 新增 `sellside_winrate_reasoning`，当证据命中卖方/机构胜率/T+5/T+10/覆盖密度时，要求按“机构胜率 × 覆盖密度 × 证据硬度 × 盘面位置”判断优先发散、只作确认或反向谨慎；经验卡片意图映射新增晚间卖方触发词，并沉淀人类样板 `docs/learning/sellside-winrate-divergence-framework.md` 与知识卡 [[finance-sellside-winrate-divergence-framework]]。
- 2026-06-30 · codex · 建立日度市场前瞻验证闭环：新增项目学习台账 `docs/learning/daily-market-forecast-ledger.md`，用于记录“盘前/前瞻研判 -> 收盘验证 -> 经验修正”，每条研判必须写清当时可得信息、数据缺口、可验证假设、强/中/弱路径和收盘后验证字段；单次研判内容留在项目学习层，只有反复有效的稳定方法论再升级进 Agent Memory。
- 2026-06-30 · codex · 吸收高位主线反证与生命周期分析动作：新增 `AnswerQualityContext.high_position_mainline_reasoning`、经验卡片触发词和人读样板 `docs/learning/high-position-mainline-rebuttal-framework.md`，要求 AI硬件/CPO/PCB/半导体/存储等高位主线回答先看边际预期、流动性、证据硬度、位置约束，再做产业瑕疵审查、事件锚点生命周期和缩量拥挤反证；同步沉淀知识卡 [[finance-high-position-mainline-rebuttal-framework]]。
- 2026-06-30 · codex · 固化个股/题材完整分析路径：新增 `AnswerQualityContext.stock_analysis_entrypoints` 与 `logic_lifecycle_questions`，把“公司本体 -> 产业链暴露 -> 证据层 -> 高位主线反证 -> 大盘流动性 -> 市场风格 -> 行业容量 -> 题材结构 -> 个股相对强度 -> 生命周期四问 -> 二阶导 -> 条件化结论”写入普通问答硬约束；项目学习层新增 `docs/learning/stock-analysis-entrypoint-framework.md`，经验卡片新增“个股与题材完整分析路径”，同步沉淀知识卡 [[finance-stock-analysis-entrypoint-framework]]。

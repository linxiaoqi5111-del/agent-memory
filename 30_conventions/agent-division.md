---
title: 多 Agent 分工约定 (谁接什么 / 什么转给谁)
type: convention
agent: all
source: 客观评估 (2026-06-28)
date: 2026-06-28
tags: [convention, agents, division-of-labor, core, workflow]
status: verified
related: ["[[../50_agents/devin]]", "[[../50_agents/claude]]", "[[../50_agents/codex]]", "[[../50_agents/grok]]", "[[../50_agents/onboarding]]"]
---

# 多 Agent 分工约定

> 前提：各 agent 能力重叠且更新快，本卡是「按相对优势的起手默认值」，**按任务选、不按忠诚度选**。
> 贯穿原则：**想"学会"的部分用会讲解的（Claude/Codex）亲自做；只想"搞定"的部分丢给能跑长任务的（Devin）。**

## 各 agent 优劣与定位

| Agent | 相对优势 | 短板 | 最适合 |
|---|---|---|---|
| **Claude Code** | 代码质量高、大上下文多文件改动稳、最会"边做边讲"、本机直跑 repo（已配 hook） | 原生不联网；超长会话会漂 | 你要学的核心开发：RAG、前端、重构 |
| **Codex** | 系统性推理、架构/算法、结构化产出、第二意见审查 | 偏规划非长程执行；不联网 | 设计与规划、系统设计文档、code review |
| **Grok** | 实时联网（新闻/X/行情/舆情）、找信息源 | 非强编码体；读不到本地文件 | 信息采集 → 落 `00_inbox/` |
| **Devin** | 自主长任务、端到端（clone→跑→测→PR）、可并行、接 CI | 账号一次性、云端 VM、按量计费、交互少 | 可委派的成块执行：批量重构、迁移、测试、CI、抓取 |

## 按仓分配（金融 Agent 项目）

- **`knowledge-base-private`（RAG / 知识图谱）= 大脑，也是最想学的**
  → Codex 出检索架构设计（向量 / Hybrid=BM25+向量+rerank 取舍）→ Claude 亲手实现并讲解。**别整段丢 Devin**（这是面试核心谈资，要亲手过）。
- **`finance-workspace-private`（Python / DuckDB / 飞书 / CDP 抓取）= 数据层，偏机械**
  → Devin 执行（抓取、入库、批量）；Grok 找数据源；难点拉 Claude 讲。
- **`finhot`（Electron/React/TS）= 产品**
  → Claude 做功能 + 学前端；规格清晰的大功能/测试/CI 交 Devin。
- **`finance-research-site`（Astro/Cloudflare）= 对外站**
  → Grok 供素材 → Claude/Devin 落地页面/部署。

## 协作闭环

> **Grok 采集 → Codex 规划/架构 → Claude 实现(学) 或 Devin 执行(委派) → 分层沉淀 → 下一轮**

vault 是共享记忆：Grok 的料进 `00_inbox/`，提炼进 `10_knowledge/`；Codex 的设计 + 项目级任务看板进 `20_projects/<repo>.md`；单次问答评分、用户纠偏、案例样本进项目内学习层；干完按 `40_playbooks/devin-writeback.md` 做分层沉淀。

## 学习 + 面试导向

- 核心检索/RAG 用 Claude 亲手做，每步讲"为什么这么选 / 替代方案差在哪"——大厂系统设计常考。
- 让 Codex 把做过的东西写成"系统设计文档"（架构图、权衡、容量估算）进 `10_knowledge/`，既沉淀也是面试材料。
- Devin 用来解放双手：把已懂的、重复的活批量交它，省时间学新东西。

## 给 agent 的一句话（开工时自检）
- 我接到的活，是不是更该转给更合适的 agent？（采集→Grok / 架构→Codex / 学习型实现→Claude / 委派型执行→Devin）
- 干完是否按 `40_playbooks/devin-writeback.md` 判断了沉淀层级：项目级写 `20_projects/<repo>.md`，稳定方法论写 `10_knowledge/`，样本级反馈写项目学习层？

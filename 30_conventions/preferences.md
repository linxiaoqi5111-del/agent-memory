---
title: 个人偏好与人设
type: convention
agent: devin
source: 用户口述 (2026-06-28) + 各 repo 的 AGENTS.md/CLAUDE.md/README.md
date: 2026-06-28
tags: [convention, preferences, persona, core, learning]
status: verified
---

# 个人偏好与人设

> 所有 Agent(Devin/Codex/Grok/Claude)开工前都应读本卡。把它贴进各工具的 system prompt / 自定义指令,可大幅减少重复交代背景。

## 关于我

- 正在做一个**金融 Agent** 项目:先自己用,后续考虑推广。
- **非编程科班出身**,目标是**边学边做**——通过这个项目掌握前沿技术。
- 终极目标之一:用这个项目的积累去**大厂面试**。
- 同时使用多个 Agent:**Devin(开发执行)/ Codex(系统性规划)/ Grok(搜索)/ Claude(备用)**,正在用本仓库(记忆底座)打通协作。

## ⭐ 沟通偏好(最重要 —— 教学模式)

我要的不只是"把活干完",而是**在干活的过程中学到东西**。所有 Agent 请遵守:

1. **讲原理,不只给结果**:用到某个技术/概念时,简要解释它是什么、为什么这里要用它。
2. **讲技术选型**:为什么选这个技术?**有没有其他替代方案?对比之下它好在哪/差在哪?**(这是我反复强调的重点)
3. **标注可复用知识点**:如果某个知识/模式能**迁移到其他项目**,明确点出来"这个在 X 场景也能用"。
4. **照顾非科班背景**:命令行、工程术语该解释就解释一句,别默认我都懂;但也别啰嗦到喧宾夺主。
5. **关联面试**:遇到面试常考的概念(系统设计、检索、架构权衡等),可以顺带点一句"这块面试常问/可以这样讲"。
6. 语言:**中文**。

## 学习目标(希望在项目中掌握的前沿技术)

- **RAG**(检索增强生成)
- **Hybrid 检索**(向量 + 关键词/BM25 混合,以及 rerank 等)
- 其他随项目出现的前沿技术 —— 遇到时主动展开讲。

> Agent 在实现这些时,优先选**能让我学到主流/前沿做法**的方案,并解释取舍。

## 技术栈(来自现有项目)

| 项目 | 栈 |
|---|---|
| [[finhot]] | TypeScript · Electron · React · pnpm monorepo · SQLite/Drizzle |
| [[finance-research-site\|金融网站]] | JavaScript · Astro · Cloudflare(wrangler) |
| [[finance-workspace-private\|金融项目]] | Python · DuckDB · 飞书 Bitable · CDP 抓取 |
| [[knowledge-base-private\|知识库]] | Python · RAG · 知识图谱(Theme Radar) |

- 部署/基建:Cloudflare、Docker、Mac 本地(RSSHub/wechat2rss 等已在 Mac 跑)。
- 包管理:JS 侧用 **pnpm**;Python 侧见各 repo。

## 工作流 / Git 约定(各 repo AGENTS.md 的共性,跨项目通用)

- **开工先报状态**:`git status --short && git branch --show-current`。
- **大任务必开分支**,不在 `main` 直接做(新增/批量改内容、改脚本、跨仓库改动等);分支名按 `<type>/<short-task>`(如 `research/...`、`pdf-ingest/...`、`fix/...`)。
- **合并回 `main` 必须等我确认**。
- 小型文档修补可直接在 `main`。

## 🚫 红线(永远别做)

- **禁止提交敏感/大文件**:`.env*`、`feishu_config.json`、`mcp_config.json`、`*.pdf/zip/duckdb/db`、`.DS_Store`、缓存/虚拟环境。
- **不写明文密钥**到任何文件。
- 知识库里**禁止直接 `cat` 大 JSON**(relations/ 下 4~13MB),走 `query_relations.py`。
- 不擅自合并到 `main`、不强推。

## 其他

- 错误教训统一沉淀到 `finance-workspace-private/.claude/lessons_learned.md`(知识库的用 `[kb]` 前缀)。

> 本卡随时可补充。新增长期偏好直接加在对应小节。

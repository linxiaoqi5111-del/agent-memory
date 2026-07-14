---
title: 项目总览
type: project
agent: devin
source: 仓库盘点
date: 2026-06-28
tags: [project, index, moc]
---

# 项目总览 (Projects MOC)

当前纳入记忆底座的项目（均为 `linxiaoqi5111-del` 名下仓库）：

| 项目 | 仓库 | 定位 | 技术栈 |
|---|---|---|---|
| [[finhot]] | finhot (public) | 金融 RSS 信息流阅读器 | Electron + React + TS |
| [[finance-workspace-private\|金融项目]] | finance-workspace-private | A股量化复盘+研究工具集 | Python + DuckDB + 飞书 |
| [[knowledge-base-private\|知识库]] | knowledge-base-private | LLM 维护的金融知识图谱/Wiki | Python + RAG |
| [[finance-research-site\|金融网站]] | finance-research-site | 面向读者+AI检索的研究网站 | Astro + Cloudflare |
| [[金融Agent面试学习]] | agent-memory | 金融 Agent 大模型面试教材、教学计划与跨账号进度交接 | Markdown + Obsidian |

## 金融内容矩阵（它们怎么串起来）
```
knowledge-base-private  ──(知识/synthesis)──►  finance-research-site (对外研究文章)
        ▲                                              
        │ ingest/RAG                                   
finance-workspace-private (量化复盘/数据)              finhot (信息流阅读器/采集)
```

> 每个项目的任务看板、关键决策、交接记录都在各自的 MOC 里维护。新项目按 `_templates/project.md` 新建。

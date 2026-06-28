---
title: 金融网站 (finance-research-site)
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/finance-research-site (README/AGENTS)
date: 2026-06-28
tags: [project, 金融网站, astro, cloudflare, seo, geo, javascript]
status: active
related: ["[[knowledge-base-private]]", "[[finhot]]"]
---

# 金融网站 — 项目 MOC

## 概述
- **是什么**：面向**读者与 AI 检索（GEO）**的金融产业研究网站。
- **仓库**：`linxiaoqi5111-del/finance-research-site`（private，JavaScript/Astro，分支 `main`）
- **注意**：`main` 是共享基线但**仍在持续修缮**，不代表已稳定。

## 技术栈
- **Astro** 静态站（`astro.config.mjs`）
- **Cloudflare** 部署（`wrangler.jsonc`）
- 内容用 Markdown frontmatter 管理（标题/摘要/分类/标签/日期）

## 目录导览
- `src/content/research/` — 研究文章（Markdown）
- `src/` — Astro 页面/组件；`public/` — 静态资源
- `scripts/` — 导入/生成脚本（含 `llms-full.txt` 等 GEO 文件）
- `docs/` `AGENTS.md` `CLAUDE.md`

## 关键命令
```bash
npm install
npm run dev
npm run build
```

## 强制规则（来自 AGENTS.md）
- 开工先 `git status --short && git branch --show-current` 并汇报。
- **大任务不在 `main` 直接做**：新增/批量导入文章、改 `src/content/research/`、改 SEO/GEO 文件、改 Astro 页面/组件、改导入脚本、批量生成 `llms-full.txt` 等，必须从最新 `main` 新建任务分支；合并回 `main` 需用户确认。
- 分支命名：`research/<文章/主题>`、`content/<主题>`、`seo/<问题>`、`site/<页面/组件>`、`fix/<问题>`。
- 禁止提交：`.env*`、`mcp_config.json`、`feishu_config.json`、`*.pdf/zip/duckdb/db` 等。

## 关联
- 研究内容与 [[knowledge-base-private]] 的 wiki/synthesis 互为上下游（知识 → 文章）。
- 与 [[finhot]] 同属金融内容矩阵：site 是**研究文章网站**，FinHot 是**信息流阅读器**。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
|  |  |  |  |

## 交接记录
- 2026-06-28 · devin · 初次建档（基于 README/AGENTS）

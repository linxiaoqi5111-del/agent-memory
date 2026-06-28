---
title: FinHot · 金融信息流阅读器
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/finhot (README/AGENTS)
date: 2026-06-28
tags: [project, finhot, rss, electron, typescript]
status: active
related: ["[[finance-research-site]]"]
---

# FinHot — 项目 MOC

## 概述
- **是什么**：本地优先的**金融 RSS 信息流阅读器**。聚合财经 RSS + 微博/雪球/微信/X，自动打分、AI 摘要、AI 中译。
- **基底**：基于 [Focal](https://github.com/nextcaicai/Focal)（[Folo/RSSNext](https://github.com/RSSNext/Folo) 的 fork）构建，复用其 RSS 引擎、本地 SQLite、BYOK AI 框架、Electron 壳。
- **形态**：macOS/Windows/Linux 桌面应用，亦可部署为公网站点。
- **License**：AGPL-3.0。
- **仓库**：`linxiaoqi5111-del/finhot`（public，TypeScript，分支 `main`）

## 技术栈
- Electron + Vite + React（Renderer：RSS 时间线 / 条目详情 / 订阅管理）
- Main Process：RSS 定时采集、服务端富集（打分/摘要/翻译）、本地 SQLite（Drizzle ORM）
- Monorepo：pnpm workspace + turbo；共享包 `@follow/components`、`@follow/utils`、`@follow/database`

## 目录导览（仓库根）
- `apps/` `api/` `packages/` `plugins/` — 主代码
- `scripts/` `docs/` `wiki/` `locales/`
- `pnpm-workspace.yaml` `turbo.json` `package.json`

## 关键命令
```bash
pnpm install
cd apps/desktop && pnpm run dev:web       # 开发（浏览器，推荐）
cd apps/desktop && pnpm run dev:electron  # 完整 Electron
pnpm run build:web
```

## 关键信息 / 关联
- 富集所用的微信源经 wechat2rss / RSSHub 提供（Mac 上有 RSSHub localhost:1200、wechat2rss）。
- 与 [[finance-research-site]] 同属金融内容矩阵，但定位不同：FinHot 是**阅读器/信息流**，site 是**研究文章网站**。

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|---|---|---|---|
|  |  |  |  |

## 交接记录
- 2026-06-28 · devin · 初次建档（基于 README/仓库结构）

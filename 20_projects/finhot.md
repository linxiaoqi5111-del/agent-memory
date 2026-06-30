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

- 2026-06-30 · devin · 公网快照回归排查 + 修复（微博旧源 / 公众号<25）
  - **公众号<25**：非代码问题。`passesScoreGateServer` 一直把公众号卡在 qualityScore>=25；线上实测最低 32，无 <25。cninfo 白盒源 <25 是 #86 设计（whitebox 绕过分数门）。
  - **微博旧源"复活"根因**：`/api/public/refresh` 是**增量**导入——从 watchlist 删掉的源不会自动从缓存移除，旧 feed 的条目仍留在 `.finhot-cache` 并被 `/api/public/deploy` 重新发布。**仅改 watchlist 不够，必须 prune 缓存**。
  - **缓存真实路径**：`apps/desktop/.finhot-cache`（devweb 以 apps/desktop 为 root），不是仓库根的 `.finhot-cache`。
  - **本次处理**：PR #88 把 watchlist weibo 50→5、+22 公众号、+cninfo L3 rss；手动从 manifest+entries 删除 43 个旧微博 feed；deploy-public-only.sh 重新部署。线上 finhot.industry7view.com 已为：公众号<25=0、微博只剩 curated 5（当前仅 2014433131 有过线内容）。
  - **可复用知识**：增量缓存系统里"删订阅"要同时处理"缓存裁剪"，否则旧数据阴魂不散——这在 RAG 的向量库/索引同步里同理（删文档要同步删 embedding）。

- 2026-06-30 · codex · PR #91 / 巨潮 cninfo-rss 准入评审
  - PR #91 本身只恢复 expanded 微信公众号列表，巨潮 RSS 源只是保留既有 `http://localhost:8787/l3-hard-delta.xml`，真正的巨潮逻辑在 PR #84/#85 和 `skills/cninfo-rss/`。
  - L3 边界方向正确：只读标题+元数据，因此产物应为 `L1_L3_candidate` + `fact_hardness=review_candidate` + `review_required=true`，不能直接写成 `L3 hard_fact`。
  - 准入门槛需修：`config.yaml` 中 `category_yjkb_szsh` 在巨潮前端分类枚举中未出现，实测会返回大量全量公告；`category_zj_szsh` 官方含义是“中介报告”，不是“增减持”。这两项会让 `hard_delta` 噪音很高。
  - 建议：删除/禁用 `category_yjkb_szsh`，把业绩快报改为标题关键词精确匹配；把增减持改走 `category_gqbd_szsh` 或标题关键词二次校验；分类命中后仍需标题正则/排除词二次校验，`hard_delta.xml` 只放高确定性标题。
  - 验证：标准 Python 与 Codex Python 均缺 PyYAML，直接单测会 ImportError；用进程内 yaml shim 跑离线逻辑测试 15 项通过。真实样本 dry-run（近 3 天、每源 1 页）抓到 201 条，其中 hard 132 / review 69，样本暴露分类噪音问题。

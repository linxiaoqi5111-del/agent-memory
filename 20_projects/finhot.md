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
| cninfo-rss L3 准入收紧（标题二次校验 + 组合规则 + 纠正分类码） | devin | done | PR #92 |

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

- 2026-06-30 · devin · 落实 cninfo-rss 准入收紧（PR #92，接 codex 评审）
  - **classify() 改「粗筛 → 准入门」两段式**：分类码命中后必须过分类内 `title_include_any/title_exclude_any` 二次校验；不再 `category in cat_map => hard_delta`。
  - **分类码纠正**：`category_yjkb_szsh`（业绩快报）返回全量公告 → enabled:false，改走标题关键词；`category_zj_szsh`（=中介报告）→ `category_gqbd_szsh`（=股权变动）+ 标题须含 增持/减持/权益变动/持股变动/股份变动。
  - **新增 `hard_delta_combo_rules`**：宽词（签订/产能/亏损/增持/减持）单独命中只算 review_candidate，需配伴随词（签订+合同/订单、产能+投产/达产）才升 hard_delta。扩充 exclude_any（担保/问询函/关注函/回复/股东会决议/风险提示等）。
  - **命名纠偏**：feed `l3-hard-delta.xml → l3-candidates-hard-delta.xml`，标题「巨潮 L3 候选 · 高确定性公告」。⚠️ **FinHot 订阅 URL 需同步改**为 `…/l3-candidates-hard-delta.xml`（旧 URL 会 404）。
  - **验证**：本机装 PyYAML 后单测 21/21（新增准入门 3 + 组合规则 3）；直连 cninfo live dry-run（近 3 天、每源 1 页）fetched=189 / hard=118 / review=71，hard 合集已完全排除担保/问询函/回复/股东会决议/风险提示/招股等噪音。`category_gqbd_szsh` live 返回确为减持/权益变动类，纠正成立。
  - **环境坑**：Mac 本机 python3 缺 PyYAML，dry-run/单测会 ImportError；本次发现 cninfo 从 Devin 机器可直达，故未动 Mac、直接本地跑 live dry-run。建议给 Mac 装 PyYAML 以便本地跑。

- 2026-07-01 · codex · `feat/disclosure-lookup` 分支试跑验证
  - **环境**：用临时 git worktree 拉 `origin/feat/disclosure-lookup`（提交 `89aefd4`），`python3.12` venv 安装 `disclosure_lookup/requirements.txt` 成功；本机 Python/OpenSSL 为 Homebrew Python + OpenSSL 3.x。
  - **验证结果**：`python -m unittest discover -s disclosure_lookup/tests` 通过 61/61；`company 瑞华泰 --days 30 --source cninfo` 约 1.4s 返回公告；首次 `sse_einteract` 需要构建全市场 uid 缓存，实测 2304 条映射耗时 411.5s，`688323 -> 201868`。
  - **运行坑**：首次 SSE 没有逐页进度输出，长时间静默看起来像卡死；缓存写入 `disclosure_lookup/.cache/sse_uids.json` 后，`sse_einteract` 单源约 24s 返回，组合命令 `cninfo,sse_einteract` 约 1.4s 端到端成功。
  - **建议**：给 SSE uid 缓存构建加进度日志/提示，或改成按股票代码定向解析 uid，避免新 Mac 首跑等待 6-7 分钟时误判失败。

- 2026-07-02 · devin · cninfo-rss 细颗粒度订阅 + 硬筛选收紧（PR https://github.com/linxiaoqi5111-del/finhot/pull/97，待用户确认合并）
  - **样本驱动**：实拉 2026-06-18~07-02 巨潮真实公告（24 关键词×数百标题）逐类审读后定规则，不是拍脑袋加词。
  - **细颗粒度**：新增 `feeds/by-fact-type/{fact_type}.xml`，每个事实类型独立 Atom feed（订单/客户定点/注册获证/量产/增减持…），FinHot 可按类型订阅。
  - **新增高价值类型**：定点(customer_validation)、注册证/获批上市/临床试验批准(regulatory_approval)、CE认证、授权许可(license_out)、交割完成(acquisition)。
  - **收紧噪音**：exclude 新增 监管协议/管理办法/资产评估报告/财务顾问/报告书摘要/发明专利；降级新增 中标候选人/拟中标/注册证变更；combo 新增 定点/注册证/收购。
  - **关键坑**：`_contains_any` 按列表序返回首个命中 → 特异词（授权许可）必须排在宽词（签订）前，否则 fact_type 归错。关键词规则引擎通用教训：匹配优先级=列表顺序时，specificity 要显式排序。
  - **验证**：单测 35/35（新增 12 例用真实标题回归）；live dry-run 3 天窗口 211 候选/hard 130，抽查 regulatory_approval、order_contract feed 全为高价值公告。

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

- 2026-07-03 · devin · 积压 5 PR 评测后经用户确认全部合入 main（顺序 #102→#89→#93→#94→#97）。要点：①#94/#97 的 CI lint 失败是 main 上 `scripts/precommit.mjs` 未过 prettier 的存量问题（b481f23 引入），#102 顺手修了，故 #102 必须先合；②#94 与 #97 在 `skills/cninfo-rss/config.yaml` 排除词列表真冲突（并行分支各自加词），经用户授权按**并集**解决（排除词并集只多滤噪音、误伤风险低；「财务顾问」覆盖「独立财务顾问」去重）。合并后 main CI 全绿、cninfo 测试 24/24 过。**可复用教训**：并行 PR 同改一份关键词配置时，先判断是"并行补充"还是"后者推翻前者"，排除类列表默认并集、准入类列表需逐词裁决。

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

- 2026-07-02 · devin · L3 CLI（disclosure_lookup）优化（PR https://github.com/linxiaoqi5111-del/finhot/pull/98，堆叠在 feat/disclosure-lookup 上，先合底座再合本条）
  - **CLI 输出控制**：company/keyword/evidence 通用 `--level P0,P1` / `--sort triage` / `--limit N` / `--json`（含 is_reverse，供 agent 消费）；evidence 展示可筛但证据卡生成用全量。
  - **修 SSE uid 静默痛点**：首次 6-7 分钟构建现在 stderr 报进度（每 10 页）+ 增量落盘（中断不丢已爬）。可复用点：进度走 stderr、数据走 stdout，管道消费不受污染。
  - **triage 前向兼容 #97**：_LIFECYCLE_HIGH += regulatory_approval，MID += license_out；#97 合入后"中标候选人"会自动降级（triage 复用 cninfo classify）。
  - **验证**：单测 64/64（新增 3 例）；live keyword 中标 --sort triage 正常。

- 2026-07-03 · devin · 依赖安全审计第一轮（PR https://github.com/linxiaoqi5111-del/finhot/pull/104，CI 全绿待用户确认合并）
  - **范围**：GitHub Dependabot 328 告警中的 5 个 critical 全部修复——vitest 3.2.4→3.2.6（直接依赖 patch 升级）+ pnpm.overrides 钉 shell-quote≥1.8.4 / protobufjs≥7.6.1 / handlebars≥4.7.9（均为传递依赖 patch 级）。
  - **关键坑**：pnpm 10.17 只认根 package.json 的 `pnpm.overrides`，写进 pnpm-workspace.yaml 的 overrides 不生效（该节只服务 catalog）；renderer 测试依赖 @follow/electron-main 的 dist 类型，跑全量 test 前须先 `pnpm --filter @follow/electron-main build`。
  - **验证**：typecheck 13/13、test 全绿（155+39+65+46）、prettier 过；lockfile 确认 4 个漏洞版本全部升级。
  - **遗留**：130 个 high 告警已在 PR 内分桶评估——patch/minor 可低风险 override 的一批（tar/minimatch/tmp/node-forge 等）、需评估的 major（electron 38→39、vite、axios、react-router、drizzle-orm 钉版原因不明），建议按桶分 PR 跟进。

- 2026-07-03 · devin · SEO/GEO 基础设施（PR https://github.com/linxiaoqi5111-del/finhot/pull/102，待用户确认合并）
  - **背景**：线上审计发现除首页外全部路径命中 SPA 兜底；Cloudflare「托管 robots.txt」（Content Signals）默认 Disallow GPTBot/ClaudeBot/CCBot/Bytespider/Google-Extended 等 AI 爬虫。
  - **改动**（`rss-proxy.ts` 部署管线 `buildPublicSnapshotFiles`）：新增 robots.txt（显式 Allow 18 个搜索/AI 爬虫）、sitemap.xml（首页+过审条目 /items/<id>，带 lastmod）、llms.txt（llmstxt.org 规范）；每次部署把每条过审条目预渲染为静态 `items/<id>.html`（`isStaticPageSafeId` 白名单防路径注入）；详情页/首页补 canonical、OG、NewsArticle/WebSite JSON-LD；dev server 加三个镜像中间件。新增 `PUBLIC_CANONICAL_BASE`（默认 https://finhot.industry7view.com，sitemap/canonical 必须绝对 URL）。
  - **线上已生效**：用用户提供的 CF token（secrets: CLOUDFLARE_API_TOKEN_FINHOT / CLOUDFLARE_ACCOUNT_ID_FINHOT）从 Devin 机器完成一次临时部署——从线上 index.html 内嵌 JSON（var feeds/entriesByFeed/allEntries/enrichments）**反向重建 .finhot-cache**，起 dev:web 后 POST /api/public/deploy。sitemap/llms/静态详情页/feed.xml/api/public/*.json 全部真实可访问。可复用技巧：静态站内嵌数据可反推出部署所需缓存。
  - **未完成**：/robots.txt 仍被 CF zone 级托管 robots.txt 覆盖（zone industry7view.com=22af35e4fe4274bb58a0e6380c77b5ea）。用户 token 缺 Zone→Bot Management:Edit / Zone Settings:Edit 权限，已请用户在 dash.cloudflare.com/profile/api-tokens 补权限后由 Devin 关闭（bot_management API）。
  - **CI 坑**：main 上 format:check 一直红（4 文件 prettier）+ precommit.mjs 5 个 regexp/no-unused-capturing-group，本 PR 顺手修了（捕获组→非捕获组）。环境坑：Devin box corepack 签名 bug 需 `COREPACK_INTEGRITY_KEYS=0`；vite 要 Node ≥20.19（`sudo n 22`）；`@rolldown/binding-linux-x64-gnu` 需手动装（勿提交 package.json）。

- 2026-07-07 · codex · FinHot 短视频制作包已落到 `docs/marketing/finhot-short-video-script.md`，可作为 Vibe Motion / HyperFrames / Remotion 的唯一输入生成 9:16、75 秒 motion 成片。包内含 HKRR 叙事、11 个 Shot 分镜、旁白全文、15 秒切片版、录屏素材清单、产品事实库、音轨/字幕规范、JSON 时间线提示和发布检查清单。交接给其他 IDE 时需强调：产品名是 FinHot（不是复盘会/fupanhui），按 §3 分镜和 §6 录屏取材，产品录屏不少于 40 秒，片尾保留合规免责声明和公网 URL，不添加收益承诺或买卖指令。此次只需项目级交接记录，不另建 `10_knowledge/`。

- 2026-07-07 · codex · 已按 `docs/marketing/finhot-short-video-script.md` 执行生成 HyperFrames 竖版短视频工程：`docs/marketing/finhot-short-video-motion/`。交付物包含 `design.md`、`.hyperframes/expanded-prompt.md`、`index.html`、本地化 GSAP runtime、产品截图素材、QA 抽帧和渲染产物 `renders/finhot-short-video.mp4`。验证：`npx hyperframes lint --verbose` 0 error；`npx hyperframes inspect --samples 18` 0 layout issues；渲染输出 H.264 1080×1920、30fps、75.000s、约 16MB。注意：当前版本是无旁白音频的视觉/字幕成片，后续如补 `assets/narration.wav` 可接入音频轨；工程单文件约 312 行，长期维护可拆 11 个 sub-composition。

- 2026-07-07 · codex · FinHot 短视频 logo 纠偏：用户确认应使用公网品牌图（`/Users/a77/Downloads/grok-image-cba4d813-de56-40b2-80e4-0a966096955c.jpg`，完整 FINHOT 字样 + 火焰箭头），不是仓库 `finhot-logo.svg` 的小火焰图标。已复制为 `docs/marketing/finhot-short-video-motion/assets/finhot-public-logo.jpg`，替换 Logo Reveal / Slogan / CTA 三处 logo，并重渲染 `renders/finhot-short-video.mp4`。验证：lint 0 error（仅复用 logo 与单文件偏大 warning）、inspect 18 samples 0 layout issues、输出仍为 H.264 1080×1920、30fps、75.000s。

- 2026-07-08 · codex · 短视频公网 logo 二次校验：同名覆盖 `renders/finhot-short-video.mp4` 后抽帧仍显示旧小火焰图标，判断为 HyperFrames/播放器缓存或重复媒体发现导致。已改为三份唯一素材名（`finhot-public-logo-reveal/slogan/cta.jpg`，hash 均等于用户提供图片）、删除旧 motion assets 中的 `finhot-logo.svg/png`、composition id 改 `finhot-promo-public-logo-v2`，并输出新文件 `renders/finhot-short-video-public-logo-v2.mp4`。已从新 MP4 抽 11s/73s 帧验证，均显示完整 FINHOT 公网图。

- 2026-07-08 · codex · 已评审用户桌面版 `finhot-promo-75s.mp4`（实际 80.15s，Remotion 输出）：抽帧拼图与音频统计产物放在 `docs/marketing/finhot-short-video-motion/review/finhot-promo-75s/`，评审文档为 `voice-and-visual-review.md`。结论：配音 AI 感主要来自响度偏低（约 -26.6 LUFS）和动态起伏窄（LRA 约 3.8 LU），建议重新分段生成/真人录口播并标准化到 -16~-18 LUFS；画面建议优先改开头 0-1s Hook、截图局部放大、结尾完整公网 logo 强露出、减少底部字幕重复。

- 2026-07-09 · codex · 用户补录真人口播 `20260709_095609.m4a`（100.76s）。已在 `docs/marketing/finhot-short-video-motion/review/user-voice-20260709/` 生成处理链路与记录：自动剪停顿后强剪版约 83.2s，再轻微变速贴合现有 80.1s 视频，最终音轨 `user-voice-fit-80s-final.m4a` 约 -18.3 LUFS / -1.9 dBFS true peak。已输出桌面预览 `/Users/a77/Desktop/finhot-promo-user-voice-preview.mp4`。注意：该预览替换了原音轨，暂不含 clean BGM；正式版建议要么把 motion 时间线扩到约 83s 保留自然停顿，要么人工删句/剪停顿后再配 clean BGM ducking。

- 2026-07-09 · codex · 已执行短视频真人口播正式后期：基于用户录音保留 83.2s 自然停顿，重新安全限峰后得到 `user-voice-83s-final.m4a`（约 -18.2 LUFS / -1.9 dBFS true peak）；用 FFmpeg 将桌面 Remotion MP4 画面 `setpts=1.038701623*PTS` 拉长匹配，并在 CTA `75s-83.2s` 叠加公网完整 FINHOT logo（560px 宽，y=135）。最终推荐版在 `/Users/a77/Desktop/finhot-promo-final-83s.mp4`；另有轻合成环境底预览 `/Users/a77/Desktop/finhot-promo-final-83s-with-bgm.mp4`。处理参数已补到 `docs/marketing/finhot-short-video-motion/review/user-voice-20260709/processing-notes.md`。

- 2026-07-09 · codex · 修正短视频真人口播与字幕不同步问题：根因是桌面 Remotion 版 `finhot-promo-75s.mp4` 的字幕/镜头稿实际来自 `/Users/a77/Desktop/finhot-vo-script.md`（80s、s01-s11），而非早期 `docs/marketing/finhot-short-video-script.md` 或 voice-director 改写稿；此前 83s 全局拉长会让烘焙字幕错位。已改为保持原 80.1s 视频不变，把用户录音按静音边界切成 11 段并逐段 fit 到 `s01-s11` 时长，输出 `/Users/a77/Desktop/finhot-promo-final-80s-audio-sync.mp4`；分段映射和注意事项已记录在 `docs/marketing/finhot-short-video-motion/review/user-voice-20260709/processing-notes.md`。注意：s10 源 take 需 1.649x 压缩，若要更自然，应重录 s10 到约 8.5s 或重渲染画面字幕。

- 2026-07-09 · codex · 二次确认短视频字幕/口播稿混用问题：此前给用户的 voice-director 稿（“你每天早上打开手机…”）与当前 Remotion 视频字幕稿完全不是同一版，不能用于给 `finhot-promo-75s.mp4` 录音。已新增 `docs/marketing/finhot-short-video-motion/review/user-voice-20260709/correct-recording-script-for-current-video.md`，明确当前视频唯一可用口播稿为 `/Users/a77/Desktop/finhot-vo-script.md` 的 s01-s11 版本；后续若保留当前视频画面/字幕，必须按该稿重录或分段录制，不能再混用早期 marketing 长稿。

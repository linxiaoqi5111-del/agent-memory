---
title: vidio · 短视频运营（抖音起号）
type: project
agent: grok
source: 对话共创 + https://github.com/linxiaoqi5111-del/vidio branch ops/short-video
date: 2026-07-10
tags: [project, vidio, douyin, short-video, ops, finhot]
status: active
related: ["[[finhot]]", "[[finance-workspace-private]]"]
---

# vidio 短视频运营 — 项目 MOC

## 概述
- **目标**：为 FinHot + 金融 Agent 做抖音冷启动与内容获客；Grok 任运营顾问。
- **状态**：active（分支 `ops/short-video`，知识资产已起）
- **工作仓**：本机 `/Users/a77/vidio`（GitHub `linxiaoqi5111-del/vidio`）
- **负责**：human 拍发 · grok 策略/脚本/复盘

## 架构决策（重要）
- **不新开 Obsidian vault**。长期记忆继续用本 vault；项目 SSOT 在 `vidio/ops/`。
- 详见仓内：`ops/knowledge/obsidian-decision.md`

## 项目内 SSOT 路径（vidio）
| 路径 | 内容 |
|------|------|
| `ops/knowledge/` | 钩子 playbook、冷启动假设、skill 目录、流水线 |
| `ops/douyin/` | 策略、排期、脚本、复盘、钩子库 |
| `ops/shared/principles.md` | 合规与起号原则 |
| `industry7view-card-lab/` | 成片生产（行业卡/Remotion） |
| `短视频演讲稿/` | 题材母稿 |

## 关键决策（2026-07-10 用户确认）
- 旧号 **弃用** · **开新号**
- 主叙事：**Deep Fomo 研究过程**；FinHot 第 16 条后软植入
- 出镜：**情绪素材 + 屏幕**（约 0–3.5s 硬切）
- 前 10 条：框架优先、少点具体票
- Industry 7View：**偶尔插 1 条**（每 6–8 条 ≤1）
- 前 15 条禁止硬广/外链/报票 CTA
- 完播+评论优先于播放量

## 任务看板
| 任务 | 负责 | 状态 | 备注 |
|------|------|------|------|
| 仓库清理 + ops 骨架 | grok | done | branch ops/short-video |
| 知识资产首批入库 | grok | done | hooks/skills/coldstart |
| 全 repo 起号规划 | grok | done | launch-plan.md |
| 决策锁定写入文档 | grok | done | 情绪+屏幕 / 偶插 / 弃旧开新 |
| 新号资料定稿 | human | todo | profile-copy 昵称三选一 |
| 前 7 条可拍脚本 | grok | todo | 等昵称或直接开工 |
| face-hook 素材规范 + 试渲染 | both | todo | kit + 情绪段 |
| 发布后复盘闭环 | both | todo | reviews/ |

## 相关知识
- 项目内全文：vidio `ops/knowledge/README.md`、`ops/douyin/launch-plan.md`
- 产品：[[finhot]] · [[finance-workspace-private]]

## 交接记录
- 2026-07-10 · grok · 建 MOC；沉淀 hooks/skills/算法假设到 vidio/ops/knowledge
- 2026-07-10 · grok · 用户确认：情绪+屏幕、产业偶插、弃旧开新；更新排期与 strategy

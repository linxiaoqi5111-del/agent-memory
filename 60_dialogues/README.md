---
title: 对话记录模块（Knevo 蒸馏语料库）
type: convention
agent: devin
source: 用户需求（2026-07-08 会话：蒸馏 Knevo 问答）
date: 2026-07-08
tags: [dialogues, knevo, distillation, corpus]
status: verified
related: ["[[knevo-reverse-engineering]]"]
---

# 60_dialogues/ — 对话记录模块

> 专门存放**用户与外部 AI（当前主要是 Knevo）的原始对话记录**，作为蒸馏语料库。
> 目标：从真实对话中提取输出模版、思考路径、工具调用链，反哺我们自己的 agent。

## 与其他目录的分工

| 目录 | 放什么 |
|---|---|
| `60_dialogues/` | **原始对话逐字记录**（长期保留，不会像 inbox 一样被清空） |
| `10_knowledge/knevo-reverse-engineering.md` | 从对话中**提炼出的结论**（架构/数据源/记忆/闭环） |
| `00_inbox/` | 其他 agent 的临时原始产出（会被清空，对话记录不要放这里） |

## 目录结构

```
60_dialogues/
├── README.md          # 本文件（模块约定）
├── _template.md       # 单次对话记录模板
├── INDEX.md           # 对话索引（每录一篇必须登记）
└── knevo/             # 按对方 AI 分子目录
    └── YYYY-MM-DD-主题短语.md
```

## 记录规范

1. **文件名**：`knevo/YYYY-MM-DD-主题短语.md`（日期=对话发生日，不是录入日）。
2. **逐字保留**：用户提问原文 + AI 回答原文（长回答可折叠为要点+关键段落引用，但输出骨架、工具调用行、来源标注必须原样保留）。
3. **工具调用链必录**：回答中出现的「思考了 X 秒」「显示其余 N 个工具调用」「Recommend Decision」、来源标注（datasvc/gangtise/ifind/web…）、sub-agent 派发提示，都是最高价值信息，逐条记录。
4. **每篇末尾写「蒸馏要点」**：本次对话暴露了什么模版/路径/工具行为；值得回写 `knevo-reverse-engineering.md` 的，标 `→ 待回写` 并注明目标章节。
5. **登记索引**：每录一篇，在 `INDEX.md` 加一行（日期/主题/场景标签/蒸馏状态）。
6. **场景标签**（对齐 Knevo 手册章节，用于聚合分析）：`复盘` `盘中监控` `盘感翻译` `猜你想问` `记忆库` `决策追踪` `事实核查` `情景推演` `推板块推票` `消息解读` `行为模拟` `资金推演` `压力测试` `价值迁移` `记忆召回` `行业报告` `建仓复盘` `探针`（主动测试边界的对话）。

## 蒸馏工作流

```
粘贴对话 → 按 _template.md 录入 knevo/ → 登记 INDEX.md
        → 提取蒸馏要点 → 回写 10_knowledge/knevo-reverse-engineering.md
        → （如产生可落地改进）在金融仓/知识库仓开任务
```

## 红线

- 不记录真实持仓规模、账户、身份信息（录入时脱敏）。
- 本目录是证据库：**只录不改**，原文段落不做二次加工；分析写在「蒸馏要点」或 10_knowledge。

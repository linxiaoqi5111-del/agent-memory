---
title: 维护纪律
type: convention
agent: devin
source: 设计约定
date: 2026-06-28
tags: [convention, maintenance, core]
---

# 维护纪律

底座的价值取决于**持续按规范回写**，而不是搭建本身。下面是必须遵守的最小纪律。

## 生命周期：inbox → knowledge

1. 任何 Agent 的原始产出（搜索结果、长篇分析、临时笔记）先落到 `00_inbox/`，`type: inbox`。
2. **定期回顾**（建议每周或每个项目节点）：把 inbox 里有长期价值的内容**提炼**成 `10_knowledge/` 的条目，标 `status: verified`。
3. 提炼后删除或归档 inbox 原件，保持 inbox 短小。

## Single Source of Truth

- 一个事实只在一个地方维护。其他地方用双链 `[[...]]` 指过去，不复制粘贴。
- 发现重复/冲突时，合并到一条，旧的标 `status: deprecated` 或删除。

## 写入检查清单（每次写笔记前过一遍）

- [ ] frontmatter 完整（title / type / agent / source / date / tags）
- [ ] 放进了正确的目录（type 与目录一致）
- [ ] 用了 `_templates/` 对应模板
- [ ] 引用其他笔记用双链而非复制
- [ ] 如果是结论/事实，标了 `status`
- [ ] 若改动会影响其他 Agent 行为（约定/偏好/agent 卡/playbook），已带 provenance 且经人工审阅（见 [[trust-boundary]]）

## 定期维护任务（可交给 Devin 定时自动化）

- 清理 `00_inbox/`：超过 N 天未提炼的条目，提醒或自动归档。
- 校验 frontmatter：扫描缺字段的笔记。
- 失效链接检查：双链指向不存在的笔记。

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

## 定期维护任务（已脚本化为 exit-code 门）

```bash
python3 scripts/vault_lint.py    # frontmatter 完整性 / type↔目录一致 / 死链 / inbox 老化(>14天 WARN)
python3 scripts/graph_audit.py   # 能力图谱节点清单路径防漂移（repo 在本地才校验）
```

- 回写沉淀前、改动 vault 后各跑一遍 `vault_lint.py`，exit 0 才算写入合规。
- 改能力图谱或相关仓有结构性合并后跑 `graph_audit.py`。

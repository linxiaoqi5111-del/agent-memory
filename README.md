# agent-memory

> 一个**可迁移的、跨 Agent 共享的"记忆底座"**。本质是一个 Obsidian vault（纯 Markdown 文件夹），用 Git 托管。

不论将来用 Devin / Codex / Grok / Claude 还是任何新工具，知识、约定、项目背景都沉淀在这里，**换工具只需重新"接线"，不用重建记忆**。

## 设计原则

1. **纯文本优先**：所有内容都是 Markdown + YAML frontmatter，无私有格式锁定。任何能读写文本的 Agent 都能用。
2. **格式统一**：不同 Agent 写入时必须遵守 [frontmatter 规范](30_conventions/frontmatter-spec.md) 和 [_templates](_templates/) 里的模板，否则内容无法被互相消费。
3. **过程 → 资产**：对话历史是流水账，会腐烂。底座只保留**提炼后的结论 / 规范 / 可复用工作流**。
4. **谁写都留痕**：每条记录的 frontmatter 必须标明 `agent`、`source`、`date`，可追溯。

## 目录结构

```
agent-memory/
├── 00_inbox/        # 各 Agent 产出的原始结果，待整理（短期）
├── 10_knowledge/    # 沉淀的事实 / 结论（长期资产）
├── 20_projects/     # 按项目组织：每个项目一个 MOC + 任务状态
├── 30_conventions/  # 跨 Agent 共享约定：规范、术语表、个人偏好
├── 40_playbooks/    # 可复用工作流（谁负责哪步、交接物格式）
├── 50_agents/       # 每个 Agent 的"接入约定卡"（贴进各自工具的指令里）
├── 60_dialogues/    # 用户与外部 AI（Knevo 等）的原始对话记录（蒸馏语料库，长期保留）
├── 70_tutor/        # 经用户检阅批准的科普 / 原理学习笔记（用户外脑）
└── _templates/      # 标准笔记模板（保证写入格式一致）
```

数字前缀用于在 Obsidian / 文件管理器里固定排序，从"短期/原始"到"长期/沉淀"。

## 工作流（黑板模型）

```
Grok 搜索  ─┐
            ├─►  00_inbox  ──(整理/提炼)──►  10_knowledge
Codex 规划 ─┤                                    │
            └─►  20_projects (方案/任务状态)  ◄───┘
                      │
                      ▼
                 Devin 执行（写代码 / 开 PR）──► 回写结论到 10_knowledge & 20_projects
```

底座是**共享数据层（黑板），不是调度器**。谁在什么时候读写，由你或上层编排决定。

## 快速开始

- **人类**：用 Obsidian 打开本仓库根目录即可（vault = 仓库根）。
- **Agent**：clone 本仓库 → 读 [`30_conventions/`](30_conventions/) 了解约定 → 按 [`50_agents/`](50_agents/) 里对应自己的卡片读写 → 用 [`_templates/`](_templates/) 的模板新建笔记。

## 维护纪律（成败关键）

底座最大的风险不是技术，是**维护习惯**。如果各 Agent 不按规范回写，它会退化成又一个乱糟糟的文件夹。

- 原始产出先进 `00_inbox/`，**定期**提炼进 `10_knowledge/` 并清空 inbox。
- 写入必须带完整 frontmatter（见规范）。
- 一条知识只有一个"事实来源"（single source of truth），避免重复。

详见 [`30_conventions/maintenance.md`](30_conventions/maintenance.md)。

---
title: Devin 回写沉淀 (任务完成 → 更新看板/交接记录)
type: playbook
agent: devin
source: 设计约定
date: 2026-06-28
tags: [playbook, workflow, devin, writeback, core]
status: verified
related: ["[[feature-lifecycle]]", "[[../50_agents/devin]]"]
---

# Devin 回写沉淀

每次 Devin 在某个项目仓库完成任务后，把"做了什么、关键决策、踩的坑"回写进本 vault，保证下一个 agent（哪怕是新开的一次性 Devin）能无缝接手。**这是 Devin 的核心职责，不是可选项。**

## 适用场景
在 `linxiaoqi5111-del` 的任意项目仓库（`finhot` / `finance-workspace-private` / `knowledge-base-private` / `finance-research-site` …）完成一次有产出的任务后（开了 PR、改了配置、跑通了流程、排查了问题）。

## 前置
- 用有写权限的 GitHub PAT 访问本 vault 仓库 `linxiaoqi5111-del/agent-memory`。
- 按 `30_conventions/frontmatter-spec.md` 写 frontmatter；双链用 `[[文件名]]`，不要裸路径。
- vault 约定**直接 commit 到 `main`**；Mac launchd 每 ~3 分钟双向同步到 Obsidian 库。

## 步骤
1. **定位项目笔记**：`20_projects/<repo>.md`（`<repo>` = 仓库短名）。不存在就用 `_templates/project.md` 新建。
2. **更新任务看板**：在「任务看板」表格里更新本次任务行，`状态` 用 `todo / doing / done / blocked`，PR 链接放「备注」列。
3. **追加交接记录**：在「交接记录」末尾加一行
   `YYYY-MM-DD · devin · 做了…（含 PR 链接 / 关键决策 / 坑）`
4. **提炼可复用知识**（仅当有跨任务复用价值时）：在 `10_knowledge/` 用 `_templates/knowledge-note.md` 建条目，`status: verified`，并从项目笔记双链过去。
5. **原始/临时产出**：长日志、未整理的中间结果放 `00_inbox/`，不要塞进项目 MOC。
6. **提交**：只改必要文件，commit message 形如
   `chore(memory): <repo> 回写 <一句话任务>`，push 到 `main`。

## 红线
- 不写任何密钥/token 到 vault（PAT、CC_REMOTE_EXEC_TOKEN 等一律不落库）。
- 不要把整段代码 diff 贴进笔记——记**结论和决策**，代码看 PR。
- 不删别的 agent 的交接记录；只追加，不覆盖历史。

## 失败/回退
- 任务未完成或被阻塞 → 看板标 `blocked` 并在交接记录写明原因和下一步，不要假装 done。
- 拿不到 vault 写权限 → 在本项目 PR 描述里写清回写内容，并提示人工补录，不要静默跳过。

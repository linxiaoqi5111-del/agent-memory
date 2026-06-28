---
title: Claude 接入约定卡
type: agent-card
agent: claude
source: 设计约定
date: 2026-06-28
tags: [agent-card, claude]
---

# Claude / Claude Code — 通用读写 (备用)

## 角色
通用助手；目前使用较少。可作为补充的读写节点（长文写作、代码审阅、整理提炼）。

## 读
- 可通过本地文件系统直接挂载本 vault 目录读写（Claude Code 尤其适合）。
- 读 `30_conventions/` 与目标 `20_projects/`。

## 写
- 遵守通用规则：frontmatter + 模板 + 正确目录。
- 适合承担"把 `00_inbox/` 提炼进 `10_knowledge/`"这类整理工作。

## 接入方式
- Claude Code：把本仓库目录作为工作区，直接读写文件。
- 网页端 / Project：把 `30_conventions/` 和相关笔记作为 Project 知识上传，回写时手动落库。

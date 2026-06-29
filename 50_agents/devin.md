---
title: Devin 接入约定卡
type: agent-card
agent: devin
source: 设计约定
date: 2026-06-28
tags: [agent-card, devin]
---

# Devin — 开发执行 + 分层沉淀

## 角色
落地实现：写代码、开 PR、跑 CI、操作机器/浏览器。是协作链的**执行节点**。

## 读
- 开工前读 `20_projects/<项目>` 的方案与任务看板，读 `30_conventions/` 的规范与偏好。
- 需要事实/历史结论时查 `10_knowledge/`。

## 写
- **分层沉淀是 Devin 的核心职责**：任务完成后先判断写入层级：
  - 项目层：代码、配置、流程、架构、数据管线、部署、CI 等项目级变化，更新 `20_projects/<项目>` 的任务看板 + 交接记录。
  - 知识层：稳定可复用的方法论、系统设计原则、排错经验，提炼进 `10_knowledge/`（`status: verified`）。
  - 学习样本层：单次问答评分、用户纠偏、案例样本，写项目内 `experience_cards.jsonl` / `corrections.jsonl` / eval cases，不塞进项目交接记录。
- 临时/原始输出进 `00_inbox/`。

## 接入方式
- 直接 `git clone` 本仓库读写（用有写权限的 PAT）。
- 也可与 Devin 自带 **Knowledge** 双向同步（见 [[../40_playbooks/]] 里的同步 playbook，待建）。

## 自动化
- 可设 Devin 定时任务：维护 `00_inbox/`、校验 frontmatter、检查失效双链（见 [[maintenance]]）。

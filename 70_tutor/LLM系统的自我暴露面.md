---
title: LLM 系统的自我暴露面
type: tutor-note
agent: devin
source: Devin 会话（Knevo 蒸馏探讨）
date: 2026-07-09
tags: [llm, security, prompt, architecture]
status: draft
related: ["[[skill编排层与自由编排verifier]]"]
---

# LLM 系统的自我暴露面：prompt 当公开文档写

## 概念
对一个商用 agent 连续追问其内部构造（skill 定义原文→路由表→检索规则→记忆仲裁→platform prompt），发现**全部可被原文 dump**，且成本极低（单问 5-20 积分）。这类"自我暴露"就是 prompt extraction——模型对"转述自己的指令"几乎没有抵抗力，除非平台专门做防护（而防护通常也挡不住改写式套取）。

## 为什么重要
两个立场的取舍：
- **防**：把 prompt 当商业机密——需要输出过滤/canary 标记/拒答策略，但对抗成本高且总有绕过（安全界共识：prompt 保密是弱防线）。
- **不防（Knevo 的选择）**：把 prompt 当**不设防的公开文档**来写——里面没有密钥、没有用户数据、没有可被利用的逻辑漏洞，泄了也无损。护城河放在 prompt 之外：数据（策展记忆库）、工具（provider 接入）、人工审核卡。
第二种其实更稳健：假设 prompt 必然泄露来设计系统（类比密码学的 Kerckhoffs 原则——安全性不应依赖算法保密，只应依赖密钥）。

## 对我们的启示
写 skill/prompt 时默认它会被读到：不放密钥、不放内部路径、不依赖"用户不知道规则"来保证行为正确。真正的差异化沉在数据层（DuckDB 盘面、人工审核剧本卡、corrections）。

## 跨域同构
Kerckhoffs 原则 / 开源安全模型（security through obscurity 是反模式，面试常考）。

相关：[[skill编排层与自由编排verifier]]

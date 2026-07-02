---
title: "Agent 系统第一性原理：从输入-处理-输出到精密闭环"
type: knowledge
agent: devin
source: "与用户关于输入/处理/输出三段式框架的讨论 + 对 agent-memory / knowledge-base-private / finance-workspace-private 的审阅"
date: 2026-07-02
tags: [system-design, agent, closed-loop, eval, memory, context-engineering, 第一性原理]
status: verified
related: ["[[finance-answer-orchestrator]]", "[[finance-answer-self-review-framework]]", "[[finance-narrative-answer-composer]]", "[[multi-agent-memory-system-design]]", "[[finance-agent-experience-cards]]"]
---

# Agent 系统第一性原理：从输入-处理-输出到精密闭环

## 结论 / 要点

1. **三段式（输入→处理→输出）是对的骨架，但只是前馈模型**。它能保证"流程走完"，不能保证"质量收敛"。缺两个一等公民：**评估/反馈** 和 **记忆/沉淀**。
2. 第一性原理：任何 LLM 系统都是一条**有损信息信道**（用户意图 → 上下文 → 模型 → 答案），每个节点的优化目标是提高信噪比、减少信息损失。
3. **优化的前提是可测量**。没有度量（answer-score、eval cases），对任何节点的调优都是盲调。评估必须和输入/处理/输出平级。
4. **输出不是终点**：最有价值的输出是会变成未来输入的部分（回写知识层、entity delta、经验卡片）。真实拓扑是环，不是线：

   ```
   输入 → 处理 → 质检 → 输出 → 评估 → 沉淀(记忆) ─┐
     ↑ ______________________________________________│
   ```

   单次会话是流水线，系统整体是闭环。
5. 控制论视角（可迁移到任何垂直 Agent）：**开环系统靠元件精度，闭环系统靠反馈**，后者对单个元件的误差不敏感。流程可控稳定的来源不是每个节点各自更好，而是环路收敛。

## 各节点的关键取舍

### 输入
- **ingest 结构化 = schema-on-write**，方向对，但要警惕源头过度结构化造成信息损失。对冲手段：`raw/` 不可变原文保留 schema-on-read 退路（知识库仓已实践）。
- **提示词措辞的杠杆很低且脆**；高杠杆的是结构化问题解析（QuestionPlan：规则先解析出任务类型 + 深度 + 视角 + 证据计划），把"让 LLM 猜意图"变成确定性编排。
- **context 工程本质是输入问题而非处理问题**：决定"给模型看什么"（检索质量）比"怎么跟模型说"（prompt 措辞）重要一个量级。

### 处理
- 两条正交的轴：
  1. **确定性轴**：能用规则的绝不用 LLM（路由、门控、字段校验），LLM 只留给必须的理解和表达——"规则编排 + LLM 生成"混合路线的本质是**用确定性组件压方差**。
  2. **质检独立成节点**：质检视角（影子用户反驳、审视者）与生成是对抗关系，混在生成里会退化成自我确认。

### 输出
- 分两类：**面向人的输出**（叙事编排，"rubric 防漏项，composer 防模板化"）和**面向系统的输出**（回写、沉淀、经验卡）。后者是闭环的回路，漏掉它系统就退化为开环。

### 评估 / 沉淀
- 事实库回答"世界发生了什么"，经验层回答"下次应该怎么想"，两者分开存放避免污染检索（见 [[finance-agent-experience-cards]]）。
- 最小闭环：回答 → 打分 → 低分/高价值样本存卡 → 下次合成时注入 → 多次验证后升级为稳定方法论。

## 背景 / 依据

- 用户提出：本质上一直在重复"输入、处理、输出"，提高每个节点的效率和质量即可让流程可控稳定。
- 审阅确认三个仓库已有对应实践：ingest 结构化（frontmatter + relations JSON）、QuestionPlan 编排层、L3 证据运行时补查、影子用户反驳质检、narrative composer、experience cards——但"评估驱动沉淀、沉淀改善输入"的闭环尚未被提到节点高度、也未完全自动化。

## 参考

- [[finance-answer-orchestrator]] — 问题解析 → 证据计划
- [[finance-answer-self-review-framework]] — 质检器与影子反驳
- [[finance-narrative-answer-composer]] — rubric 防漏项、composer 防模板化
- [[finance-agent-experience-cards]] — 经验层与事实层分离
- [[multi-agent-memory-system-design]] — 记忆底座整体设计

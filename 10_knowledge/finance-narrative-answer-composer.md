---
title: 金融 Agent 叙事回答编排器
type: knowledge
agent: codex
source: finance-workspace-private narrative answer composer implementation
date: 2026-07-01
tags: [金融Agent, 问答质量, 第一性原理, prompt, composer]
status: verified
related: ["[[finance-answer-orchestrator]]", "[[finance-answer-self-review-framework]]"]
---

# 金融 Agent 叙事回答编排器

## 核心原则

模板能防止漏项，但不能保证回答有判断力。成熟金融问答应该让“视角清单”只做内部自检，最终回答围绕核心矛盾展开。

内部先问三句话：

1. 这家公司真实业务是什么？
2. 市场正在交易什么预期？
3. 最大证据缺口或反证是什么？

然后所有视角都必须服务这条核心矛盾：公司本体、收入结构、客户证据、盘面、生命周期、二阶导和反证，不是小标题，也不是填空格。

## 写作要求

每段都要回答“这个事实改变了什么判断”：

- 改变了对上涨空间的判断；
- 改变了对逻辑生命周期的判断；
- 改变了对资金选择的判断；
- 改变了对证据硬度或更优表达的判断。

最终回答要解释资金为什么选择、放弃或犹豫，而不是只说明公司有什么故事。

## 技术落地

`finance-workspace-private` 已在 `llm_refine` 和 `answer_quality` 增加叙事编排约束：

- `compose` 系统提示要求先内部写核心矛盾句。
- 所有视角必须服务核心矛盾。
- 禁止按公司本体、盘面、二阶导、反证逐项填空。
- 二次反驳提示检查是否仍然模板化。

## 可迁移性

这是垂直 Agent 的通用模式：**rubric 防漏项，composer 防模板化**。法律、医疗、代码审查、产业研究都可以复用：先用 checklist 确保覆盖，再用核心问题组织叙事。

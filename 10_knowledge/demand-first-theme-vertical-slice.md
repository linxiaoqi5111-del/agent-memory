---
title: Demand-first 主题纵切片
type: knowledge
agent: devin
source: https://github.com/linxiaoqi5111-del/knowledge-base-private/pull/256
date: 2026-07-10
tags: [knowledge-graph, rag, ontology, prioritization, data-contract]
status: verified
related: ["[[knowledge-base-private]]", "[[finance-agent-capability-graph]]"]
---

# Demand-first 主题纵切片

## 结论 / 要点

- **先按需求选范围，再按缺口排动作**：真实查询、近期/历史提及、来源覆盖和实体覆盖决定 Top N；定义、ontology、产业链、证据、链接和评测只决定选中主题的完成路径。
- 终态显式分为 `ready / build / review`：已闭环的维护、canonical node 未闭环的执行确定动作、无法 canonicalize 的信号人工裁决。`review` 不得自动建节点或关系。
- Graph RAG（基于图关系扩展的检索增强生成）前置条件不是“节点越多越好”，而是高价值节点具备 canonical identity、typed relation、可回溯 evidence 和真实 eval query。
- 机器 JSON 保存输入快照、分数、gate 和决策原因；Markdown 只作为人工执行视图。这样能重跑、比较和审计，不依赖一次性 LLM 判断。

## 为什么不选另外两种方案

1. **全库平均清债**：覆盖面完整，但 2,000+ 节点会把时间耗在低价值长尾上，无法快速验证检索收益。
2. **按缺口总量直接排序**：实现简单，却会让空白冷门节点因“什么都缺”获得最高优先级，形成反向激励。
3. **高频词自动建 concept**：吞吐最快，但报告标题、实体名、泛层级词和同义词会污染 ontology，后续 Graph RAG 的一跳扩展会放大噪音。

## 可复用模式

这个模式可迁移到产品知识图谱、客服知识库、代码文档和实体画像：

```text
observed demand
  -> canonical resolution
  -> Top-N selection
  -> completeness gates
  -> ready | build | review
  -> auditable receipt
```

系统设计面试里可把它描述为“需求驱动的增量物化”：不用先把全量数据做到完美，而是对高价值子图建立可验证闭环，同时保留 review queue 控制 ontology 扩张。

## 执行层补充

- **批次范围应冻结在 task-plan 快照**：补 eval query 会提高主题的重要度并实时重排队列；执行中仍按已确认的批次收尾，重建后的新 P0 留给下一批，避免 scope creep。
- **知识标识不是文件扩展名**：`800G_1.6T光模块` 这类 canonical name 含小数点，不能用通用 `Path.stem` 处理；只应精确移除结尾 `.md`。这个原则也适用于模型名、版本号、产品 SKU 等带点号的业务 ID。

## 参考

- [[knowledge-base-private]]
- https://github.com/linxiaoqi5111-del/knowledge-base-private/pull/256
- https://github.com/linxiaoqi5111-del/knowledge-base-private/pull/258

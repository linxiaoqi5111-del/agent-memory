# 70_tutor — 个人技术学习笔记（用户外脑）

> 定位：Devin 对话中的科普/原理讲解沉淀——**这是用户的学习资产，不是 agent 的运行知识**。
> 与 10_knowledge 的区别：10_knowledge 是 agent 干活要复用的方法；这里是帮用户理解设计原理、可跨领域迁移的概念。
> 归档纪律：每篇一个概念，含「概念 / 为什么 / 本轮实现对照 / 边界与反例 / 跨领域同构 / 关联」，frontmatter 标 source 会话。

## 落库流程

使用 `tutor` skill（手动触发：`@tutor` 或 `@session-tutor`；自然语言“session tutor”也可）：

1. 先围绕一个核心概念讲解、举例并检查用户是否理解，不写文件；
2. 用户确认理解后，才整理少量落库候选；
3. “理解了”不等于批准；用户明确批准具体候选后，才按 `_templates/tutor-note.md` 落库；
4. 写入后更新本索引并运行 `python3 scripts/vault_lint.py`。

## 目录
- [[GraphRAG与我们的低配实现]]
- [[LLM系统的自我暴露面]]
- [[preset权限分层与最小权限]]
- [[skill编排层与自由编排verifier]]
- [[单入口派单与平铺skill路由]]
- [[检索前置硬触发]]
- [[结论TTL与delta-only跟踪契约]]
- [[记忆prior化与贝叶斯仲裁]]
- [[长尾分布与头尾分治]]
- [[头尾分治优化工程]]

# preset 权限分层：最小权限原则在 agent 派单的应用

## 概念
派发子 agent 时不只是选 skill，还按任务性质授予**工具权限集（preset）**：如 researcher（检索+输出）、producer（检索+写文件）、reviewer（检索+审查，无写权限）。审查型任务天然拿不到写文件的能力。

## 为什么
LLM agent 的工具就是它的"系统调用"。任务用不到的能力就不该给——权限越小，幻觉/注入攻击能造成的实际伤害越小。这是安全领域**最小权限原则（principle of least privilege）**在 agent 编排里的直接移植。

## 实现对照
- Knevo：`spawn_sub_agent(preset=finance-reviewer, ...)`，路由表同时决定 skill 和 preset（q7）。
- 我们：workbench/ask 所有路径同权限，无副作用分级——回灌候选：只读分析与写库任务分开授权。

## 跨域同构
IAM role / 数据库只读账号 / 容器 capability 裁剪 / OAuth scope。面试常考：为什么服务间调用要用 scoped token 而不是万能 key。

相关：[[单入口派单与平铺skill路由]]

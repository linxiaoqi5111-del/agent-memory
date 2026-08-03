---
title: 串行阶段预算：初始总额、尾段预留与前段回吐
type: knowledge
agent: codex
source: finance-workspace-private Grounded A4 M2 (2026-08-03)
date: 2026-08-03
tags: [agent-runtime, timeout, budget, orchestration]
status: verified
related: ["[[finance-workspace-private]]"]
---

# 串行阶段预算：初始总额、尾段预留与前段回吐

## 结论 / 要点

- 串行阶段若反复按“当时剩余 × 固定比例”取预算，结构上永远用不完初始总额：使用率为 `1 - ∏(1 - share_i)`，越靠后的验证阶段越容易被饿死。
- 更稳的做法是启动时冻结初始总额 `T`：给前段设 cap、给最后一道验证闸保留固定 reserve；前段提前结束时，未用时间留在共享 deadline 中，自动回吐给后续阶段。
- grant（授予时间）必须在真正发网络/工具请求的 enforcement point 被读取，并同时记录 `remaining_at_entry / grant / elapsed / result`。只把字段层层传下去，不能证明限制真的生效。
- 回收结构性闲置只证明“预算变得可达”，不证明实际工作量装得下。判断证据是否缺失前，必须扫描相邻历史 artifact 与代码中的实测注释；不能因为当前 A/B 没跑到后段，就忽略旧 run 已留下的自然完成值或截断下界。
- 同名 telemetry 字段可能因 runtime 修复而变义：本案至少有 E0（grant未执行）、E1（每次retry各拿一片）、E2（整段共享硬截止）三态。跨 revision 聚合前必须先建立 semantic epoch；字段名相同不代表统计口径相同。

## 背景 / 依据

- Grounded 三段链原先以 `0.25 / 0.50 / 0.35` 依次乘当时剩余，并被 90 秒 child cap 再收窄；修复后 child 可见 115 秒且 tail reserve/carry-forward 在运行时生效。
- 同一 A4 的修复前后结构化输入完全一致；brief grant 从 22 秒增至 28 秒后仍精确本地超时，而 120 秒 root 尚余约 90.7 秒。这个结果同时证明 allocator 生效，也证明“修复分配即可完成三段”的性能推演不能替代实测。
- 扫描全部 phase artifact 后发现已有同形状 A1 brief `ok 69.740s` 与 composer `>20.261s` 下界。在 `T=115s`、judge reserve=28.75s 时，给足 brief 后 composer 仅约16.5s，低于观测下界；allocator 只能移动失败点，不能解决总工作量与预算不相容。
- 该模式可迁移到多阶段 LLM、ETL、重试退避、限流令牌和“生成 → 校验 → 发布”流水线；最后一道安全/质量闸尤其不应只拿递归后的残余。

## 技术选型对比

- **初始总额 + 尾段预留 + 回吐**：规则简单、可纯函数测试，不依赖 token/s；缺点是前段 cap 仍需用实测校准。
- **删除一次串行往返（确定性中间表示）**：当总工作量已超过产品预算时，比继续切片更有效；代价是必须明确哪些字段可投影、哪些仍需生成，并用 validator 守住表达契约。
- **扩大 root/deep mode**：保留全部 LLM 自由度，但会改变用户等待、成本与验收 SLA；应作为显式产品 profile，而不是静默调大全局 timeout。
- **固定绝对秒数**：最直观，但模型、题型或 provider 变化后容易失真，适合短期受控实验，不宜直接固化。
- **token/吞吐自适应**：理论效率更高，但要求可靠的 phase 级 usage 与延迟分布；缺数据时会把估算误差引入调度器。
- **尾段异步化**：可缩短用户等待，但会改变 fail-closed 与发布语义；验证闸是安全边界时不能只为性能默认后置。

## 参考

- `finance-workspace-private/docs/superpowers/specs/2026-08-03-grounded-chain-budget-allocation-design.md`
- `finance-workspace-private/docs/verification/2026-08-03-a4-grounded-budget-m2-triage.md`

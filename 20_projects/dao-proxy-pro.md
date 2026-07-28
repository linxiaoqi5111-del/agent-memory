---
title: dao-proxy-pro · 多渠道 LLM 路由代理
type: project
agent: devin
source: https://github.com/linxiaoqi5111-del/dao-proxy-pro (源码分析 + 实机部署验证)
date: 2026-07-28
tags: [project, dao-proxy, llm, gateway, routing, cache]
status: active
---

# dao-proxy-pro — 项目 MOC

## 概述
- **是什么**：Devin Desktop（Windsurf 系）的 BYOK 代理扩展，本质是一个**本地 LLM 网关**：拦截 IDE 的模型请求，按路由规则分发到任意第三方渠道（GLM/DeepSeek/MiMo/Anthropic 中转等），做协议转换、故障转移与推理侧优化。
- **形态**：VS Code 扩展（`dao-agi.dao-proxy-pro`）+ 独立 Node 核心（`vendor/外接api/core/`），本地 HTTP 服务 `127.0.0.1:8955`。
- **仓库**：`linxiaoqi5111-del/dao-proxy-pro`（分支 `main`）。
- **部署实例**：a77 Mac（配置 `/Users/a77/.codeium/dao-byok/配置.json`）。

## 架构亮点（面试可讲）
1. **多协议适配层**（adapters.js）：OpenAI-chat / Anthropic messages / Responses 等协议互转，同一路由可混配不同协议渠道。
2. **分层路由 + 故障转移**（dao_router.js）：按模型档位（fast/slow/opus）分发不同渠道；上游熔断（circuit breaker）、autoFallback 备选链、健康检查、透明重试（如 prompt_cache_key 不支持时自动降级重发）。
3. **Prompt 缓存全链路优化**：
   - Anthropic cache_control 三处断点自动钉（system / 工具定义末尾 / 末消息），beta 头（prompt-caching、context-1m）自动合并；
   - OpenAI 系自动带会话级 prompt_cache_key；
   - 缓存命中/写入 token 全量记账，面板可看 hitRate。
4. **streamMode:auto 自动探测**（2026-07 新增）：部分中转（如 kfcoding）只对非流式请求启用 prompt caching。代理对配 `auto` 的渠道自动实测流式/非流式哪种能产生缓存 usage，选最优并缓存决策 24h，启动预热探测、失败重探。实测把 kfcoding 单轮从 60-90s 降到 13-58s，缓存命中率 0→71%，单轮全价输入 3 万→约 400 token。
5. **会话渠道粘性**：会话级 affinity（2h TTL）保证同一会话粘住同一渠道/模型，避免 fallback 来回切换导致上游 KV cache 反复失效；渠道熔断/失效时自动解除。连接层也按会话分 keep-alive agent。
6. **上下文管理**：tool-output-store（大工具输出存储引用，历史轮只留摘要）+ context-strategy 水位裁剪/checkpoint 复用 + token 预算管理。
7. **可观测性**：/origin/ea/usage（分渠道 token/缓存/命中率）、traces、alerts、渠道额度查询（new-api 系 billing 接口）、诊断日志。
8. **热重载**：dao_router.js mtime 变化自动清 require.cache 重载，配置 /origin/ea/reload 热生效，无需重启 IDE。

## 关键决策
- kfcoding 渠道用 `streamMode: "auto"`（探测结果 unary），因其流式请求忽略 cache_control。
- opus 路由主渠道 kfcoding，备选 anyrouter.top（Anthropic 协议 + context-1m beta 头），末位 fable-relay（当前欠费不可用）。
- 缓存 TTL 是上游机制（Anthropic 系 5 分钟，命中续期），代理层无法延长；隔天任务第一轮必然重建缓存。

## 可能的演进方向
- **换壳做通用网关**（类 claude-code-router / cc-switch）：核心已协议无关，补一个入站 Anthropic /v1/messages 端点 + 剥离扩展宿主依赖做成独立 CLI，即可给 Claude Code 等任意前端用（`ANTHROPIC_BASE_URL=http://127.0.0.1:8955`），多渠道 fallback/缓存优化/额度面板全部复用。
- 历史滚动 AI 摘要（当前是裁剪式压缩）。

## 交接记录
- 2026-07-28 · devin · 诊断路由失败（mimo key 失效、opus 渠道 baseUrl/key 不匹配）；opus 切 anyrouter.top；注册 kfcoding/fable-relay；加渠道额度显示；定位 kfcoding 流式无缓存 → 切非流式实测提速；实现 streamMode:auto + 启动预热探测；确认会话粘性已内置。PR: https://github.com/linxiaoqi5111-del/dao-proxy-pro/pull/6

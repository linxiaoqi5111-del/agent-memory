---
title: Claude Code Hooks (自动读 + 准自动回写)
type: agent-card
agent: claude
source: 设计约定 (2026-06-28)
date: 2026-06-28
tags: [agent-card, claude, hooks, automation, core]
related: ["[[claude]]", "[[onboarding]]", "[[../40_playbooks/devin-writeback]]", "[[../30_conventions/preferences]]"]
status: verified
---

# Claude Code Hooks —— 记忆底座的自动读 + 准自动回写

给 4 个项目仓（finhot / finance-workspace-private / knowledge-base-private / finance-research-site）的 `.claude/` 装了两个 hook，让 Claude Code 开窗自动加载记忆、结束前自动补回写。**项目级配置，需在 repo 目录里启动 Claude（`cd /Users/a77/<repo> && claude`），首次会弹安全确认批准。**

## 文件位置（每个 repo 内）
- `.claude/settings.json` —— 注册 hook（项目级，提交进仓库）。
- `.claude/hooks/load-memory.sh` —— SessionStart：注入偏好 + 项目笔记。
- `.claude/hooks/check-writeback.sh` —— Stop：回写门禁。

## ① SessionStart hook —— 开窗自动读
- 触发：`startup|resume|clear|compact`。
- 动作：从 repo 内软链 `.agent-memory`（回退 `/Users/a77/agent-memory`）读出
  `30_conventions/preferences.md` + 本项目 `20_projects/<repo>.md`，stdout 自动注入上下文。
- 价值：比静态 `CLAUDE.md` 更实时（每次开窗读最新看板），且不依赖模型主动开文件。

## ② Stop hook —— 结束前准自动回写（门禁）
- 触发：Claude 想结束回合时。
- 逻辑：
  1. `stop_hook_active=true`（hook 触发的二次结束）→ 放行，防死循环。
  2. repo **无改动**（工作树干净且本地不领先上游）→ 放行，不打扰纯问答。
  3. `20_projects/<repo>.md` **最近 10 分钟被改过** → 视为已回写，放行。
  4. 否则 → 返回 `{"decision":"block","reason":...}` **拦截**，提示按
     `40_playbooks/devin-writeback.md` 把结论回写到 `20_projects/<repo>.md` 再结束。
- 即：有实质改动却没沉淀时，Claude 会被拽回去自己补回写，不用人喊。

## 各 agent 加载机制全景
| Agent | 自动读偏好 | 回写 |
|---|---|---|
| Codex | 读 `AGENTS.md`（内联核心偏好） | 软指令（playbook 指向） |
| Claude Code | `CLAUDE.md` + SessionStart hook（双保险） | **Stop hook 门禁（准自动）** |
| Grok | Custom Instructions（见 [[grok]]，一次性设置常驻） | 人工落 `00_inbox/` |
| Devin | 开场白读 `AGENTS.md`（+ rx.py/PAT 读 vault） | 按 [[../40_playbooks/devin-writeback]] |

## 注意 / 维护
- 与 kb 仓的 **planning-with-files** 技能并存：那套 Stop hook（`gate-stop.sh`）管「计划任务做完没」，本门禁管「结论回写没」，职责不同、已合并共存。
- hook 是项目级：在 home 目录（`/Users/a77`）启动 Claude 不会触发；务必进 repo 目录。
- 改 hook 后 Claude Code 需重新批准（`/hooks` 查看）。
- 脚本以 `set -u`、`exit 0` 兜底，vault 不可达（如在别的机器）时静默跳过，不打断 agent。

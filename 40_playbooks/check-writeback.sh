#!/bin/sh
# Shared Stop hook for agent-memory writeback.
# It gates only project-level work. Fine-grained answer feedback should go to a
# project learning layer such as experience_cards.jsonl / corrections.jsonl.
set -u

input="$(cat 2>/dev/null || true)"
case "$input" in *'"stop_hook_active":true'*) exit 0 ;; esac

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
repo="$(basename "$repo_root")"

V="$repo_root/.agent-memory"
[ -d "$V" ] || V="/Users/a77/agent-memory"
[ -d "$V" ] || exit 0

note="$V/20_projects/$repo.md"
stamp_dir="$repo_root/.git/agent-memory"
stamp="$stamp_dir/writeback-ok"

state_key() {
  {
    git -C "$repo_root" rev-parse HEAD 2>/dev/null || true
    git -C "$repo_root" status --porcelain=v1 2>/dev/null || true
    git -C "$repo_root" diff --name-only '@{u}..HEAD' 2>/dev/null || true
  } | cksum | awk '{print $1 ":" $2}'
}

dirty="$(git -C "$repo_root" status --porcelain 2>/dev/null)"
ahead="$(git -C "$repo_root" rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)"
if [ -z "$dirty" ] && [ "${ahead:-0}" = "0" ]; then
  exit 0
fi

state="$(state_key)"
if [ -f "$stamp" ] && [ "$(cat "$stamp" 2>/dev/null || true)" = "$state" ]; then
  exit 0
fi

# Project note recently updated: treat as project-level writeback done.
if [ -f "$note" ] && [ -n "$(find "$note" -mmin -10 2>/dev/null)" ]; then
  exit 0
fi

changed="$( { git -C "$repo_root" status --porcelain 2>/dev/null | sed 's/^...//; s/^.* -> //'; \
             git -C "$repo_root" diff --name-only '@{u}..HEAD' 2>/dev/null; } | sort -u )"
if [ -n "$changed" ]; then
  data_re='(^|/)data/|\.(parquet|duckdb|db|sqlite|csv|tsv|jsonl|ndjson|arrow|feather|xlsx|h5|pkl)$'
  non_data="$(printf '%s\n' "$changed" | grep -Ev "$data_re" || true)"
  if [ -z "$non_data" ]; then
    exit 0
  fi
fi

ack_cmd="mkdir -p .git/agent-memory && { git rev-parse HEAD 2>/dev/null || true; git status --porcelain=v1 2>/dev/null || true; git diff --name-only '@{u}..HEAD' 2>/dev/null || true; } | cksum | awk '{print \$1 \":\" \$2}' > .git/agent-memory/writeback-ok"

reason="本次在 $repo 有代码/配置级改动但还没完成记忆分层处理。请先判断沉淀层级：1) 项目级代码、配置、流程、架构、数据管线决策 → 按 .agent-memory/40_playbooks/devin-writeback.md 追加到 .agent-memory/20_projects/$repo.md 的「交接记录」；2) 稳定且可跨任务复用的方法论 → 提炼进 .agent-memory/10_knowledge/；3) 单次问答评分、用户纠偏、经验样本 → 写入项目内学习层（如 experience_cards.jsonl / corrections.jsonl），不要塞进项目交接记录。若本次已写入学习层或确认无需项目级 agent-memory 回写，请在 repo 根目录运行：$ack_cmd"
printf '{"decision":"block","reason":%s}\n' "$(printf '%s' "$reason" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')"
exit 0

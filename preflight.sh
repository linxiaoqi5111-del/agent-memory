#!/usr/bin/env bash
# 开工 preflight：一次性打包「读 memory + git 现状 + 红线提醒」。
# 用法（在任一 repo 目录下，经软链调用）：  bash .agent-memory/preflight.sh
# 它会自动识别当前 repo，从 vault 读偏好与本项目笔记。
set -u

# vault 根 = 本脚本所在目录（经 .agent-memory 软链时会解析到真实 vault 路径）
V="$(cd "$(dirname "$0")" 2>/dev/null && pwd)"
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
# repo 名优先取 git remote（权威，文件夹改名也不受影响），取不到再用文件夹名兜底
remote="$(git -C "$repo_root" remote get-url origin 2>/dev/null || true)"
if [ -n "${remote:-}" ]; then repo="$(basename "${remote%.git}")"; else repo="$(basename "$repo_root")"; fi

echo "==================== 开工 PREFLIGHT ===================="
echo "项目：$repo"
echo "目录：$repo_root"
echo
echo "----- ① Git 现状（你的 Git 约定第一步）-----"
br="$(git -C "$repo_root" branch --show-current 2>/dev/null)"
[ -n "$br" ] && echo "当前分支：$br" || echo "(非 git 仓库或游离 HEAD)"
st="$(git -C "$repo_root" status --short 2>/dev/null)"
if [ -n "$st" ]; then echo "$st"; else echo "(工作树干净)"; fi
echo
echo "----- ② 红线提醒（硬拦截由 pre-commit 兜底）-----"
echo "🚫 禁提交：.env* / 密钥 / *.pdf|zip|duckdb|db / .DS_Store / 缓存或虚拟环境；不写明文密钥。"
echo "📌 Git：大任务先开分支（<type>/<task>）；合并 main 必须等确认，不强推。"
echo "完整偏好：.agent-memory/30_conventions/preferences.md ｜ 分工：.agent-memory/30_conventions/agent-division.md"
echo
echo "----- ③ 本项目笔记摘要（$repo）-----"
note="$V/20_projects/$repo.md"
if [ -f "$note" ]; then
  sed -n '1,40p' "$note"
  echo "...（完整见 .agent-memory/20_projects/$repo.md）"
else
  echo "(暂无 $repo.md，可用 _templates/project.md 新建)"
fi
echo
echo "----- ④ 完工提醒 -----"
echo "按 .agent-memory/40_playbooks/devin-writeback.md 把结论回写到 20_projects/$repo.md。"
echo "========================================================"

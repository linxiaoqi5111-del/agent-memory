#!/usr/bin/env python3
"""能力图谱防漂移审计（finance-agent-capability-graph 的 exit-code 门）。

问题：能力图谱是手工维护的 mermaid + 节点清单，「维护口径」只是散文约定，
没有任何机械校验——节点路径改名/删除后图谱不会报警，久了就变成过期地图。

本脚本把「节点清单表」当作机器可读的事实源，逐行校验：

1. 解析 `10_knowledge/finance-agent-capability-graph.md` 的节点清单 markdown 表；
2. 把「所在仓库」映射到本地 repo 目录（默认在 vault 的同级目录找）；
3. repo 在本地存在时，校验「主要路径」里的每个路径是否真实存在；
4. repo 不在本地 → SKIP（不算失败），路径缺失 → STALE。

用法::

    python3 scripts/graph_audit.py                       # repos 根默认 = vault 上一级
    python3 scripts/graph_audit.py --repos-root ~/repos

退出码 0 = 无漂移，1 = 有 STALE 节点（图谱需要更新），2 = 用法/解析错误。
只读脚本。建议：每次改图谱、以及金融/知识库仓的结构性 PR 合并后跑一遍。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]
GRAPH_NOTE = VAULT / "10_knowledge" / "finance-agent-capability-graph.md"

REPO_ALIASES = {
    "finance": "finance-workspace-private",
    "knowledge": "knowledge-base-private",
    "agent-memory": "agent-memory",
    "finhot": "finhot",
}
PATH_RE = re.compile(r"`([^`]+)`")


def parse_node_table(text: str) -> list[tuple[str, str, list[str]]]:
    """从「## 节点清单」章节解析 (节点, 仓库, [路径])。"""
    m = re.search(r"## 节点清单\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
    if not m:
        return []
    rows: list[tuple[str, str, list[str]]] = []
    for line in m.group(1).splitlines():
        if not line.startswith("|") or set(line.replace("|", "").strip()) <= {"-", " "}:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("节点", ""):
            continue
        node, repo, path_cell = cells[0], cells[1], cells[2]
        paths = PATH_RE.findall(path_cell)
        rows.append((node, repo, paths))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="能力图谱防漂移审计")
    parser.add_argument("--repos-root", default=str(VAULT.parent), help="各 repo 的父目录")
    args = parser.parse_args()

    if not GRAPH_NOTE.is_file():
        print(f"用法错误：图谱笔记不存在 {GRAPH_NOTE}", file=sys.stderr)
        return 2
    rows = parse_node_table(GRAPH_NOTE.read_text(encoding="utf-8", errors="replace"))
    if not rows:
        print("用法错误：未解析到「## 节点清单」表", file=sys.stderr)
        return 2

    repos_root = Path(args.repos_root).expanduser()
    stale: list[str] = []
    skipped = checked = 0

    for node, repo_alias, paths in rows:
        repo_name = REPO_ALIASES.get(repo_alias, repo_alias)
        repo_dir = VAULT if repo_name == "agent-memory" else repos_root / repo_name
        if not repo_dir.is_dir():
            skipped += 1
            continue
        for p in paths:
            checked += 1
            if not (repo_dir / p).exists():
                stale.append(f"{node} → {repo_name}/{p} 不存在")

    for s in stale:
        print(f"STALE {s}")
    if stale:
        print(f"\nFAIL: {len(stale)} 个节点路径漂移（图谱需要更新或节点已迁移），已检 {checked} 条。")
        return 1
    print(f"OK: 节点清单 {len(rows)} 行、路径 {checked} 条无漂移（{skipped} 行因 repo 不在本地跳过）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

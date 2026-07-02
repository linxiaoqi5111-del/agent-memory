#!/usr/bin/env python3
"""agent-memory vault 质检门（把 maintenance.md 的「定期维护任务」硬化成 exit-code 门）。

检查项（对应 30_conventions/maintenance.md 写入检查清单）：

1. frontmatter 完整性：title / type / agent / source / date / tags 必填；
2. type ↔ 目录一致（frontmatter-spec 的 type 取值表）；
3. date 格式 YYYY-MM-DD；
4. 双链死链：`[[笔记名]]` 必须能解析到 vault 内某个 .md 文件名；
5. inbox 老化：`00_inbox/` 中超过 14 天未提炼的条目（仅 WARN，不拦截）；
6. 知识过期：`10_knowledge/` 中 `status: verified` 的笔记，若 `last_verified`
   （缺省回退到 `date`）超过 `stale_after` 天（缺省 90）未复核，降为 WARN，
   提醒复核后刷新 `last_verified` 或把 status 改回 draft。

用法::

    python3 scripts/vault_lint.py            # 校验整个 vault
    python3 scripts/vault_lint.py --strict   # WARN 也算失败

退出码 0 = 通过，1 = 有 ERROR（--strict 时含 WARN），2 = 用法错误。
只读脚本。建议：改动 vault 后、以及每次回写沉淀前跑一遍。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

VAULT = Path(__file__).resolve().parents[1]

REQUIRED_FIELDS = ("title", "type", "agent", "source", "date", "tags")
TYPE_DIRS = {
    "inbox": "00_inbox",
    "knowledge": "10_knowledge",
    "project": "20_projects",
    "convention": "30_conventions",
    "playbook": "40_playbooks",
    "agent-card": "50_agents",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
INBOX_MAX_AGE_DAYS = 14
KNOWLEDGE_STALE_DAYS = 90
# 不做 frontmatter 校验的路径（模板本身是占位符；README/欢迎页是导览）。
SKIP_FRONTMATTER = {"_templates", "README.md", "欢迎.md"}


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    return fm


def should_skip(path: Path) -> bool:
    rel = path.relative_to(VAULT)
    return rel.parts[0] in SKIP_FRONTMATTER or rel.name in SKIP_FRONTMATTER


def main() -> int:
    parser = argparse.ArgumentParser(description="agent-memory vault 质检门")
    parser.add_argument("--strict", action="store_true", help="WARN 也算失败")
    args = parser.parse_args()

    md_files = [p for p in VAULT.rglob("*.md") if ".git" not in p.parts]
    basenames = {p.stem for p in md_files}
    errors: list[str] = []
    warns: list[str] = []
    today = dt.date.today()

    for path in md_files:
        rel = path.relative_to(VAULT)
        if should_skip(path):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")

        # 双链死链（跳过代码块/行内代码里的示例链）
        prose = CODE_RE.sub("", text)
        for link in WIKILINK_RE.findall(prose):
            target = link.strip().rstrip("\\").split("/")[-1]
            if target.endswith(".md"):
                target = target[:-3]
            if target and target not in basenames:
                errors.append(f"{rel}: 死链 [[{link.strip()}]]")

        fm = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel}: 缺少 frontmatter")
            continue

        for field in REQUIRED_FIELDS:
            if not fm.get(field):
                errors.append(f"{rel}: frontmatter 缺字段 {field}")

        date_val = fm.get("date", "")
        if date_val and not DATE_RE.match(date_val.strip('"')):
            errors.append(f"{rel}: date 格式应为 YYYY-MM-DD，实际 {date_val}")

        last_verified = fm.get("last_verified", "").strip('"')
        if last_verified and not DATE_RE.match(last_verified):
            errors.append(f"{rel}: last_verified 格式应为 YYYY-MM-DD，实际 {last_verified}")
        stale_after = fm.get("stale_after", "").strip('"')
        if stale_after and not stale_after.isdigit():
            errors.append(f"{rel}: stale_after 应为天数整数，实际 {stale_after}")

        note_type = fm.get("type", "")
        expected_dir = TYPE_DIRS.get(note_type)
        if expected_dir and rel.parts[0] != expected_dir:
            errors.append(f"{rel}: type={note_type} 应放在 {expected_dir}/")

        # 知识过期：verified 笔记超过 stale_after 天未复核
        if rel.parts[0] == "10_knowledge" and fm.get("status") == "verified":
            anchor = last_verified if DATE_RE.match(last_verified) else date_val.strip('"')
            max_age = int(stale_after) if stale_after.isdigit() else KNOWLEDGE_STALE_DAYS
            if DATE_RE.match(anchor):
                age = (today - dt.date.fromisoformat(anchor)).days
                if age > max_age:
                    warns.append(
                        f"{rel}: verified 笔记已 {age} 天未复核（>{max_age} 天），"
                        "复核后刷新 last_verified 或降回 draft"
                    )

        # inbox 老化
        if rel.parts[0] == "00_inbox" and DATE_RE.match(date_val.strip('"')):
            age = (today - dt.date.fromisoformat(date_val.strip('"'))).days
            if age > INBOX_MAX_AGE_DAYS:
                warns.append(f"{rel}: inbox 条目已 {age} 天未提炼（>{INBOX_MAX_AGE_DAYS} 天）")

    for w in warns:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    failed = bool(errors) or (args.strict and bool(warns))
    if failed:
        print(f"\nFAIL: {len(errors)} error(s), {len(warns)} warn(s)")
        return 1
    print(f"OK: {len(md_files)} 个文件通过（{len(warns)} warn）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

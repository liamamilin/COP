#!/usr/bin/env python3
"""Install the canonical p-discovery skill for agent harnesses.

The repo carries ONE canonical .agents/skills/p-discovery. Codex and OpenCode
read it there. Claude Code also reads .claude/skills, so copy the same skill to
that directory when requested. No dependency beyond Python stdlib.

Examples from repository root:
    python3 scripts/install_p_discovery_skill.py --host claude --scope project
    python3 scripts/install_p_discovery_skill.py --host codex --scope user
    python3 scripts/install_p_discovery_skill.py --host all --scope user
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / ".agents" / "skills" / "p-discovery"
HOST_PATHS = {
    "codex": Path(".agents") / "skills" / "p-discovery",
    "opencode": Path(".agents") / "skills" / "p-discovery",
    "claude": Path(".claude") / "skills" / "p-discovery",
}


def install(host: str, scope: str) -> None:
    if not (SOURCE / "SKILL.md").is_file():
        raise SystemExit(f"Missing canonical skill: {SOURCE}")
    root = REPO_ROOT if scope == "project" else Path.home()
    target = root / HOST_PATHS[host]

    if SOURCE.resolve() == target.resolve():
        print(f"{host}: already available at {target} (canonical project skill)")
        return
    if target.exists() or target.is_symlink():
        # Do not overwrite a previously edited skill without permission.
        raise SystemExit(
            f"Target already exists: {target}\n"
            "Move it aside manually if you want to replace it."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, target)
    print(f"{host}: copied skill to {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=(*HOST_PATHS, "all"), default="all")
    parser.add_argument("--scope", choices=("project", "user"), default="project")
    args = parser.parse_args()
    hosts = tuple(HOST_PATHS) if args.host == "all" else (args.host,)
    installed_paths = set()
    for host in hosts:
        target = (REPO_ROOT if args.scope == "project" else Path.home()) / HOST_PATHS[host]
        if target in installed_paths:
            print(f"{host}: shares {target}, already handled")
            continue
        install(host, args.scope)
        installed_paths.add(target)


if __name__ == "__main__":
    main()

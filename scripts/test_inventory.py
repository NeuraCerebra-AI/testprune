#!/usr/bin/env python3
"""Inventory test modules: on disk versus tracked versus gitignored.

Git ignore rules control commits, not test collection. This script shows the
gap so it is visible in the first minutes of a testprune run.

Usage (from the repository root, or pass --root):
    python test_inventory.py [--root PATH] [--dir tests] [--pattern GLOB ...] [--list]

Defaults cover pytest, Jest/Vitest, Go, Rust, and Ruby naming conventions.
Only the standard library and the git CLI are used.
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys

DEFAULT_PATTERNS = [
    "test_*.py", "*_test.py", "tests.py",
    "*.test.js", "*.spec.js", "*.test.ts", "*.spec.ts", "*.test.tsx", "*.spec.tsx", "*.test.mjs",
    "*_test.go",
    "*_test.rs",
    "*_test.rb", "*_spec.rb",
]
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", ".tox", ".mypy_cache", ".pytest_cache", "dist", "build", "target"}


def git(root: str, *args: str) -> str:
    return subprocess.check_output(["git", "-C", root, *args], text=True, stderr=subprocess.DEVNULL)


def on_disk(root: str, base: str, patterns: list[str]) -> set[str]:
    found: set[str] = set()
    start = os.path.join(root, base) if base else root
    for dirpath, dirnames, filenames in os.walk(start):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            if any(fnmatch.fnmatch(name, p) for p in patterns):
                found.add(os.path.relpath(os.path.join(dirpath, name), root))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repository root (default: current directory)")
    ap.add_argument("--dir", default="", help="subdirectory to scan (default: whole repo)")
    ap.add_argument("--pattern", action="append", help="filename glob for test modules; repeatable (default: common conventions)")
    ap.add_argument("--list", action="store_true", help="list the untracked and ignored modules")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    try:
        git(root, "rev-parse", "--is-inside-work-tree")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("not a git repository (or git missing):", root, file=sys.stderr)
        return 2

    patterns = args.pattern or DEFAULT_PATTERNS
    disk = on_disk(root, args.dir, patterns)
    tracked_all = set(git(root, "ls-files").splitlines())
    tracked = disk & tracked_all
    untracked = disk - tracked
    ignored: set[str] = set()
    if untracked:
        out = subprocess.run(
            ["git", "-C", root, "check-ignore", "--stdin"],
            input="\n".join(sorted(untracked)), text=True, capture_output=True,
        )
        ignored = set(out.stdout.splitlines())
    untracked_visible = untracked - ignored

    scope = args.dir or "."
    print(f"scope: {scope}   patterns: {len(patterns)}")
    print(f"test modules on disk:            {len(disk)}")
    print(f"  tracked in git:                {len(tracked)}")
    print(f"  untracked, visible to git:     {len(untracked_visible)}")
    print(f"  untracked and gitignored:      {len(ignored)}   <- still collected by the runner if on disk")
    if args.list:
        for label, group in (("untracked, visible", untracked_visible), ("gitignored", ignored)):
            if group:
                print(f"\n{label}:")
                for path in sorted(group):
                    print("  " + path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

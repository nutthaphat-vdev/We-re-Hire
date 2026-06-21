#!/usr/bin/env python3
"""
PreToolUse hook — enforce GATE 2 for the Cowork->Claude Code bridge.

Blocks git commands that COMMIT, PUBLISH, or DESTROY history/working tree when
Claude Code is launched by the bridge (env BRIDGE_RUN=1). Real, tool-level
enforcement — does NOT depend on the model obeying a preamble instruction.

Scope:
  - Enforces ONLY when BRIDGE_RUN=1 (bridge_runner.py sets it) ->
    P's normal interactive Claude Code sessions are unaffected.
  - Inspects Bash tool calls only.
  - Read-only git (status/diff/log/show/ls-files/...) and all non-git commands
    are allowed. The watcher's own `git diff --stat` runs OUTSIDE Claude Code,
    so reports are unaffected.

Contract (Claude Code hooks):
  stdin: JSON {"tool_name": "...", "tool_input": {"command": "..."}}
  exit 0 -> allow | exit 2 -> BLOCK (stderr shown to Claude)
"""

import json
import os
import re
import sys

DANGER = {
    "commit", "push", "reset", "rebase", "merge", "revert",
    "cherry-pick", "cherry", "restore", "checkout", "switch",
    "clean", "stash", "am", "apply", "filter-branch", "filter-repo",
    "update-ref", "fast-import", "reflog", "gc", "mirror", "prune",
}

OPTS_WITH_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||\n")


def git_subcommands(command):
    for segment in SEGMENT_SPLIT.split(command):
        tokens = segment.strip().split()
        if not tokens:
            continue
        for i, tok in enumerate(tokens):
            base = tok.split("/")[-1].split("\\")[-1]
            if base != "git":
                continue
            j = i + 1
            while j < len(tokens):
                t = tokens[j]
                if t in OPTS_WITH_ARG:
                    j += 2
                    continue
                if t.startswith("-"):
                    j += 1
                    continue
                yield t.lower()
                break
            break


def main():
    if os.environ.get("BRIDGE_RUN") != "1":
        return 0
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    command = (data.get("tool_input") or {}).get("command", "")
    if not isinstance(command, str) or not command.strip():
        return 0

    hit = None
    for sub in git_subcommands(command):
        if sub in DANGER:
            hit = sub
            break
    if hit is None and re.search(r"\bgit\b", command):
        if re.search(r"\bgit\b[^\n;&|]*\b(commit|push|reset|rebase|filter-branch)\b", command):
            hit = "commit/push"
    if hit is None:
        return 0

    sys.stderr.write(
        "BLOCKED by bridge GATE 2: `git " + hit + "` is not allowed from Claude Code.\n"
        "The human reviews the diff and commits/pushes by hand. "
        "Make the file changes and run tests, then STOP and report — "
        "do not touch git history or remotes.\n"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

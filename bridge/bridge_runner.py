#!/usr/bin/env python3
"""
bridge_runner.py — Cowork -> Claude Code file-based bridge (MVP)

Loop:
  Cowork (plan/review) -> [P approve] -> drop task packet in bridge/inbox/<id>.md
  -> this watcher (run in VS Code terminal) fires `claude -p ...` in the repo
  -> P watches edits land live in the editor / Source Control
  -> watcher writes bridge/outbox/<id>.report.md and moves the task to bridge/archive/

Design constraints (see BRIDGE_PLAN.md):
  - Polling only (no watchdog dependency).
  - Whitelisted tools only.
  - GATE 2: watcher NEVER runs git commit/push. P reviews the diff and commits by hand.

Usage:
  python bridge/bridge_runner.py          # from repo root
  (or double-click bridge/start_watcher.bat)

Env overrides (optional):
  CLAUDE_BIN        path/name of the Claude Code CLI   (default: "claude")
  BRIDGE_POLL_SEC   poll interval seconds              (default: 3)
  BRIDGE_SETTLE_SEC ignore files newer than N sec      (default: 4, lets OneDrive finish syncing)
  BRIDGE_TOOLS      allowed tools                       (default: "Read,Edit,Write,Bash,Grep,Glob")
"""

import io
import os
import sys
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout/stderr so Thai text and emoji from Claude don't crash on Windows CP1252
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# --- Paths -------------------------------------------------------------------
BRIDGE_DIR = Path(__file__).resolve().parent
REPO_DIR = BRIDGE_DIR.parent
INBOX = BRIDGE_DIR / "inbox"
OUTBOX = BRIDGE_DIR / "outbox"
ARCHIVE = BRIDGE_DIR / "archive"

# --- Config ------------------------------------------------------------------
POLL_SEC = int(os.environ.get("BRIDGE_POLL_SEC", "3"))
SETTLE_SEC = int(os.environ.get("BRIDGE_SETTLE_SEC", "4"))
ALLOWED_TOOLS = os.environ.get("BRIDGE_TOOLS", "Read,Edit,Write,Bash,Grep,Glob")
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")

# Files in inbox/ that are never treated as tasks.
IGNORE_NAMES = {".gitkeep", "TASK_PACKET_TEMPLATE.md", "README.md"}

OUTPUT_TAIL_LINES = 120  # how much CC output to keep in the report

PREAMBLE = """You are running inside a file-based bridge from Cowork. Execute the task packet below.

HARD RULES (do not violate):
1. NEVER run `git commit`, `git push`, `git reset`, `git checkout -- .`, or anything that
   rewrites history or publishes. The human (P) reviews your diff and commits by hand.
2. Stay inside this repository. Do not touch files outside it.
3. Only use the allowed tools you were granted.
4. Do not delete `statement_cache_size=0` or change auth/JWT logic unless the task explicitly says so.
5. If you get stuck, hit something ambiguous, or the change looks risky/irreversible — STOP and
   write what's blocking you instead of guessing.
6. Follow the project rules in CLAUDE.md.

When done, give a short report: what you changed, what to watch out for, and a suggested test.

================= TASK PACKET =================
"""


def log(msg: str) -> None:
    print(f"[bridge {datetime.now():%H:%M:%S}] {msg}", flush=True)


def resolve_claude() -> str:
    found = shutil.which(CLAUDE_BIN)
    if found:
        return found
    # On Windows the CLI is often claude.cmd — let shutil try variants.
    for ext in (".cmd", ".exe", ".bat"):
        found = shutil.which(CLAUDE_BIN + ext)
        if found:
            return found
    return CLAUDE_BIN  # fall back; Popen may still resolve it via PATH


def ensure_dirs() -> None:
    for d in (INBOX, OUTBOX, ARCHIVE):
        d.mkdir(parents=True, exist_ok=True)


def list_tasks() -> list[Path]:
    tasks = []
    for p in sorted(INBOX.glob("*.md")):
        if p.name in IGNORE_NAMES:
            continue
        tasks.append(p)
    return tasks


def is_settled(p: Path) -> bool:
    """Avoid grabbing a file mid-sync (OneDrive write delay)."""
    try:
        age = time.time() - p.stat().st_mtime
    except OSError:
        return False
    return age >= SETTLE_SEC


def git_diff_stat() -> str:
    try:
        out = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        stat = (out.stdout or "").strip()
        # also include untracked files so new files show up
        untr = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        new_files = (untr.stdout or "").strip()
        parts = []
        if stat:
            parts.append(stat)
        if new_files:
            parts.append("New (untracked) files:\n" + new_files)
        return "\n\n".join(parts) if parts else "(no changes detected)"
    except Exception as e:  # noqa: BLE001
        return f"(git diff failed: {e})"


def run_task(task_path: Path, claude_path: str) -> None:
    task_id = task_path.stem
    packet = task_path.read_text(encoding="utf-8", errors="replace")
    prompt = PREAMBLE + packet

    cmd = [claude_path, "-p", prompt, "--allowedTools", ALLOWED_TOOLS]

    log(f"START  task={task_id}")
    log(f"       cmd: {claude_path} -p <prompt> --allowedTools {ALLOWED_TOOLS}")
    print("-" * 70, flush=True)

    captured: list[str] = []
    started = time.time()
    status = "ok"
    rc = 0

    # Mark this as a bridge-launched run so the PreToolUse hook
    # (.claude/hooks/block_git_write.py) enforces GATE 2 — and does NOT
    # interfere with P's normal interactive Claude Code sessions.
    child_env = dict(os.environ)
    child_env["BRIDGE_RUN"] = "1"

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=REPO_DIR,
            env=child_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except FileNotFoundError:
        log(f"ERROR  Claude CLI not found ('{claude_path}'). Set CLAUDE_BIN env var.")
        write_report(task_id, "error", "Claude CLI not found. Set CLAUDE_BIN.", 127, 0.0)
        archive_task(task_path)
        return

    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stdout.write(line)  # live stream -> P watches in terminal
            sys.stdout.flush()
            captured.append(line)
        rc = proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        status = "interrupted"
        log("interrupted by user — terminating Claude Code")
    if rc != 0 and status == "ok":
        status = "error"

    elapsed = time.time() - started
    print("-" * 70, flush=True)
    log(f"DONE   task={task_id} status={status} rc={rc} ({elapsed:.0f}s)")

    tail = "".join(captured[-OUTPUT_TAIL_LINES:]).rstrip()
    write_report(task_id, status, tail, rc, elapsed)
    archive_task(task_path)


def write_report(task_id: str, status: str, output_tail: str, rc: int, elapsed: float) -> None:
    report = OUTBOX / f"{task_id}.report.md"
    diff = git_diff_stat()
    content = f"""# Report — {task_id}

- **Status:** {status}
- **Exit code:** {rc}
- **Duration:** {elapsed:.0f}s
- **Finished:** {datetime.now():%Y-%m-%d %H:%M:%S}

> GATE 2: review the diff in VS Code Source Control, then commit yourself.
> The watcher did NOT commit or push.

## git diff --stat
```
{diff}
```

## Claude Code output (last {OUTPUT_TAIL_LINES} lines)
```
{output_tail}
```
"""
    report.write_text(content, encoding="utf-8")
    log(f"REPORT {report.relative_to(REPO_DIR)}")


def archive_task(task_path: Path) -> None:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = ARCHIVE / f"{ts}__{task_path.name}"
    try:
        shutil.move(str(task_path), str(dest))
        log(f"ARCHIVE {dest.relative_to(REPO_DIR)}")
    except Exception as e:  # noqa: BLE001
        log(f"WARN   could not archive {task_path.name}: {e}")


def main() -> int:
    ensure_dirs()
    claude_path = resolve_claude()

    print("=" * 70)
    print(" Cowork -> Claude Code bridge watcher")
    print(f"   repo    : {REPO_DIR}")
    print(f"   inbox   : {INBOX.relative_to(REPO_DIR)}/")
    print(f"   tools   : {ALLOWED_TOOLS}")
    print(f"   claude  : {claude_path}")
    print(f"   poll    : every {POLL_SEC}s  (settle {SETTLE_SEC}s)")
    print("   GATE 2  : watcher never commits/pushes — you review + commit by hand")
    print("   stop    : Ctrl+C")
    print("=" * 70, flush=True)
    if shutil.which(claude_path) is None and not Path(claude_path).exists():
        log("WARN   Claude CLI not detected on PATH yet. Set CLAUDE_BIN if runs fail.")

    try:
        while True:
            for task in list_tasks():
                if is_settled(task):
                    run_task(task, claude_path)
                    break  # re-scan from top after each task
            time.sleep(POLL_SEC)
    except KeyboardInterrupt:
        print()
        log("watcher stopped. bye.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

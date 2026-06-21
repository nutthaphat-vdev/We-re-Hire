# bridge/ — Cowork → Claude Code bridge (MVP)

File-based bus so Cowork (plan/review) can hand execution to Claude Code running live in
your VS Code terminal, while you (P) watch the edits land and stay the only one who commits.

```
Cowork: plan + you approve (GATE 1)
   └─> drop  bridge/inbox/<id>.md   (filled TASK_PACKET_TEMPLATE.md)
            └─> bridge_runner.py (in VS Code terminal) fires:
                 claude -p "<preamble + packet>" --allowedTools Read,Edit,Write,Bash,Grep,Glob
                   • output streams to the terminal (you watch)
                   • file edits appear live in editor / Source Control
            └─> writes bridge/outbox/<id>.report.md  (status + git diff --stat + output tail)
            └─> moves the task into bridge/archive/
You: review diff in Source Control, then COMMIT yourself (GATE 2)
```

## Run it
From the repo root, in a VS Code terminal:

```
bridge\start_watcher.bat
```
or
```
python bridge\bridge_runner.py
```

Leave it running. It polls `bridge/inbox/` every few seconds.

## Send a task
1. Copy `TASK_PACKET_TEMPLATE.md`, fill in Goal / Files / Acceptance / Constraints / Context.
2. Save it as `bridge/inbox/YYYYMMDD-HHMM-short-name.md`.
3. Watch Claude Code work in the terminal. When it finishes, read `bridge/outbox/<id>.report.md`.

## The two gates (do not skip)
- **GATE 1** — you approve the plan in Cowork *before* a task packet is written.
- **GATE 2** — after Claude Code finishes, you review the diff in VS Code Source Control and
  **commit by hand**. The watcher never runs `git commit`/`push` (enforced + told to CC in the preamble).

## Config (env vars, all optional)
| var | default | meaning |
|-----|---------|---------|
| `CLAUDE_BIN` | `claude` | path/name of the Claude Code CLI |
| `BRIDGE_POLL_SEC` | `3` | poll interval |
| `BRIDGE_SETTLE_SEC` | `4` | ignore files newer than this (lets OneDrive finish syncing) |
| `BRIDGE_TOOLS` | `Read,Edit,Write,Bash,Grep,Glob` | whitelisted tools |

## Security note
A folder that auto-runs Claude Code on dropped files is an RCE surface on yourself. Keep it
**local only**, keep the tool whitelist tight, and don't point `inbox/` at any shared/public path
beyond your own OneDrive. The preamble forbids commit/push but `Bash` is still allowed for tests —
that's the accepted MVP tradeoff.

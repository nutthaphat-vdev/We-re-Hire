# Cowork → Claude Code Bridge — Plan (build next session, in this Hire repo)

## เป้า
loop: **Cowork (คุย/plan/review) → [P approve] → Claude Code ใน VS Code (execute, P นั่งดู) → report → Cowork review**
P อยากเห็นมันทำงานสดใน VS Code: พอ add task → watcher ยิง Claude Code ทำงานให้ดูเลย

## ข้อจำกัดที่กำหนด design
Cowork bash = sandbox แยกจากเครื่องจริง → เชื่อมผ่าน **shared folder เท่านั้น** (OneDrive)
→ MVP = file-based bus + **watcher รันใน VS Code terminal** (ไม่ใช่ MCP — Cowork อาจเพิ่ม local MCP เองไม่ได้)

## MVP = 3 ชิ้น (build ใน `bridge/` ใต้ repo นี้)
1. **`bridge/bridge_runner.py`** — polling watcher (ไม่ต้อง watchdog) รันใน VS Code terminal
   - เห็น `inbox/*.md` ใหม่ → ยิง `claude -p "<preamble+packet>" --allowedTools "Read,Edit,Write,Bash,Grep,Glob"` cwd=repo
   - stream output → terminal (P watch) + ไฟล์แก้โผล่ใน editor/Source Control สด
   - เสร็จ → เขียน `outbox/<id>.report.md` (status + git diff --stat + output tail) → ย้าย task ไป archive/
2. **`bridge/TASK_PACKET_TEMPLATE.md`** — Goal / Files / Acceptance criteria / Constraints / Context pointer
3. **`bridge/start_watcher.bat`** — กดเปิด watcher จาก repo root (ASCII+CRLF)

## 2 GATE (ห้ามข้าม — หลัก agent เสนอ คนตัดสิน irreversible)
- **GATE 1:** P approve plan ใน Cowork ก่อนเขียน task packet
- **GATE 2:** หลัง CC ทำเสร็จ P review diff ใน VS Code Source Control แล้ว **commit เอง** — watcher **ห้าม auto commit/push**

## Devil caveats
- OneDrive sync หน่วงไม่กี่วินาที (add task → เริ่ม มี delay sync) — รับได้
- preamble บังคับใน prompt: "ห้าม git commit/push, อยู่ใน repo, ติดให้หยุดบอก"
- security: file-drop ที่ auto-run CC = RCE surface ตัวเอง → whitelist tools + local only

## เริ่ม session หน้า
เปิด Cowork ในโฟลเดอร์ `C:\Users\User\Downloads\Hire` แล้วพิมพ์ "build bridge ตาม BRIDGE_PLAN.md"
(design เต็มอยู่ที่ Quant Co-work/COWORK_CLAUDECODE_BRIDGE_DESIGN.md)

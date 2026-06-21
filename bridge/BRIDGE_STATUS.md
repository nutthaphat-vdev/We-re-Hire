# Bridge Status — Cowork → Claude Code

อัปเดต: 2026-06-21

---

## ภาพรวม

Bridge เป็น file-based bus ที่เชื่อม **Cowork** (ฝั่ง plan/review) กับ **Claude Code** (ฝั่ง execute ใน VS Code terminal) โดยที่ P (พี่) เป็นคนเดียวที่ commit/push — Claude Code ทำได้แค่แก้ไฟล์ในโฟลเดอร์ repo

**ออกแบบมาเพราะ:** Cowork bash รันใน sandbox แยกจากเครื่องจริง เชื่อมตรงไม่ได้ → ใช้ shared folder (OneDrive) เป็น bus แทน

---

## Flow การทำงาน

```
Cowork: plan + P approve (GATE 1)
  └─> drop  bridge/inbox/<id>.md
              └─> bridge_runner.py (รันใน VS Code terminal) fires:
                   claude -p "<preamble + packet>" --allowedTools Read,Edit,Write,Bash,Grep,Glob
                     • output stream → terminal (P นั่งดูสด)
                     • file edits โผล่ใน editor / Source Control ทันที
              └─> เขียน bridge/outbox/<id>.report.md (status + git diff --stat + output tail 120 lines)
              └─> ย้าย task ไป bridge/archive/<timestamp>__<id>.md
P: review diff ใน Source Control → COMMIT เอง (GATE 2)
```

---

## ไฟล์แต่ละตัวทำอะไร

| ไฟล์ | หน้าที่ |
|------|---------|
| `bridge_runner.py` | Polling watcher หลัก — วนทุก 3s เช็ค `inbox/*.md` → ยิง `claude -p` → เขียน report → archive task |
| `start_watcher.bat` | Shortcut เปิด watcher จาก repo root (ตรวจหา `py` ก่อน ถ้าไม่มีใช้ `python`) |
| `TASK_PACKET_TEMPLATE.md` | Template สร้าง task packet (Goal / Files / Acceptance criteria / Constraints / Context pointer) |
| `README.md` | สรุป flow + วิธีใช้ + config env vars + security note |
| `.gitignore` | กัน `inbox/*.md` (tasks ที่รอ) และ `outbox/*.md` (reports) ไม่ให้ขึ้น git — archive/ เท่านั้นที่ track |
| `inbox/` | drop zone สำหรับ task packets (`.gitkeep` อยู่เพื่อให้ folder ขึ้น git) |
| `outbox/` | รายงานผล (`.report.md`) จาก Claude Code แต่ละ task |
| `archive/` | task packets ที่ run แล้ว (ย้ายมาพร้อม timestamp) |

---

## 2 GATE (ห้ามข้าม)

### GATE 1 — Plan approval
P approve plan ใน Cowork **ก่อน** เขียน task packet ลง inbox/ เพื่อกัน Claude Code ทำงานที่ไม่ได้ approve

### GATE 2 — Commit by hand
หลัง Claude Code ทำงานเสร็จ P **review diff ใน VS Code Source Control** แล้ว commit เอง  
→ มีสองชั้นรับประกัน:
1. **PREAMBLE ใน code** (บรรทัด 54–68 ของ `bridge_runner.py`): บอก Claude Code ว่า "ห้าม git commit/push/reset/checkout -- . ทุกกรณี"
2. **ALLOWED_TOOLS** ที่ส่งให้ Claude Code: `Read,Edit,Write,Bash,Grep,Glob` — `Bash` ยังมีอยู่สำหรับ test แต่ preamble ห้ามใช้กับ git destructive commands

---

## ข้อจำกัดและความเสี่ยง

| จุด | รายละเอียด |
|-----|-----------|
| **OneDrive sync delay** | task packet drop ลง inbox/ แล้ว bridge อาจยังไม่เห็นทันที (delay sync) — `BRIDGE_SETTLE_SEC=4` กันไฟล์ที่ยังเขียนไม่เสร็จ |
| **RCE surface** | folder ที่ auto-run Claude Code บนไฟล์ที่ drop = ถ้าใครเข้าถึง inbox/ ได้ → run code บนเครื่องได้ ต้อง local only ห้าม share path สาธารณะ |
| **Bash ยังอยู่ใน whitelist** | Claude Code ใช้ Bash สำหรับ test ได้ — preamble ห้าม git commands แต่ไม่ได้ block Bash ทั้งหมด |
| **Task 1 ครั้ง** | watcher ทำทีละ 1 task แล้ว re-scan (ไม่ parallel) — task ที่ 2 รอต่อ queue ตามลำดับ |
| **Output tail 120 บรรทัด** | report เก็บแค่ 120 บรรทัดสุดท้ายของ output — task ที่ยาวมาก log ต้นๆ หาย (ต้องดูใน terminal สด) |
| **Token permission prompt** | Claude Code อาจถามยืนยัน permission ระหว่างทำงาน → block โดยไม่มีคนกด → task ค้าง (เห็นแล้วใน task แรก) |

---

## สถานะตอนนี้ (2026-06-21)

- **Watcher:** รันอยู่ (task ID `brv5gq1ei` ใน Claude Code session)
- **Task แรก:** `20260621-0925-bridge-status-report` — run เสร็จ status=ok, archived แล้ว
- **inbox/:** ว่าง (พร้อมรับ task ใหม่)
- **outbox/:** มี 1 report (`20260621-0925-bridge-status-report.report.md`)
- **archive/:** มี 1 task ที่ archived

---

## วิธีใช้ย่อ

```
# 1. เปิด watcher (ครั้งเดียว ค้างไว้)
python bridge\bridge_runner.py

# 2. ส่ง task
# copy TASK_PACKET_TEMPLATE.md → กรอก Goal/Files/Criteria/Constraints
# save เป็น bridge/inbox/YYYYMMDD-HHMM-short-name.md
# รอดูใน terminal → อ่าน bridge/outbox/<id>.report.md

# 3. Review + commit เอง (GATE 2)
# VS Code Source Control → review diff → git commit -m "..."
```

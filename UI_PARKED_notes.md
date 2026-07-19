# UI / Readability — Parked Decisions

> สถานะ: **PARK** · P ตัดสิน 2026-07-08: signal ยังไม่ strong พอที่จะแก้
> จดไว้กันลืม + กันคิดใหม่ตั้งแต่ต้นตอนกลับมา

---

## 1. Theme — dark-green vs light/ขาว
**Feedback:** worker บางคนบอก **ขาวอ่านง่ายกว่า** (จาก 3 คน = weak signal)

**Reframe คำถาม:** ไม่ใช่ "อันไหนสวย" (= รสนิยมเรา) แต่คือ
> "คนอายุมากขึ้น ยืนกลางแดด ถือมือถือถูกๆ ต้องใช้หาเงิน — อ่านอันไหนง่าย?"

- **dark-green:** พรีเมียม/ดีตอน pitch · แต่ washout กลางแดด + text เทาจางบนดำ contrast ต่ำ + สายตาเอียงเห็นเบลอ
- **light:** อ่านง่ายกว่าคนส่วนใหญ่, สู้แดด, น่าเชื่อถือ (เหมือน LINE/แอปธนาคารที่กลุ่มนี้ใช้)

**แนวที่เอน (ถ้าตัดสินใจทำ):**
- **แอป (ใช้จริง) = light default + เขียวเป็น accent** → อ่านง่าย + คงแบรนด์
- **landing/pitch = เก็บ dark-green** (audience = นักลงทุน/tech)
- **อย่าทำ theme toggle** (over-engineer + กลุ่มนี้ไม่กดหาเอง) · แค่ตัดสิน default

**Decision: PARK** — signal ยังไม่ strong พอ + re-theme = งานใหญ่ (dark hardcode + rgba ทั้ง index.html 4400 บรรทัด)

---

## 2. Zoom ค้าง (worker บอก "ดูยาก")
- ⚠️ **reset/ปิด pinch-zoom ทำไม่ได้จริงบน iOS Safari** (Apple ล็อกเพื่อ accessibility ตั้งแต่ iOS 10) → **อย่าไล่ทำ reset · อย่าใส่ `user-scalable=no`**
- **สาเหตุจริง = อ่านไม่ออกเลยต้องซูม** แล้วติดค้าง
- **Quick wins (ถูก, ไม่ผูกกับ theme):**
  - body มือถือ **13px → 15-16px** + line-height เยอะขึ้น (13px เล็กไปสำหรับกลุ่มนี้)
  - tap target ใหญ่ขึ้น
  - `touch-action: manipulation` → ฆ่า double-tap-zoom ที่เผลอโดน (ไม่กระทบ pinch ของคนที่จำเป็น)

---

## Trigger ให้ unpark (กลับมาทำเมื่อ):
- **employer บ่นด้วย** (cross-side signal) หรือ user เยอะขึ้นบ่นเรื่องเดียวกัน
- readability ทำให้มีคน **ทำงานไม่จบจริง**
- ตอนทำ **mobile pass รอบหน้า** อยู่แล้ว → เอา font 13→16 + touch-action แถมไปเลย (near-free ไม่ผูก theme)

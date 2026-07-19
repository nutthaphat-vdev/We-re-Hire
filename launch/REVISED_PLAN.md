# WeHire — Revised Launch Plan (ปรับตาม devil review 2026-06-26)

> หลักการ: **narrow + dense · reliability + seed ก่อน · build/policy ไม่สร้าง traction**
> traction ที่ angel อยากเห็น = จำนวนงาน completed จริง + repeat employer

## ลำดับใหม่ (ทำตามนี้)

### Phase 0 — ก่อนปล่อย user จริง (สัปดาห์นี้)
1. **Reliability — keep-alive กัน Render หลับ** (15 นาที ไม่ต้องเขียนโค้ด)
   - สมัคร UptimeRobot (ฟรี) → New Monitor → HTTP(s) → URL: `https://we-re-hire.onrender.com/health` → interval 5 นาที
   - (ทางเลือก: cron-job.org ก็ได้) → Render จะไม่หลับ → request แรกไม่ fail
2. **QA loop เต็มบนมือถือจริง** → `launch/QA_LOOP_CHECKLIST.md` (เจอพังแก้ก่อน)
3. **Policy consent ในแอป** → task อยู่ใน `bridge/inbox/20260630-policy-consent-implement.md` (legal must-have ก่อนเก็บ KYC จริง)

### Phase 1 — narrow launch (อังคาร+ — ดู task schedule + kit)
4. เลือก **1 โซน + 1 หมวดเดียว** (เช่น ก่อสร้าง หรือ f&b)
5. **Seed supply ด้วยมือก่อนเปิด** — recruit worker 10-15 + employer 2-3 ในหมวดนั้น (แอปจะได้ดูมีชีวิตตอนคนจริงเปิด)
6. ดันให้เกิด **~20 งาน completed** + repeat → เก็บ metric ไว้ pitch

### Deferred (ทำทีหลัง)
- **`018_job_categories_v2.sql` = ON HOLD** อย่าเพิ่งรัน — เปิดหมวดใหม่ทีละหมวด "เมื่อมี supply" เท่านั้น (กันหมวดว่าง = แอปดูร้าง)
- ขยาย catalog / feature อื่นๆ

## เตือนตัวเอง (จาก devil)
- การ build หมวด/policy/เครื่องมือ = สบายกว่าโทรหา employer → ระวัง comfort-zone หนีงาน outreach จริง
- policy + dedupe หมวด = จำเป็น (กฎหมาย/คุณภาพ) แต่ **ไม่ใช่ traction** — ลำดับต้อง reliability+seed มาก่อน

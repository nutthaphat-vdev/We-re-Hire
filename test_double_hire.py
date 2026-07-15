"""
WeHire — Double-Hire Guard & Time-Overlap Test
ทดสอบ fix จุด 2: overlap withdraw (time-based) + double-hire guard + multi-day span

ครอบคลุม:
  1. Overlap withdraw  — hire B(09-13) → A(08-12) ถอด, C(14-18) อยู่
  2. Double-hire guard — hire X(09-13) แล้วสมัคร+hire Y(10-12) ทับ → ต้องเด้ง 409
  3. Non-overlap OK    — hired X(09-13) แล้ว hire Z(14-18) ไม่ทับ → ผ่าน 200
  4. Multi-day span    — hire M(3วัน 09-13) แล้ว hire N(วันที่2 15-18) → เด้ง 409 (ล็อกทั้งสแปน)

⚠️  ต้อง run migration 023_job_time_range.sql บน DB เป้าหมายก่อน
    (ไม่งั้น decide จะ error เพราะไม่มี function job_occupied_range)

Usage:
  python test_double_hire.py --url http://localhost:8000     # local (แนะนำ)
  python test_double_hire.py --url https://we-re-hire.onrender.com   # prod (ระวัง! สร้าง test data จริง)
"""

import argparse
import io
import random
import sys
import uuid
from datetime import datetime, timezone, timedelta, date
import httpx

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DEFAULT_BASE = "http://localhost:8000"

# GPS: Siam Paragon — worker + job จุดเดียวกัน ผ่าน radius check
LAT, LNG = 13.7466, 100.5347

RUN_ID    = uuid.uuid4().hex[:6]
EMP_EMAIL = f"test_dh_emp_{RUN_ID}@wehire-test.com"
WRK_EMAIL = f"test_dh_wrk_{RUN_ID}@wehire-test.com"
PWD       = "TestPass123!"
# phone ต้อง unique + format 0XXXXXXXXX (10 หลัก ขึ้นต้น 0)
EMP_PHONE = "0" + "".join(random.choices("0123456789", k=9))
WRK_PHONE = "0" + "".join(random.choices("0123456789", k=9))

# วันที่อนาคตไกลๆ กันชน cron (checkin/noshow/D-1) และข้อมูลจริง
D1 = (date.today() + timedelta(days=30)).isoformat()   # test 1
D2 = (date.today() + timedelta(days=40)).isoformat()   # test 2 & 3
D3 = (date.today() + timedelta(days=50)).isoformat()   # test 4 (multi-day start)
D3_DAY2 = (date.today() + timedelta(days=51)).isoformat()

results: list[tuple[str, bool, str]] = []


def step(name: str, ok: bool, detail: str = ""):
    icon = "✅ PASS" if ok else "❌ FAIL"
    print(f"  {icon}  {name}" + (f"\n         {detail}" if detail else ""))
    results.append((name, ok, detail))
    return ok


def api(c, method, path, token="", **kw):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    return c.request(method, path, headers=h, timeout=30, **kw)


def check(r, expected=200) -> dict:
    if r.status_code != expected:
        raise AssertionError(f"HTTP {r.status_code} (expected {expected}): {r.text[:200]}")
    return r.json() if r.text else {}


def post_job(c, tok, title, start_date, ws, we, duration=1):
    r = api(c, "POST", "/jobs", token=tok, json={
        "title": f"{title} {RUN_ID}",
        "description": "double-hire test — safe to ignore",
        "required_skills": ["cleaning"],
        "daily_wage_rate": 500.0,
        "duration_days": duration,
        "slots_available": 1,
        "lat": LAT, "lng": LNG,
        "location_name": "Siam Paragon",
        "start_date": start_date,
        "work_start": ws, "work_end": we,
    })
    return check(r, 201)["id"]


def apply_job(c, tok, job_id) -> str:
    r = api(c, "POST", f"/jobs/{job_id}/apply", token=tok, json={"lat": LAT, "lng": LNG})
    return check(r, 201)["application_id"]


def _code_body(r):
    return r.status_code, (r.json() if r.text and r.headers.get("content-type","").startswith("application/json") else r.text)


def hire(c, tok, app_id):
    """คืน (status_code, body_or_text)"""
    r = api(c, "PATCH", f"/applications/{app_id}/decide", token=tok,
            json={"decision": "hired", "note": "test"})
    return _code_body(r)


def send_backup(c, tok, app_id):
    return _code_body(api(c, "POST", f"/applications/{app_id}/send-backup", token=tok))


def accept_backup(c, tok, app_id):
    return _code_body(api(c, "POST", f"/applications/{app_id}/accept-backup", token=tok))


def app_status_map(c, tok) -> dict:
    """{ application_id: status } จาก worker apps list"""
    r = api(c, "GET", "/workers/applications", token=tok)
    apps = check(r, 200)
    return {a["id"]: a["status"] for a in apps}


def run(base: str) -> bool:
    print(f"\n{'='*62}\n  Double-Hire Guard Test  —  {base}\n  Run ID: {RUN_ID}\n{'='*62}\n")

    with httpx.Client(base_url=base) as c:
        # ── Setup ────────────────────────────────────────────────
        try:
            emp = check(api(c, "POST", "/auth/register",
                            json={"email": EMP_EMAIL, "password": PWD, "role": "employer",
                                  "phone": EMP_PHONE, "terms_accepted": True}), 201)["access_token"]
            check(api(c, "POST", "/employers/profile", token=emp,
                      json={"company_name": f"DH Corp {RUN_ID}", "business_type": "retail",
                            "contact_person": "Mgr"}), 201)
            wrk = check(api(c, "POST", "/auth/register",
                            json={"email": WRK_EMAIL, "password": PWD, "role": "worker",
                                  "phone": WRK_PHONE, "terms_accepted": True}), 201)["access_token"]
            check(api(c, "POST", "/workers/profile", token=wrk,
                      json={"full_name": f"DH Worker {RUN_ID}", "skills": ["cleaning"],
                            "experience_years": 1, "daily_rate_expected": 400.0,
                            "lat": LAT, "lng": LNG, "location_name": "Siam"}), 201)
            step("0. Setup (emp + worker + profiles)", True)
        except Exception as e:
            step("0. Setup", False, str(e))
            return _summary()

        # ── Test 1: Overlap withdraw ตอน hire ────────────────────
        try:
            a = post_job(c, emp, "A", D1, "08:00", "12:00")
            b = post_job(c, emp, "B", D1, "09:00", "13:00")
            cc = post_job(c, emp, "C", D1, "14:00", "18:00")
            aa = apply_job(c, wrk, a)
            ab = apply_job(c, wrk, b)
            ac = apply_job(c, wrk, cc)
            code, _ = hire(c, emp, ab)   # hire B
            assert code == 200, f"hire B expected 200 got {code}"
            st = app_status_map(c, wrk)
            ok = (st.get(ab) == "hired" and st.get(aa) == "withdrawn" and st.get(ac) == "applied")
            step("1. Overlap withdraw (hire B→ A ถอด, C อยู่)", ok,
                 f"A={st.get(aa)} B={st.get(ab)} C={st.get(ac)}  (คาด withdrawn/hired/applied)")
        except Exception as e:
            step("1. Overlap withdraw", False, str(e))

        # ── Test 2: Double-hire guard ────────────────────────────
        try:
            x = post_job(c, emp, "X", D2, "09:00", "13:00")
            y = post_job(c, emp, "Y", D2, "10:00", "12:00")   # ทับ X
            ax = apply_job(c, wrk, x)
            code_x, _ = hire(c, emp, ax)                       # hire X ก่อน
            assert code_x == 200, f"hire X expected 200 got {code_x}"
            ay = apply_job(c, wrk, y)                          # สมัคร Y หลังถูก hire X (apply อิสระ)
            code_y, body_y = hire(c, emp, ay)                  # hire Y → ต้องเด้ง
            ok = code_y == 409
            detail = body_y.get("detail", "") if isinstance(body_y, dict) else str(body_y)
            step("2. Double-hire guard (hire Y ทับ X → 409)", ok,
                 f"got HTTP {code_y}  detail={detail[:60]}")
        except Exception as e:
            step("2. Double-hire guard", False, str(e))

        # ── Test 3: Non-overlap ผ่านได้ (หลาย job/วัน) ───────────
        try:
            z = post_job(c, emp, "Z", D2, "14:00", "18:00")    # ไม่ทับ X(09-13)
            az = apply_job(c, wrk, z)
            code_z, _ = hire(c, emp, az)                        # hire Z → ควรผ่าน
            ok = code_z == 200
            step("3. Non-overlap OK (hire Z 14-18 ไม่ทับ X → 200)", ok, f"got HTTP {code_z}")
        except Exception as e:
            step("3. Non-overlap OK", False, str(e))

        # ── Test 4: Multi-day ล็อกทั้งสแปน ───────────────────────
        try:
            m = post_job(c, emp, "M", D3, "09:00", "13:00", duration=3)   # 3 วัน
            n = post_job(c, emp, "N", D3_DAY2, "15:00", "18:00")          # วันที่2 เวลาไม่ทับ แต่อยู่ในสแปน
            am = apply_job(c, wrk, m)
            code_m, _ = hire(c, emp, am)
            assert code_m == 200, f"hire M expected 200 got {code_m}"
            an = apply_job(c, wrk, n)
            code_n, body_n = hire(c, emp, an)                  # ต้องเด้ง (multi-day บล็อกทั้งวัน)
            ok = code_n == 409
            detail = body_n.get("detail", "") if isinstance(body_n, dict) else str(body_n)
            step("4. Multi-day span (hire N ในสแปน M → 409)", ok,
                 f"got HTTP {code_n}  detail={detail[:60]}")
        except Exception as e:
            step("4. Multi-day span", False, str(e))

        # ── Test 5: Backup-accept double-hire guard ──────────────
        try:
            D5 = (date.today() + timedelta(days=60)).isoformat()
            j1 = post_job(c, emp, "J1", D5, "09:00", "13:00")
            j2 = post_job(c, emp, "J2", D5, "10:00", "12:00")   # ทับ J1
            aj1 = apply_job(c, wrk, j1)
            code_j1, _ = hire(c, emp, aj1)                       # hire J1
            assert code_j1 == 200, f"hire J1 expected 200 got {code_j1}"
            aj2 = apply_job(c, wrk, j2)                          # สมัคร J2 (หลัง hired J1)
            code_sb, _ = send_backup(c, emp, aj2)                # employer ส่ง backup offer J2
            code_ab, body_ab = accept_backup(c, wrk, aj2)        # worker รับ backup → ต้องเด้ง
            ok = code_ab == 409
            detail = body_ab.get("detail", "") if isinstance(body_ab, dict) else str(body_ab)
            step("5. Backup-accept double-hire (accept J2 ทับ J1 → 409)", ok,
                 f"send-backup={code_sb} accept={code_ab}  detail={detail[:50]}")
        except Exception as e:
            step("5. Backup-accept double-hire", False, str(e))

    return _summary()


def _summary() -> bool:
    passed = sum(1 for _, ok, _ in results if ok)
    total  = len(results)
    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{'─'*62}\n  Result: {passed}/{total} passed")
    if failed:
        print("  Failed:")
        for n in failed:
            print(f"    • {n}")
    else:
        print("  🎉  All passed — double-hire guard ทำงานถูกต้อง")
    print(f"{'─'*62}\n")
    return not failed


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=DEFAULT_BASE)
    args = p.parse_args()
    sys.exit(0 if run(args.url.rstrip("/")) else 1)

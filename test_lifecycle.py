"""
WeHire — Job Lifecycle Integration Test
ทดสอบ flow ทั้งหมด: register → post job → apply → hire → checkin → start → complete → verify

Usage:
  python test_lifecycle.py                         # ยิงไป production
  python test_lifecycle.py --url http://localhost:8000  # local
  python test_lifecycle.py --cleanup               # ลบ test users หลัง test
"""

import argparse
import io
import sys
import uuid
from datetime import datetime, timezone, timedelta
import httpx


def _now_plus(hours: int) -> str:
    """เวลาปัจจุบัน TH + N ชั่วโมง → 'HH:MM' (ใช้ใน work_start/work_end)"""
    th = datetime.now(timezone(timedelta(hours=7))) + timedelta(hours=hours)
    return th.strftime("%H:%M")

# Force UTF-8 output on Windows so emoji prints correctly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── Config ────────────────────────────────────────────────────────────────
DEFAULT_BASE = "https://web-production-03c5a.up.railway.app"

# GPS: ใช้ตึก Siam Paragon (กลาง BKK) — job + worker อยู่จุดเดียวกัน ผ่าน 150m check
JOB_LAT =  13.7466  # Siam Paragon
JOB_LNG = 100.5347

WORKER_LAT = JOB_LAT   # 0 เมตร จาก job → ผ่าน GPS check แน่นอน
WORKER_LNG = JOB_LNG

# Test account credentials (random suffix กัน conflict)
RUN_ID     = uuid.uuid4().hex[:6]
EMP_EMAIL  = f"test_emp_{RUN_ID}@wehire-test.com"
EMP_PASS   = "TestPass123!"
WRK_EMAIL  = f"test_wrk_{RUN_ID}@wehire-test.com"
WRK_PASS   = "TestPass123!"


# ─── Helpers ───────────────────────────────────────────────────────────────

PASS = "✅ PASS"
FAIL = "❌ FAIL"

results: list[tuple[str, bool, str]] = []


def step(name: str, ok: bool, detail: str = ""):
    icon = PASS if ok else FAIL
    msg  = f"  {icon}  {name}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    results.append((name, ok, detail))
    return ok


def api(client: httpx.Client, method: str, path: str, token: str = "", **kwargs):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = client.request(method, path, headers=headers, timeout=30, **kwargs)
    return r


def check(r: httpx.Response, expected_status: int = 200) -> dict:
    if r.status_code != expected_status:
        raise AssertionError(
            f"HTTP {r.status_code} (expected {expected_status}): {r.text[:200]}"
        )
    return r.json()


# ─── Test Runner ───────────────────────────────────────────────────────────

def run_tests(base: str) -> bool:
    print(f"\n{'='*60}")
    print(f"  WeHire Lifecycle Test  —  {base}")
    print(f"  Run ID: {RUN_ID}")
    print(f"{'='*60}\n")

    with httpx.Client(base_url=base) as c:

        # ── Step 0: Health check ──────────────────────────────────────────
        try:
            r = api(c, "GET", "/health")
            ok = r.status_code in (200, 404)  # 404 ถ้าไม่มี /health ก็ผ่าน
            step("0. Backend reachable", ok, f"HTTP {r.status_code}")
        except Exception as e:
            step("0. Backend reachable", False, str(e))
            print("\n⛔  Backend ไม่ตอบสนอง — หยุด test")
            return False

        # ── Step 1: Register Employer ─────────────────────────────────────
        emp_token = ""
        try:
            r = api(c, "POST", "/auth/register", json={
                "email": EMP_EMAIL, "password": EMP_PASS, "role": "employer"
            })
            data = check(r, 201)
            emp_token = data["access_token"]
            step("1a. Register employer", True, f"user_id={data['user_id'][:8]}…")
        except Exception as e:
            step("1a. Register employer", False, str(e))
            return _summary()

        # ── Step 1b: Create Employer Profile ─────────────────────────────
        try:
            r = api(c, "POST", "/employers/profile", token=emp_token, json={
                "company_name":   f"Test Corp {RUN_ID}",
                "business_type":  "retail",
                "contact_person": "Test Manager",
            })
            check(r, 201)
            step("1b. Create employer profile", True)
        except Exception as e:
            step("1b. Create employer profile", False, str(e))
            return _summary()

        # ── Step 2: Register Worker ───────────────────────────────────────
        wrk_token = ""
        try:
            r = api(c, "POST", "/auth/register", json={
                "email": WRK_EMAIL, "password": WRK_PASS, "role": "worker"
            })
            data = check(r, 201)
            wrk_token = data["access_token"]
            step("2a. Register worker", True, f"user_id={data['user_id'][:8]}…")
        except Exception as e:
            step("2a. Register worker", False, str(e))
            return _summary()

        # ── Step 2b: Create Worker Profile ───────────────────────────────
        try:
            r = api(c, "POST", "/workers/profile", token=wrk_token, json={
                "full_name":           f"Test Worker {RUN_ID}",
                "skills":              ["cleaning", "cooking"],
                "experience_years":    1,
                "daily_rate_expected": 400.0,
                "lat":  WORKER_LAT,
                "lng":  WORKER_LNG,
                "location_name":       "Siam, Bangkok",
            })
            check(r, 201)
            step("2b. Create worker profile", True)
        except Exception as e:
            step("2b. Create worker profile", False, str(e))
            return _summary()

        # ── Step 3: Employer Post Job ─────────────────────────────────────
        job_id         = ""
        has_work_hours = False
        try:
            base_payload = {
                "title":           f"Test Cleaning Job {RUN_ID}",
                "description":     "Lifecycle test job — safe to ignore",
                "required_skills": ["cleaning"],
                "daily_wage_rate": 500.0,
                "duration_days":   1,
                "slots_available": 1,
                "lat":             JOB_LAT,
                "lng":             JOB_LNG,
                "location_name":   "Siam Paragon, Bangkok",
            }
            # ลอง with work hours ก่อน
            r = api(c, "POST", "/jobs", token=emp_token, json={
                **base_payload, "work_start": _now_plus(0), "work_end": _now_plus(4), "ot_rate": 75.0
            })
            if r.status_code == 500:
                # migration 007 ยังไม่รัน — fallback ไม่ใส่ work hours
                r = api(c, "POST", "/jobs", token=emp_token, json=base_payload)
            else:
                has_work_hours = True

            data = check(r, 201)
            job_id = data["id"]
            hint = "work 09:00-17:00 OT ฿75/hr" if has_work_hours else "⚠️  no work_hours (migration 007 ยังไม่ได้รัน)"
            step("3. Employer post job", True, f"job_id={job_id[:8]}… | {hint}")
        except Exception as e:
            step("3. Employer post job", False, str(e))
            return _summary()

        # ── Step 4: Worker Apply ──────────────────────────────────────────
        app_id = ""
        try:
            r = api(c, "POST", f"/jobs/{job_id}/apply", token=wrk_token, json={
                "lat": WORKER_LAT,
                "lng": WORKER_LNG,
            })
            data = check(r, 201)
            app_id = data["application_id"]
            step("4. Worker apply", True,
                 f"app_id={app_id[:8]}… | score={data.get('match_score', '?'):.1f} | dist={data.get('distance_km', 0):.3f}km")
        except Exception as e:
            step("4. Worker apply", False, str(e))
            return _summary()

        # ── Step 5: Employer Hire ─────────────────────────────────────────
        try:
            r = api(c, "PATCH", f"/applications/{app_id}/decide", token=emp_token, json={
                "decision": "hired",
                "note":     "ยินดีต้อนรับ (test)",
            })
            data = check(r, 200)
            step("5. Employer hire worker", True,
                 f"status={data.get('status')} | contact={bool(data.get('contact'))}")
        except Exception as e:
            step("5. Employer hire worker", False, str(e))
            return _summary()

        # ── Step 6: Worker Checkin (GPS mock) ────────────────────────────
        try:
            r = api(c, "POST", f"/applications/{app_id}/checkin", token=wrk_token, json={
                "lat": WORKER_LAT,   # 0m จาก job → ผ่าน 150m check แน่นอน
                "lng": WORKER_LNG,
            })
            data = check(r, 200)
            dist = data.get("distance_m", "?")
            step("6. Worker checkin (GPS)", True,
                 f"status={data['status']} | distance={dist}m (threshold 150m)")
        except Exception as e:
            step("6. Worker checkin (GPS)", False, str(e))
            return _summary()

        # ── Step 7: Employer Start ────────────────────────────────────────
        # work_start = เวลาปัจจุบัน TH → ผ่าน ±30min check เสมอ
        try:
            r = api(c, "POST", f"/applications/{app_id}/start", token=emp_token)
            data = check(r, 200)
            step("7. Employer start work", True, f"status={data['status']}")
        except Exception as e:
            step("7. Employer start work", False, str(e))
            return _summary()

        # ── Step 8: Worker Complete ───────────────────────────────────────
        try:
            r = api(c, "POST", f"/applications/{app_id}/complete", token=wrk_token)
            data = check(r, 200)
            step("8. Worker complete", True, f"status={data['status']}")
        except Exception as e:
            step("8. Worker complete", False, str(e))
            return _summary()

        # ── Step 9: Employer Verify ───────────────────────────────────────
        try:
            r = api(c, "POST", f"/applications/{app_id}/verify", token=emp_token)
            data = check(r, 200)
            step("9. Employer verify", True, f"status={data['status']}")
        except Exception as e:
            step("9. Employer verify", False, str(e))

        # ── Step 10: Confirm final status via worker apps list ────────────
        try:
            r = api(c, "GET", "/workers/applications", token=wrk_token)
            apps = check(r, 200)
            match = next((a for a in apps if a["id"] == app_id), None)
            if match:
                final = match["status"]
                ok    = final == "verified"
                step("10. Confirm status = verified", ok, f"status={final}")
            else:
                step("10. Confirm status = verified", False, "application not found in list")
        except Exception as e:
            step("10. Confirm status = verified", False, str(e))

    return _summary()


def _summary() -> bool:
    passed = sum(1 for _, ok, _ in results if ok)
    total  = len(results)
    failed = [name for name, ok, _ in results if not ok]

    print(f"\n{'─'*60}")
    print(f"  Result: {passed}/{total} passed")
    if failed:
        print(f"  Failed steps:")
        for name in failed:
            detail = next(d for n, _, d in results if n == name)
            print(f"    • {name}")
            if detail:
                for line in detail.splitlines():
                    print(f"        {line}")
    else:
        print("  🎉  All steps passed!")
    print(f"{'─'*60}\n")
    return len(failed) == 0


# ─── Entry Point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WeHire lifecycle test")
    parser.add_argument("--url", default=DEFAULT_BASE, help="Base URL of backend")
    args = parser.parse_args()

    base = args.url.rstrip("/")
    ok   = run_tests(base)
    sys.exit(0 if ok else 1)

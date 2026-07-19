"""
QA smoke test: #1 Atomic slot claim (กัน slot oversell) บน production
รันบนเครื่อง: python qa_slot_race.py   (stdlib ล้วน ไม่ต้อง pip)

ทดสอบ 2 แบบ:
  Test A (sequential): job slot=1 → hire w1 (200) → hire w2 (ต้อง 409 "ที่นั่งเต็มแล้ว")
  Test B (concurrent): job slot=1 → ยิง hire w1 + w2 พร้อมกัน 2 thread
                       → ต้องได้ 200 หนึ่งราย + 409 หนึ่งราย เป๊ะ (พิสูจน์ atomic ไม่มี race window)

หลังเทสต์ลบ account ทดสอบแบบ best-effort (worker ที่ถูก hire ลบไม่ได้ = ปกติ ปล่อยไว้ได้)
"""
import time, random, json, sys, uuid
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

API = "https://we-re-hire.onrender.com"
LAT, LNG = 13.7563, 100.5018   # Bangkok
PW = "QaTest123!"

def phone():
    return "0" + "".join(random.choice("0123456789") for _ in range(9))

def req(method, path, token=None, jbody=None):
    url = API + path
    headers = {}
    data = None
    if token:
        headers["Authorization"] = "Bearer " + token
    if jbody is not None:
        data = json.dumps(jbody).encode()
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            body = resp.read().decode(errors="replace")
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:    return e.code, json.loads(body)
        except: return e.code, {"detail": body[:200]}

def mk_employer():
    ts = int(time.time()*1000) % 1000000
    em = f"qa_emp_{ts}_{random.randint(100,999)}@wehiretest.com"
    st, b = req("POST", "/auth/register", jbody={"email": em, "password": PW, "role": "employer", "phone": phone(), "terms_accepted": True})
    assert st == 201, f"emp register fail {st} {b}"
    tok = b["access_token"]
    st, b = req("POST", "/employers/profile", tok, {"company_name": "QA Co", "contact_person": "QA"})
    assert st in (200, 201), f"emp profile fail {st} {b}"
    return tok

def mk_worker(name):
    ts = int(time.time()*1000) % 1000000
    em = f"qa_wk_{ts}_{random.randint(100,999)}@wehiretest.com"
    st, b = req("POST", "/auth/register", jbody={"email": em, "password": PW, "role": "worker", "phone": phone(), "terms_accepted": True})
    assert st == 201, f"worker register fail {st} {b}"
    tok = b["access_token"]
    st, b = req("POST", "/workers/profile", tok, {"full_name": name, "skills": ["cleaning"], "experience_years": 1})
    assert st in (200, 201), f"worker profile fail {st} {b}"
    return tok

def post_job(emp_tok):
    st, b = req("POST", "/jobs", emp_tok, {
        "title": "QA Slot Test", "daily_wage_rate": 400, "duration_days": 1,
        "slots_available": 1, "lat": LAT, "lng": LNG, "location_name": "QA site",
    })
    assert st == 201, f"post job fail {st} {b}"
    return b["id"]

def apply(worker_tok, job_id):
    st, b = req("POST", f"/jobs/{job_id}/apply", worker_tok, {"lat": LAT, "lng": LNG})
    assert st == 201, f"apply fail {st} {b}"
    return b["application_id"]

def hire(emp_tok, app_id):
    return req("PATCH", f"/applications/{app_id}/decide", emp_tok, {"decision": "hired"})

def cleanup(tokens):
    for t in tokens:
        try: req("DELETE", "/users/me", t)
        except: pass

def main():
    print(f"[i] API={API}\n[i] setting up employer + 2 workers ...")
    emp = mk_employer()
    w1  = mk_worker("QA Worker 1")
    w2  = mk_worker("QA Worker 2")
    results_ok = True

    # ---- Test A: sequential ----
    print("\n=== Test A: sequential hire (slot=1) ===")
    job = post_job(emp)
    a1 = apply(w1, job)
    a2 = apply(w2, job)
    s1, b1 = hire(emp, a1)
    s2, b2 = hire(emp, a2)
    print(f"  hire w1 -> {s1} ({b1.get('new_status', b1.get('detail'))})")
    print(f"  hire w2 -> {s2} ({b2.get('new_status', b2.get('detail'))})")
    passA = (s1 == 200 and s2 == 409)
    print(f"  {'PASS' if passA else 'FAIL'} — expect w1=200, w2=409")
    results_ok &= passA

    # ---- Test B: concurrent race ----
    print("\n=== Test B: concurrent hire race (slot=1, 2 threads) ===")
    job2 = post_job(emp)
    b_a1 = apply(w1, job2)
    b_a2 = apply(w2, job2)
    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(hire, emp, b_a1)
        f2 = ex.submit(hire, emp, b_a2)
        (rs1, rb1), (rs2, rb2) = f1.result(), f2.result()
    codes = sorted([rs1, rs2])
    print(f"  concurrent results -> {rs1}, {rs2}")
    passB = (codes == [200, 409])
    print(f"  {'PASS' if passB else 'FAIL'} — expect exactly one 200 + one 409 (got {codes})")
    results_ok &= passB

    print("\n[i] cleanup test accounts (best-effort) ...")
    cleanup([emp, w1, w2])

    print("\n" + "=" * 54)
    print("ALL PASS - atomic slot claim กัน oversell ได้จริง" if results_ok
          else "SOME FAIL - ดูผลข้างบน (ถ้า w2 ได้ 200 = slot ยังขายเกิน)")
    print("=" * 54)
    sys.exit(0 if results_ok else 1)

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n[SETUP ERROR] {e}")
        sys.exit(2)

"""
QA Step 2: ทดสอบ /jobs/nearby scope=related|all + category adjacency บน production
รันหลัง deploy backend ใหม่: python qa_scope_adjacency.py   (stdlib ล้วน)

พิสูจน์:
  - สร้าง 2 งานหมวดเดียวกัน (warehouse) title ต่างกัน: jobA=titleA, jobB=titleB
  - worker1 มี skill = titleA
      scope=related -> เห็นทั้ง jobA (is_direct) และ jobB (adjacent, หมวดเดียวกัน)
  - worker2 มี skill หมวดอื่น (fnb)
      scope=related -> ไม่เห็น jobA/jobB   |   scope=all -> เห็น
ปิดท้าย: ปิดงานทดสอบ + ลบ account (best-effort)
"""
import time, random, json, sys
import urllib.request, urllib.error

API = "https://we-re-hire.onrender.com"
LAT, LNG = 13.7010, 100.6010   # จุดทดสอบ (แยกจากงานจริง)
PW = "QaTest123!"

def phone(): return "0" + "".join(random.choice("0123456789") for _ in range(9))

def req(method, path, token=None, jbody=None):
    url = API + path; headers = {}; data = None
    if token: headers["Authorization"] = "Bearer " + token
    if jbody is not None:
        data = json.dumps(jbody).encode(); headers["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            b = resp.read().decode(errors="replace")
            return resp.status, (json.loads(b) if b else None)
    except urllib.error.HTTPError as e:
        b = e.read().decode(errors="replace")
        try: return e.code, json.loads(b)
        except: return e.code, {"detail": b[:200]}

def titles_of(cat):
    st, t = req("GET", f"/job-categories/{cat}/titles")
    return [x["code"] for x in t] if st == 200 and t else []

def mk_worker(skill_code):
    ts = int(time.time()*1000) % 1000000
    st, b = req("POST", "/auth/register", jbody={"email": f"qa_sc_w_{ts}_{random.randint(1,999)}@wehiretest.com",
                "password": PW, "role": "worker", "phone": phone(), "terms_accepted": True})
    assert st == 201, f"worker reg {st} {b}"
    tok = b["access_token"]
    st, b = req("POST", "/workers/profile", tok, {"full_name": "QA W", "skills": [skill_code], "experience_years": 1})
    assert st in (200,201), f"worker profile {st} {b}"
    return tok

def nearby(tok, scope):
    st, b = req("GET", f"/jobs/nearby?lat={LAT}&lng={LNG}&radius_km=5&scope={scope}", tok)
    assert st == 200, f"nearby {st} {b}"
    return {j["job_id"]: j for j in b.get("jobs", [])}

def main():
    # --- pick codes ---
    wh = titles_of("warehouse")
    if len(wh) < 2:
        print(f"[!] warehouse มี title < 2 ({wh}) — ปรับ script ใช้หมวดอื่นที่มี >=2 title"); sys.exit(1)
    tA, tB = wh[0], wh[1]
    other = None
    for c in ("fnb", "cleaning", "event", "factory"):
        ts = titles_of(c)
        if ts: other = ts[0]; break
    if not other:
        print("[!] หา title หมวดอื่นไม่เจอ"); sys.exit(1)
    print(f"[i] warehouse titles: direct={tA}, adjacent={tB} | other-category skill={other}")

    # --- employer + 2 jobs ---
    ts = int(time.time())
    st, b = req("POST", "/auth/register", jbody={"email": f"qa_sc_e_{ts}@wehiretest.com",
                "password": PW, "role": "employer", "phone": phone(), "terms_accepted": True})
    assert st == 201, f"emp reg {st} {b}"; emp = b["access_token"]
    req("POST", "/employers/profile", emp, {"company_name": "QA Co", "contact_person": "QA"})
    def post(skill):
        st, b = req("POST", "/jobs", emp, {"title": f"QA {skill}", "daily_wage_rate": 500, "duration_days": 1,
                    "slots_available": 1, "lat": LAT, "lng": LNG, "required_skills": [skill]})
        assert st == 201, f"post job {st} {b}"; return b["id"]
    jobA, jobB = post(tA), post(tB)
    print(f"[i] jobA({tA})={jobA[:8]}  jobB({tB})={jobB[:8]}")

    ok = True
    # --- worker1 (skill=tA) ---
    w1 = mk_worker(tA)
    rel = nearby(w1, "related")
    a, bb = rel.get(jobA), rel.get(jobB)
    print("\n=== worker1 (skill=%s) scope=related ===" % tA)
    print(f"  jobA present={a is not None} is_direct={a and a['is_direct']} adjacent={a and a['adjacent']}")
    print(f"  jobB present={bb is not None} is_direct={bb and bb['is_direct']} adjacent={bb and bb['adjacent']}")
    t1 = (a and a["is_direct"] and not a["adjacent"]) and (bb and bb["adjacent"] and not bb["is_direct"])
    print(f"  {'PASS' if t1 else 'FAIL'} — expect jobA=direct, jobB=adjacent (หมวดเดียวกัน)")
    ok &= bool(t1)

    # --- worker2 (skill=other category) ---
    w2 = mk_worker(other)
    rel2 = nearby(w2, "related")
    all2 = nearby(w2, "all")
    print("\n=== worker2 (skill=%s, คนละหมวด) ===" % other)
    print(f"  scope=related: jobA present={jobA in rel2}  jobB present={jobB in rel2}  (ควรไม่เห็นทั้งคู่)")
    print(f"  scope=all:     jobA present={jobA in all2}  jobB present={jobB in all2}  (ควรเห็นทั้งคู่)")
    t2 = (jobA not in rel2 and jobB not in rel2) and (jobA in all2 and jobB in all2)
    print(f"  {'PASS' if t2 else 'FAIL'} — expect related=ไม่เห็น, all=เห็น")
    ok &= bool(t2)

    # --- cleanup best-effort ---
    for jid in (jobA, jobB):
        req("PATCH", f"/jobs/{jid}/status", emp, {"status": "closed"})
    for tok in (emp, w1, w2):
        req("DELETE", "/users/me", tok)

    print("\n" + "=" * 56)
    print("ALL PASS - scope + category adjacency ทำงานถูกต้อง" if ok
          else "SOME FAIL - ดูผลข้างบน")
    print("=" * 56)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    try: main()
    except AssertionError as e:
        print(f"\n[SETUP ERROR] {e}"); sys.exit(2)

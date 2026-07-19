"""
QA Step 1 spot-check: ตรวจว่า required_skills ของงานจริงบน production เก็บเป็น title code ที่ถูกต้อง
(เพื่อยืนยันว่า category-adjacency mapping ใช้ได้ ไม่มี free-text / code เก่าหลุด)

รันบนเครื่อง: python qa_skill_data_check.py   (stdlib ล้วน)

วิธี:
  1) register worker ทดสอบ (ไม่ใส่ skill) -> เห็นงานทุกงานในรัศมี
  2) ยิง /jobs/nearby หลายจุด (พื้นที่ pilot) -> รวม required_skills ของทุกงาน
     (worker ไม่มี skill => missing_skills = required_skills ทั้งหมดของงานนั้น)
  3) ดึง title code ที่ถูกต้องจาก /job-categories + /titles
  4) เทียบ -> รายงาน code ที่ orphan (ไม่อยู่ใน taxonomy)
  5) ลบ account ทดสอบ
"""
import time, random, json, sys
import urllib.request, urllib.error

API = "https://we-re-hire.onrender.com"
PW = "QaTest123!"
# จุดสำรวจครอบพื้นที่ pilot (ลาดกระบัง / ลำลูกกา / กลาง กทม.)
POINTS = [(13.7244, 100.7501), (13.9630, 100.7480), (13.7563, 100.5018)]

def phone():
    return "0" + "".join(random.choice("0123456789") for _ in range(9))

def req(method, path, token=None, jbody=None):
    url = API + path
    headers, data = {}, None
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

def main():
    # --- valid title codes จาก taxonomy จริง ---
    st, cats = req("GET", "/job-categories")
    if st != 200:
        print(f"[!] โหลด categories ไม่ได้: {st} {cats}"); sys.exit(1)
    valid = set()
    cat_of = {}   # title_code -> category_code (ไว้โชว์)
    for c in cats:
        st, titles = req("GET", f"/job-categories/{c['code']}/titles")
        if st == 200 and titles:
            for ti in titles:
                valid.add(ti["code"].lower())
                cat_of[ti["code"].lower()] = c["code"]
    print(f"[i] taxonomy จริง: {len(cats)} หมวด, {len(valid)} title codes")

    # --- register worker (ไม่มี skill) ---
    ts = int(time.time())
    em = f"qa_skillchk_{ts}@wehiretest.com"
    st, b = req("POST", "/auth/register", jbody={"email": em, "password": PW, "role": "worker", "phone": phone(), "terms_accepted": True})
    if st != 201:
        print(f"[!] register fail: {st} {b}"); sys.exit(1)
    tok = b["access_token"]

    # --- รวม required_skills ของทุกงานในหลายจุด ---
    used = {}   # code(lower) -> จำนวนงานที่ใช้
    total_jobs = 0
    seen_jobs = set()
    for (lat, lng) in POINTS:
        st, data = req("GET", f"/jobs/nearby?lat={lat}&lng={lng}&radius_km=30", tok)
        if st != 200 or not data:
            continue
        for j in data.get("jobs", []):
            jid = j.get("job_id")
            if jid in seen_jobs:
                continue
            seen_jobs.add(jid); total_jobs += 1
            # worker ไม่มี skill => missing_skills = required ทั้งหมด (title-cased) -> lower กลับ
            for s in (j.get("missing_skills") or []):
                code = str(s).lower()
                used[code] = used.get(code, 0) + 1

    # --- cleanup ---
    req("DELETE", "/users/me", tok)

    # --- report ---
    print(f"[i] สำรวจงาน (unique) = {total_jobs} งาน, required_skills distinct = {len(used)} code\n")
    orphans = {c: n for c, n in used.items() if c not in valid}
    print("required_skills ที่พบ:")
    for code, n in sorted(used.items(), key=lambda x: -x[1]):
        ok = code in valid
        tag = f"OK  (หมวด {cat_of.get(code,'?')})" if ok else "ORPHAN <-- ไม่อยู่ใน taxonomy"
        print(f"   {code:<22} x{n:<3} {tag}")

    print("\n" + "=" * 56)
    if not used:
        print("ไม่พบงานในพื้นที่สำรวจ — ลองเพิ่มจุด/รัศมี หรือยังไม่มีงาน open")
    elif orphans:
        print(f"พบ ORPHAN {len(orphans)} code: {', '.join(orphans)}")
        print("=> งานที่ใช้ code เหล่านี้จะไม่ได้ category-adjacency")
        print("   (จะโผล่แค่ 'direct match' หรือแท็บ 'ทั้งหมด' — ไม่ crash)")
    else:
        print("PASS - required_skills ทุกตัวเป็น title code ที่ถูกต้อง")
        print("       => category-adjacency ใช้ได้เต็มร้อย ไม่มี orphan")
    print("=" * 56)

if __name__ == "__main__":
    main()

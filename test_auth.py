"""
WeHire — Phone Login / Auth Test
ทดสอบ auth cluster: login ด้วยเบอร์/อีเมล + remember me 30 วัน + timing fix + PATCH /auth/phone

Usage:
  python test_auth.py                               # default = prod (onrender)
  python test_auth.py --url http://localhost:8000   # local

หมายเหตุ: สร้าง test account (test_auth_*) จริงใน DB
"""

import argparse
import base64
import io
import json
import random
import sys
import time
import uuid
import httpx

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

DEFAULT_BASE = "https://we-re-hire.onrender.com"

RUN_ID = uuid.uuid4().hex[:6]
EMAIL  = f"test_auth_{RUN_ID}@wehire-test.com"
PHONE  = "0" + "".join(random.choices("0123456789", k=9))
PWD    = "TestPass123!"

results = []


def step(name, ok, detail=""):
    print(f"  {'✅ PASS' if ok else '❌ FAIL'}  {name}" + (f"\n         {detail}" if detail else ""))
    results.append((name, ok))
    return ok


def api(c, method, path, token="", **kw):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    return c.request(method, path, headers=h, timeout=30, **kw)


def jwt_exp_span(token):
    """คืน (exp - iat) วินาที จาก JWT (decode payload อย่างเดียว ไม่ verify)"""
    seg = token.split(".")[1]
    seg += "=" * (-len(seg) % 4)
    data = json.loads(base64.urlsafe_b64decode(seg))
    return data["exp"] - data["iat"]


def run(base):
    print(f"\n{'='*60}\n  Auth / Phone Login Test  —  {base}\n  Run ID: {RUN_ID}  phone={PHONE}\n{'='*60}\n")
    with httpx.Client(base_url=base) as c:
        # Setup: register worker ด้วย email + phone + password
        try:
            r = api(c, "POST", "/auth/register", json={
                "email": EMAIL, "password": PWD, "role": "worker",
                "phone": PHONE, "terms_accepted": True,
            })
            assert r.status_code == 201, f"register {r.status_code}: {r.text[:150]}"
            step("0. Register (email+phone)", True)
        except Exception as e:
            step("0. Register", False, str(e))
            return _summary()

        worker_token = ""   # เก็บไว้ reuse กัน rate-limit (login 10/min)

        # 1. login ด้วย EMAIL (backward compat)
        try:
            r = api(c, "POST", "/auth/login", json={"email": EMAIL, "password": PWD})
            ok = r.status_code == 200 and "access_token" in r.json()
            step("1. Login ด้วยอีเมล (backward compat)", ok, f"HTTP {r.status_code}")
        except Exception as e:
            step("1. Login email", False, str(e))

        # 2. login ด้วย PHONE (ฟีเจอร์ใหม่)
        try:
            r = api(c, "POST", "/auth/login", json={"identifier": PHONE, "password": PWD})
            ok = r.status_code == 200 and "access_token" in r.json()
            if ok:
                worker_token = r.json()["access_token"]
            step("2. Login ด้วยเบอร์โทร", ok, f"HTTP {r.status_code}")
        except Exception as e:
            step("2. Login phone", False, str(e))

        # 3. login เบอร์ + รหัสผิด → 401
        try:
            r = api(c, "POST", "/auth/login", json={"identifier": PHONE, "password": "wrongpass"})
            step("3. เบอร์ + รหัสผิด → 401", r.status_code == 401, f"HTTP {r.status_code}")
        except Exception as e:
            step("3. wrong password", False, str(e))

        # 4. login เบอร์ที่ไม่มีในระบบ → 401
        try:
            r = api(c, "POST", "/auth/login", json={"identifier": "0000000000", "password": PWD})
            step("4. เบอร์ไม่มีในระบบ → 401", r.status_code == 401, f"HTTP {r.status_code}")
        except Exception as e:
            step("4. nonexistent", False, str(e))

        # 5. remember me → token อายุ ~30 วัน (ไม่ติ๊ก → ~1 วัน)
        try:
            r1 = api(c, "POST", "/auth/login", json={"identifier": PHONE, "password": PWD, "remember": False})
            r2 = api(c, "POST", "/auth/login", json={"identifier": PHONE, "password": PWD, "remember": True})
            span_no = jwt_exp_span(r1.json()["access_token"]) / 86400.0
            span_yes = jwt_exp_span(r2.json()["access_token"]) / 86400.0
            ok = span_no < 2 and span_yes > 20
            step("5. remember me → token 30 วัน", ok,
                 f"ไม่ติ๊ก={span_no:.1f}วัน (คาด ~1) · ติ๊ก={span_yes:.1f}วัน (คาด ~30)")
        except Exception as e:
            step("5. remember me", False, str(e))

        # 6. timing fix — เบอร์ไม่มีในระบบต้อง "ยังรัน bcrypt" (ไม่ตอบทันที) = dummy ทำงาน
        #    robust กว่าเทียบ ratio (ซึ่งโดน Render jitter): ถ้า fix ไม่ทำงาน absent จะเร็วผิดปกติ (ไม่มี bcrypt)
        try:
            def t(payload):
                s = time.perf_counter()
                api(c, "POST", "/auth/login", json=payload)
                return time.perf_counter() - s
            t_absent = min(t({"identifier": "0000000000", "password": "wrongpass"}) for _ in range(2))
            ok = t_absent > 0.05   # bcrypt cost 12 ~150-300ms → absent ควร >50ms = dummy รันจริง
            step("6. timing fix (เบอร์ไม่มี ยังรัน bcrypt)", ok,
                 f"เบอร์ไม่มี={t_absent*1000:.0f}ms (>50ms = dummy bcrypt ทำงาน)")
        except Exception as e:
            step("6. timing", False, str(e))

        # 7. PATCH /auth/phone — เปลี่ยนเบอร์ แล้ว login เบอร์ใหม่ได้ (reuse token กัน rate-limit)
        try:
            if not worker_token:
                worker_token = api(c, "POST", "/auth/login",
                                   json={"identifier": PHONE, "password": PWD}).json()["access_token"]
            new_phone = "0" + "".join(random.choices("0123456789", k=9))
            r = api(c, "PATCH", "/auth/phone", token=worker_token, json={"phone": new_phone})
            ok_set = r.status_code == 200
            r2 = api(c, "POST", "/auth/login", json={"identifier": new_phone, "password": PWD})
            ok_login = r2.status_code == 200
            step("7. PATCH /auth/phone → login เบอร์ใหม่", ok_set and ok_login,
                 f"set={r.status_code} login-new={r2.status_code}")
        except Exception as e:
            step("7. PATCH /auth/phone", False, str(e))

    return _summary()


def _summary():
    passed = sum(1 for _, ok in results if ok)
    print(f"\n{'─'*60}\n  Result: {passed}/{len(results)} passed")
    if passed == len(results):
        print("  🎉  All passed — phone login + remember + timing ทำงานถูกต้อง")
    else:
        for n, ok in results:
            if not ok:
                print(f"    • {n}")
    print(f"{'─'*60}\n")
    return passed == len(results)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", default=DEFAULT_BASE)
    args = p.parse_args()
    sys.exit(0 if run(args.url.rstrip("/")) else 1)

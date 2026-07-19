"""
QA: ทดสอบ Supabase Storage upload บน production (หลังเปลี่ยนเป็น apikey header)
รันบนเครื่องพี่ได้เลย ไม่ต้อง pip install อะไร (stdlib ล้วน):

    python qa_storage_upload.py

สคริปต์จะ:
  1) register worker ทดสอบใหม่ (throwaway) -> token
  2) create worker profile
  3) POST /workers/kyc/upload ด้วยรูป PNG dummy   <-- จุดที่เทสต์ _storage_upload/apikey
  4) ลบบัญชีทดสอบทิ้ง (soft-delete)

หมายเหตุ: KYC upload กับ employer แนบสลิป ใช้ _storage_upload/_storage_auth_headers
ตัวเดียวกัน => KYC upload ผ่าน = ครอบคลุมสลิป employer ด้วย
"""
import time, random, struct, zlib, json, sys, uuid
import urllib.request, urllib.error

API = "https://we-re-hire.onrender.com"
ts  = int(time.time())
EMAIL = f"qa_storage_{ts}@wehiretest.com"
PW    = "QaTest123!"
PHONE = "0" + "".join(random.choice("0123456789") for _ in range(9))


def tiny_png() -> bytes:
    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    sig  = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00"))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def req(method, path, token=None, jbody=None, multipart=None):
    url = API + path
    headers = {}
    data = None
    if token:
        headers["Authorization"] = "Bearer " + token
    if jbody is not None:
        data = json.dumps(jbody).encode()
        headers["Content-Type"] = "application/json"
    if multipart is not None:
        boundary = "----qa" + uuid.uuid4().hex
        buf = b""
        for name, (fname, content, ctype) in multipart.items():
            buf += f"--{boundary}\r\n".encode()
            buf += f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
            buf += f"Content-Type: {ctype}\r\n\r\n".encode()
            buf += content + b"\r\n"
        buf += f"--{boundary}--\r\n".encode()
        data = buf
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, resp.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")


def main():
    png = tiny_png()
    print(f"[i] API={API}")
    print(f"[i] test worker: {EMAIL} / phone {PHONE}\n")

    # 1) register
    st, body = req("POST", "/auth/register", jbody={
        "email": EMAIL, "password": PW, "role": "worker",
        "phone": PHONE, "terms_accepted": True,
    })
    print(f"[1] register -> {st}")
    if st != 201:
        print("    FAIL:", body[:300]); sys.exit(1)
    token = json.loads(body)["access_token"]

    # 2) create worker profile
    st, body = req("POST", "/workers/profile", token=token, jbody={
        "full_name": "QA Storage Test", "skills": ["cleaning"], "experience_years": 1,
    })
    print(f"[2] create profile -> {st}")
    if st not in (200, 201):
        print("    warn:", body[:300])

    # 3) KYC upload — เทสต์ _storage_upload (apikey header)
    st, body = req("POST", "/workers/kyc/upload", token=token, multipart={
        "face_photo":    ("face.png",    png, "image/png"),
        "id_card_photo": ("id_card.png", png, "image/png"),
    })
    print(f"[3] KYC upload -> {st}")
    print("    body:", body[:400])
    upload_ok = (st == 200)

    # 4) cleanup
    st, _ = req("DELETE", "/users/me", token=token)
    print(f"[4] cleanup delete test acct -> {st}")

    print("\n" + "=" * 52)
    if upload_ok:
        print("PASS - Storage upload (apikey header) ทำงานบน production")
        print("      ครอบคลุม employer แนบสลิปด้วย (โค้ด _storage_upload ตัวเดียวกัน)")
    else:
        print("FAIL - upload ไม่ผ่าน ดู body ข้างบน")
        print("      เช็ค: ตั้ง SUPABASE_SECRET_KEY ใน Render + redeploy แล้วหรือยัง")
    print("=" * 52)
    sys.exit(0 if upload_ok else 1)


if __name__ == "__main__":
    main()

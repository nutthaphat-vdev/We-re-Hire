"""
WeHire backend smoke checks — stdlib only (urllib), no pip deps required.
Run: python bridge/smoke_check.py
"""

import json
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://web-production-1db39.up.railway.app"
TIMEOUT = 5  # seconds


def check_health():
    """GET /health — expect HTTP 200."""
    url = f"{BASE_URL}/health"
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            latency_ms = (time.monotonic() - t0) * 1000
            ok = resp.status == 200
            return ok, latency_ms, resp.status
    except urllib.error.HTTPError as exc:
        latency_ms = (time.monotonic() - t0) * 1000
        return False, latency_ms, exc.code
    except Exception as exc:
        latency_ms = (time.monotonic() - t0) * 1000
        return False, latency_ms, str(exc)


def check_zones():
    """GET /zones — expect HTTP 200 and a non-empty list."""
    url = f"{BASE_URL}/zones"
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            latency_ms = (time.monotonic() - t0) * 1000
            if resp.status != 200:
                return False, latency_ms, 0
            body = json.loads(resp.read().decode())
            zones = body if isinstance(body, list) else body.get("zones", body.get("data", []))
            count = len(zones) if isinstance(zones, list) else 0
            return count > 0, latency_ms, count
    except urllib.error.HTTPError as exc:
        latency_ms = (time.monotonic() - t0) * 1000
        return False, latency_ms, 0
    except Exception as exc:
        latency_ms = (time.monotonic() - t0) * 1000
        return False, latency_ms, 0


def main():
    results = []

    ok, ms, detail = check_health()
    label = "PASS" if ok else "FAIL"
    print(f"[{label}] /health  — {ms:.0f}ms  (status={detail})")
    results.append(ok)

    ok, ms, count = check_zones()
    label = "PASS" if ok else "FAIL"
    print(f"[{label}] /zones   — {ms:.0f}ms  (zones={count})")
    results.append(ok)

    print()
    if all(results):
        print("✓ All checks passed.")
    else:
        failed = results.count(False)
        print(f"✗ {failed}/{len(results)} check(s) FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()

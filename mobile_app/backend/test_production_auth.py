import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8080"

def post_json(endpoint, payload, token=None):
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            body = json.loads(body)
        except Exception:
            pass
        return e.code, body

print("==================================================")
print("     SHARK SENTINEL PRODUCTION SECURITY SUITE     ")
print("==================================================")

# Test 1: Wrong PIN
status, res = post_json("/api/auth/login", {"pin": "0000"})
print(f"[TEST 1] Wrong PIN '0000' -> Status: {status} (Expected 401)")
assert status == 401, f"Expected 401, got {status}"

# Test 2: Correct PIN
status, res = post_json("/api/auth/login", {"pin": "7777"})
print(f"[TEST 2] Correct PIN '7777' -> Status: {status} (Expected 200)")
assert status == 200, f"Expected 200, got {status}"
token = res.get("token")
print(f"         Issued Session Token: {token[:12]}... (Length: {len(token)})")

# Test 3: Protected Mutation without Token
status, res = post_json("/api/algos/toggle", {"magic": 24024, "enabled": False})
print(f"[TEST 3] Protected Endpoint without Token -> Status: {status} (Expected 401)")
assert status == 401, f"Expected 401, got {status}"

# Test 4: Protected Mutation with Valid Token
status, res = post_json("/api/algos/toggle", {"magic": 24024, "enabled": True}, token=token)
print(f"[TEST 4] Protected Endpoint with Token -> Status: {status} (Expected 200)")
assert status == 200, f"Expected 200, got {status}"

# Test 5: News Settings Update with Token
status, res = post_json("/api/news/settings", {"enabled": True, "block_before_min": 35, "block_after_min": 20}, token=token)
print(f"[TEST 5] News Settings with Token -> Status: {status} (Expected 200)")
assert status == 200, f"Expected 200, got {status}"

print("\n==================================================")
print("   ALL PRODUCTION SECURITY TESTS PASSED 100%!     ")
print("==================================================")

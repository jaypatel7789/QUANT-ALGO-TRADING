import urllib.request
import json

endpoints = [
    'http://127.0.0.1:8080/',
    'http://127.0.0.1:8080/css/style.css',
    'http://127.0.0.1:8080/js/app.js',
    'http://127.0.0.1:8080/manifest.json',
    'http://127.0.0.1:8080/service-worker.js',
    'http://127.0.0.1:8080/api/account',
    'http://127.0.0.1:8080/api/positions',
    'http://127.0.0.1:8080/api/algos',
    'http://127.0.0.1:8080/api/chart',
    'http://127.0.0.1:8080/api/news',
    'http://127.0.0.1:8080/api/system',
    'http://127.0.0.1:8080/api/history'
]

print("=== TESTING SHARK MT5 SENTINEL ENDPOINTS ===")
for ep in endpoints:
    try:
        req = urllib.request.Request(ep)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read()
            print(f"[OK] {ep:38} | Status: {response.status} | Size: {len(data)} bytes")
    except Exception as e:
        print(f"[ERR] {ep:38} | Error: {e}")

print("=== ALL SUITE CHECKS COMPLETED ===")

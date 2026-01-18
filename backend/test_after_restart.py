import requests
import json

print("=" * 60)
print("TESTING CUSTOM BOYFRIEND ENDPOINTS")
print("=" * 60)

# Test 1: List custom boyfriends
print("\n[Test 1] GET /3d/boyfriends/custom")
r = requests.get('http://localhost:8000/3d/boyfriends/custom')
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("[PASS] Endpoint found!")
    print(f"Response: {r.json()}")
else:
    print(f"[FAIL] Endpoint not found: {r.text}")

# Test 2: Check OpenAPI spec
print("\n[Test 2] Checking OpenAPI spec...")
r = requests.get('http://localhost:8000/openapi.json')
spec = r.json()
custom_endpoints = [p for p in spec['paths'].keys() if 'custom' in p]
print(f"Custom boyfriend endpoints in spec: {len(custom_endpoints)}")
for endpoint in custom_endpoints:
    print(f"  - {endpoint}")

if len(custom_endpoints) >= 4:
    print("[PASS] All 4 custom boyfriend endpoints registered!")
else:
    print(f"[FAIL] Only {len(custom_endpoints)}/4 endpoints found")

# Test 3: Check /3d/ root
print("\n[Test 3] GET /3d/")
r = requests.get('http://localhost:8000/3d/')
info = r.json()
print(f"Service: {info.get('service')}")
print(f"Endpoints listed: {list(info.get('endpoints', {}).keys())}")

print("\n" + "=" * 60)
if len(custom_endpoints) >= 4:
    print("SUCCESS! Custom boyfriend generator is ready!")
else:
    print("FAILED! Server needs restart.")
print("=" * 60)

#!/usr/bin/env python
import requests

try:
    r = requests.get('http://localhost:8000/3d/boyfriends/custom')
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        print('SUCCESS! Custom boyfriend endpoint is working!')
        print('Response:', r.json())
    else:
        print('FAIL: Endpoint still not found')
        print('Response:', r.text)
except Exception as e:
    print(f'ERROR: Could not connect to server: {e}')
    print('Make sure the backend server is running on localhost:8000')
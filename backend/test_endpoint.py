import requests
import time

time.sleep(3)

r = requests.get('http://localhost:8000/3d/boyfriends/custom')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    print(f'Response: {r.json()}')
    print('\n✓ Custom boyfriend endpoints are working!')
else:
    print(f'Response: {r.text}')
    print('\n✗ Still getting 404')

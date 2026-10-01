# test_api.py
import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
})

# جستجوی نماد "فولاد"
url = "https://cdn.tsetmc.com/api/Instrument/GetInstrumentSearch/فولاد"
r = session.get(url, timeout=15)

print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"✅ اتصال برقراره")
    print(f"نتیجه: {data}")
else:
    print(f"❌ خطا: {r.text[:200]}")

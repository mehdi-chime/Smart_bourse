# test_connection.py
# تست اتصال به TSETMC
# اجرا: python test_connection.py

import os
import sys
import socket

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

import requests

print()
print("=" * 80)
print("  TEST CONNECTION")
print("=" * 80)
print()

# ۱. تست DNS
print("  1. DNS Test:")
try:
    ip = socket.gethostbyname("old.tsetmc.com")
    print(f"     OK: old.tsetmc.com → {ip}")
except Exception as e:
    print(f"     ERR: {e}")
print()

# ۲. تست HTTP
print("  2. HTTP Test:")
try:
    r = requests.get("https://old.tsetmc.com", timeout=10)
    print(f"     OK: status {r.status_code}")
except Exception as e:
    print(f"     ERR: {e}")
print()

# ۳. تست سایت دیگه
print("  3. Other Site Test:")
try:
    r = requests.get("https://www.google.com", timeout=10)
    print(f"     OK: google.com status {r.status_code}")
except Exception as e:
    print(f"     ERR: {e}")
print()

# ۴. تست TSETMC جدید
print("  4. New TSETMC:")
try:
    r = requests.get("https://www.tsetmc.com", timeout=10)
    print(f"     OK: status {r.status_code}")
except Exception as e:
    print(f"     ERR: {e}")
print()

print("=" * 80)
print()

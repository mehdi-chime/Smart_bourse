# find_pn_sh.py
# پیدا کردن شپنا و شتران با روش‌های مختلف
# اجرا: python find_pn_sh.py

import os
import sys
from pathlib import Path

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def normalize(s):
    if not s:
        return s
    return (str(s)
            .replace("\u0643", "\u06a9")
            .replace("\u064a", "\u06cc")
            .replace("\u0649", "\u06cc")
            .replace("\u0629", "\u0647")
            .replace("\u0640", "")
            .replace(" ", "")
            .strip())


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 پیدا کردن شپنا و شتران")
    safe_print("=" * 80)
    safe_print("")

    # دریافت داده
    df = att.get_live_market()
    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print(f"  📊 {len(df)} سهم")
    safe_print("")

    # لیست جستجو
    search_terms = [
        "شپنا", "شتران",
        "پالایش", "پالايش",
        "نفت", "اصفهان", "تهران",
        "PNES", "PTEH",
    ]

    for term in search_terms:
        safe_print(f"  🔍 جستجو: {term}")
        count = 0

        for _, row in df.iterrows():
            symbol = str(row.get("Symbol", ""))
            name = str(row.get("Name", ""))
            ins_code = str(row.get("InsCode") or "")

            if (normalize(term) in normalize(symbol) or
                normalize(term) in normalize(name)):
                safe_print(f"     ✅ {symbol}")
                safe_print(f"        Name: {name}")
                safe_print(f"        InsCode: {ins_code}")
                count += 1
                if count >= 10:
                    break

        if count == 0:
            safe_print(f"     ❌ پیدا نشد")
        safe_print("")

    # جستجوی گسترده
    safe_print("  🔍 جستجوی گسترده (نمادهای خاص):")

    # الف) نمادهای شروع با "شپ"
    safe_print("  الف) نمادهای با 'شپ':")
    count = 0
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if symbol.startswith("شپ"):
            safe_print(f"     {symbol} | {row.get('Name')} | {row.get('InsCode')}")
            count += 1
            if count >= 15:
                break
    safe_print("")

    # ب) نمادهای شروع با "شت"
    safe_print("  ب) نمادهای با 'شت':")
    count = 0
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if symbol.startswith("شت"):
            safe_print(f"     {symbol} | {row.get('Name')} | {row.get('InsCode')}")
            count += 1
            if count >= 15:
                break
    safe_print("")

    # ج) INS Codeهای معروف
    safe_print("  ج) INS Codeهای معروف پالایشگاه:")
    known_codes = {
        "شپنا": "7745894403636165",   # ← احتمالاً
        "شتران": "35366681030756042",  # ← احتمالاً
    }

    for name, code in known_codes.items():
        found = False
        for _, row in df.iterrows():
            if str(row.get("InsCode")) == code:
                safe_print(f"     ✅ {name}: {row.get('Symbol')} | {row.get('Name')}")
                found = True
                break

        if not found:
            safe_print(f"     ❌ {name} ({code})")
    safe_print("")

    safe_print("=" * 80)


if __name__ == "__main__":
    main()

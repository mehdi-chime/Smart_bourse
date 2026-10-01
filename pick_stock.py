# pick_stock.py
# جستجو و انتخاب سهم
# اجرا: python pick_stock.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

SYMBOLS_FILE = PROJECT_ROOT / "data" / "all_symbols.json"


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
            .strip())


def load_symbols():
    if not SYMBOLS_FILE.exists():
        return []
    try:
        with open(SYMBOLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("symbols", [])
    except:
        return []


def search(query, symbols, limit=30):
    if not query:
        return []

    q = normalize(query).lower()
    results = []

    for s in symbols:
        sym = normalize(s.get("symbol", "")).lower()
        name = normalize(s.get("name", "")).lower()
        inscode = str(s.get("inscode", ""))

        # جستجو
        if q in sym or q in name or q == inscode:
            results.append(s)
            if len(results) >= limit:
                break

    return results


def show_results(results, query):
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  🔍 نتایج جستجو برای: {query}")
    safe_print(f"  📊 {len(results)} نتیجه")
    safe_print("=" * 80)
    safe_print("")

    for i, s in enumerate(results, 1):
        sym = s.get("symbol", "")
        name = s.get("name", "")[:45]
        safe_print(f"  {i:>3}. {sym:<15} | {name}")

    safe_print("")


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  🎯 Smart_Bourse - Pick Stock")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # لود
    symbols = load_symbols()

    if not symbols:
        safe_print("  ❌ فایل all_symbols.json نیست!")
        safe_print("  اجرا کن: python fetch_all_symbols.py")
        safe_print("")
        return

    safe_print(f"  ✅ {len(symbols)} سهم لود شد")
    safe_print("")
    safe_print("  راهنما:")
    safe_print("   - نام سهم رو تایپ کن (فارسی/انگلیسی)")
    safe_print("   - یا InsCode")
    safe_print("   - 'q' برای خروج")
    safe_print("")

    while True:
        safe_print("=" * 80)

        try:
            query = input("  🔍 جستجو: ").strip()
        except KeyboardInterrupt:
            safe_print("\n  خروج...")
            break

        if query.lower() == "q":
            safe_print("  خروج...")
            break

        if not query:
            continue

        # جستجو
        results = search(query, symbols, limit=30)

        if not results:
            safe_print(f"  ❌ '{query}' پیدا نشد")
            safe_print("")
            continue

        show_results(results, query)

        # انتخاب
        safe_print(f"  کدوم؟ (1-{len(results)}) یا Enter: ", end="")
        pick = input().strip()

        if not pick:
            continue

        if pick.isdigit():
            idx = int(pick)
            if 1 <= idx <= len(results):
                selected = results[idx - 1]
                safe_print("")
                safe_print("=" * 80)
                safe_print(f"  ✅ انتخاب: {selected.get('symbol', '')}")
                safe_print("=" * 80)
                safe_print("")
                safe_print(f"  📌 نام: {selected.get('name', '')}")
                safe_print(f"  🔢 InsCode: {selected.get('inscode', '')}")
                safe_print(f"  🏭 صنعت: {selected.get('sector', '')}")
                safe_print(f"  💰 EPS: {selected.get('eps', 0):,.0f}")
                safe_print(f"  📊 سهام: {selected.get('shares', 0):,.0f}")
                safe_print("")

                # ذخیره
                output = PROJECT_ROOT / "data" / "selected_stock.json"
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(selected, f, ensure_ascii=False, indent=2)

                safe_print(f"  💾 ذخیره: {output}")
                safe_print("")
                safe_print("  حالا می‌تونی تحلیل کنی:")
                safe_print(f"     python analyze_stock.py")
                safe_print("")
                break
        else:
            safe_print("  ❌ نامعتبر")


if __name__ == "__main__":
    main()

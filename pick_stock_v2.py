# pick_stock_v2.py
# جستجو با InsCode یا شماره
# اجرا: python pick_stock_v2.py

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


def save_selected(s):
    output = PROJECT_ROOT / "data" / "selected_stock.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
    return output


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  🎯 Pick Stock v2")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    symbols = load_symbols()

    if not symbols:
        safe_print("  ❌ all_symbols.json نیست!")
        safe_print("")
        return

    safe_print(f"  ✅ {len(symbols)} سهم لود شد")
    safe_print("")
    safe_print("  راهنما:")
    safe_print("   - InsCode رو وارد کن (مثلاً 48990026850202503)")
    safe_print("   - یا 'q' برای خروج")
    safe_print("")

    while True:
        safe_print("=" * 80)
        safe_print("")

        try:
            query = input("  🔍 InsCode یا نام (Finglish): ").strip()
        except KeyboardInterrupt:
            break

        if query.lower() == "q":
            break

        if not query:
            continue

        # جستجو
        results = []

        # با InsCode
        if query.isdigit() and len(query) > 5:
            for s in symbols:
                if str(s.get("inscode", "")) == query:
                    results.append(s)

        # یا با نام (Finglish)
        else:
            q = query.lower()
            for s in symbols:
                sym = normalize(s.get("symbol", "")).lower()
                name = normalize(s.get("name", "")).lower()
                if q in sym or q in name:
                    results.append(s)
                    if len(results) >= 20:
                        break

        if not results:
            safe_print(f"  ❌ پیدا نشد")
            safe_print("")
            continue

        safe_print("")
        safe_print(f"  ✅ {len(results)} نتیجه:")
        safe_print("")
        for i, s in enumerate(results, 1):
            sym = s.get("symbol", "")
            name = s.get("name", "")[:40]
            ins = s.get("inscode", "")
            safe_print(f"  {i:>3}. {sym:<12} | {name}")
            safe_print(f"       InsCode: {ins}")

        safe_print("")
        safe_print("  شماره (1-{}) یا InsCode: ".format(len(results)), end="")
        pick = input().strip()

        if not pick:
            continue

        # اگه شماره
        if pick.isdigit() and int(pick) <= len(results):
            idx = int(pick)
            selected = results[idx - 1]
        else:
            # اگه InsCode
            selected = None
            for s in results:
                if str(s.get("inscode", "")) == pick:
                    selected = s
                    break

        if selected:
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

            output = save_selected(selected)
            safe_print(f"  💾 ذخیره: {output}")
            safe_print("")
            safe_print("  حالا تحلیل کن:")
            safe_print("     python analyze_stock_v2.py")
            safe_print("")
            break
        else:
            safe_print("  ❌ نامعتبر")


if __name__ == "__main__":
    main()

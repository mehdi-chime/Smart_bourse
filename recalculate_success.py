# recalculate_success.py
# بازمحاسبه success
# اجرا: python recalculate_success.py

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
OUTCOMES_FILE = PROJECT_ROOT / "data" / "ai" / "outcomes.jsonl"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔄 بازمحاسبه success")
    safe_print("=" * 80)
    safe_print("")

    if not OUTCOMES_FILE.exists():
        safe_print(f"  ❌ {OUTCOMES_FILE} پیدا نشد!")
        return

    # بکاپ
    backup = OUTCOMES_FILE.with_suffix(".jsonl.bak")
    backup.write_text(OUTCOMES_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    safe_print(f"  📦 بکاپ: {backup.name}")
    safe_print("")

    # خوندن
    outcomes = []
    with open(OUTCOMES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                outcomes.append(json.loads(line))
            except:
                pass

    safe_print(f"  📊 {len(outcomes)} نتیجه")
    safe_print("")

    # بازمحاسبه
    updated = 0
    THRESHOLD = 1.0

    for o in outcomes:
        price_at = o.get("price_at_signal")
        if not price_at or price_at <= 0:
            continue

        best_price = None
        for key in ["price_after_7d", "price_after_3d", "price_after_1d"]:
            p = o.get(key)
            if p and p > 0:
                best_price = p
                break

        if not best_price:
            continue

        change_pct = (best_price - price_at) / price_at * 100

        cat = o.get("category", "")
        if cat == "SAFE_BUY":
            new_success = change_pct > THRESHOLD
        elif cat == "SAFE_SELL":
            new_success = change_pct < -THRESHOLD
        else:
            continue

        old_success = o.get("success")
        if old_success != new_success:
            o["success"] = new_success
            o["old_success"] = old_success
            o["change_pct"] = round(change_pct, 2)
            updated += 1

    safe_print(f"  ✅ {updated} نتیجه آپدیت شد")
    safe_print("")

    # ذخیره
    with open(OUTCOMES_FILE, "w", encoding="utf-8") as f:
        for o in outcomes:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    safe_print(f"  💾 ذخیره: {OUTCOMES_FILE}")
    safe_print("")

    # آمار
    success = sum(1 for o in outcomes if o.get("success"))
    fail = sum(1 for o in outcomes if o.get("success") is False)

    safe_print(f"  📊 موفق: {success}")
    safe_print(f"  📊 ناموفق: {fail}")
    if success + fail > 0:
        safe_print(f"  🎯 نرخ: {success/(success+fail)*100:.1f}%")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()

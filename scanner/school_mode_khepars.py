# school_mode_khepars.py
# چک خودکار خپارس برای فردا
# اجرا: python school_mode_khepars.py

import sys
from pathlib import Path
from datetime import datetime
PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

SYMBOL = "خپارس"


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


def send_eitaa(text):
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
        import requests
        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=15)
        return r.status_code == 200
    except:
        return False


def main():
    print()
    print("=" * 80)
    print(f"  📊 چک خپارس - حالت خودکار")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ❌ خطا")
        return

    found = None
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if "خپارس" in symbol or "خپارس" in normalize(symbol):
            found = row
            break

    if found is None:
        print("  ❌ خپارس پیدا نشد")
        return

    last = float(found.get("Last") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

    print(f"  Last: {int(last):,}")
    print(f"  کف:   {int(min_a):,}")
    print(f"  سقف:  {int(max_a):,}")
    print()

    # چک: آیا -3% شد؟
    if last <= min_a:
        print("  🟢 الآن ≤ کف! بخر!")
        msg = f"🟢 خپارس - فرصت خرید!\n\n"
        msg += f"قیمت: {int(last):,}\n"
        msg += f"کف: {int(min_a):,}\n"
        msg += f"سقف: {int(max_a):,}\n"
        msg += f"حقوقی: {int(vol_buy_n):,} vs {int(vol_sell_n):,}\n"
        msg += f"\n🟢 سفارش خرید: {int(min_a):,}\n"
        msg += f"🔴 سفارش فروش: {int(max_a):,}\n"
        msg += f"⛔ حد ضرر: {int(min_a * 0.98):,}"
        send_eitaa(msg)
    else:
        diff = ((last - min_a) / min_a) * 100
        print(f"  ⏳ {diff:.2f}% بالاتر از کف")
        print(f"  💡 صبر کن...")

    print()
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

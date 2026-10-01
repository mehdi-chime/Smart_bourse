# check_aap_now.py
# چک آپ با P/E و EPS
# اجرا: python check_aap_now.py

import os
import sys
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

import algotik_tse as att

SYMBOL = "آپ"


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


def main():
    print()
    print("=" * 90)
    print(f"  Check {SYMBOL} (P/E + EPS)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ERR")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    found = None
    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if normalize(symbol) == normalize(SYMBOL):
            found = row
            break

    if found is None:
        print(f"  {SYMBOL} NOT FOUND")
        return

    print(f"  {SYMBOL}")
    print(f"     Name: {found.get('Name', '?')}")
    print()

    # قیمت‌ها
    print(f"  Gheymat:")
    for col in ["Last", "Close", "Yesterday", "MinAllowed", "MaxAllowed",
                "ChangePct", "EPS"]:
        try:
            val = found.get(col)
            print(f"     {col:15}: {val}")
        except:
            pass
    print()

    # محاسبات
    last = float(found.get("Last") or 0)
    eps = float(found.get("EPS") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    yesterday = float(found.get("Yesterday") or 0)

    print(f"  Mohasebat:")
    print(f"     Last:      {int(last):,}")
    print(f"     Yesterday: {int(yesterday):,}")
    print(f"     Kaf:       {int(min_a):,}")
    print(f"     Saghf:     {int(max_a):,}")
    print(f"     EPS:       {int(eps):,}")
    print()

    # P/E
    if eps > 0:
        pe = last / eps
        print(f"  P/E Analysis:")
        print(f"     P/E = {int(last):,} / {int(eps):,} = {pe:.2f}")
        print()

        if pe < 5:
            print(f"     ✅ P/E kheili khoob (< 5)")
        elif pe < 10:
            print(f"     ✅ P/E khoob (5-10)")
        elif pe < 15:
            print(f"     ✅ P/E monaseb (10-15)")
        elif pe < 25:
            print(f"     🟡 P/E bala (15-25)")
        else:
            print(f"     ❌ P/E kheili bala (> 25)")
    else:
        print(f"  P/E Analysis:")
        print(f"     ❌ EPS manfi ya sefr!")
        print(f"     → Sherkat ziyan dahande!")
        print(f"     → NAZAN!")
    print()

    # شناوری
    shares = float(found.get("SharesOutstanding") or 0)
    base_vol = float(found.get("BaseVolume") or 0)

    print(f"  Shenavari:")
    print(f"     Total Shares: {int(shares):,}")
    print(f"     Base Volume:  {int(base_vol):,}")
    if shares > 0 and base_vol > 0:
        float_pct = (base_vol / shares) * 100
        print(f"     Shenavari:    {float_pct:.1f}%")
        if float_pct > 50:
            print(f"     ✅ Shenavari khoob")
        elif float_pct > 30:
            print(f"     ✅ Shenavari monaseb")
        elif float_pct > 20:
            print(f"     🟡 Shenavari ghabele ghobool")
        else:
            print(f"     ⚠️ Shenavari paeen (poran)")
    print()

    # حقوقی/حقیقی
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)
    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)

    print(f"  Hoqoqi/Haghighi:")
    print(f"     Hoqoqi: Kharid={int(vol_buy_n):,} | Foroosh={int(vol_sell_n):,}")
    print(f"     Haghighi: Kharid={int(vol_buy):,} | Foroosh={int(vol_sell):,}")
    print()

    print("=" * 90)
    print()


if __name__ == "__main__":
    main()

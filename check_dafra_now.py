# check_dafra_now.py
# چک دقیق دفرا
# اجرا: python check_dafra_now.py

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

SYMBOL = "دفرا"


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
    print(f"  Check {SYMBOL}")
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
    for col in ["Last", "Close", "Yesterday", "PreviousClose",
                "Open", "FirstPrice", "High", "Low",
                "MinAllowed", "MaxAllowed", "ChangePct", "EPS"]:
        try:
            val = found.get(col)
            print(f"     {col:15}: {val}")
        except:
            pass
    print()

    # سفارشات
    print(f"  Sefareshat:")
    for col in ["Vol_buy_retail", "Vol_sell_retail",
                "Vol_buy_institutional", "Vol_sell_institutional"]:
        try:
            val = found.get(col)
            print(f"     {col:25}: {val}")
        except:
            pass
    print()

    # Order Book
    print(f"  Order Book:")
    for i in range(1, 4):
        bid_p = found.get(f"BidPrice{i}")
        bid_v = found.get(f"BidVolume{i}")
        ask_p = found.get(f"AskPrice{i}")
        ask_v = found.get(f"AskVolume{i}")
        print(f"     L{i}: BID {bid_p} ({bid_v}) | ASK {ask_p} ({ask_v})")
    print()

    # محاسبات
    last = float(found.get("Last") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    eps = float(found.get("EPS") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)
    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)

    if last > 0:
        print(f"  Mohasebat:")
        print(f"     Last:       {int(last):,}")
        print(f"     Yesterday:  {int(yesterday):,}")
        print(f"     Kaf:        {int(min_a):,}")
        print(f"     Saghf:      {int(max_a):,}")
        print()

        if eps > 0:
            pe = last / eps
            print(f"     EPS:        {int(eps):,}")
            print(f"     P/E:        {pe:.2f}")
            print()

        if min_a > 0:
            distance = (last - min_a) / min_a * 100
            print(f"     Fosel az kaf:  {distance:.2f}%")
        if max_a > 0:
            distance = (max_a - last) / last * 100
            print(f"     Fosel az saghf: {distance:.2f}%")
        print()

    # تحلیل
    print(f"  Tahlil:")
    if last == max_a:
        print(f"     SAFE KHARID! (Last = saghf)")
    elif last == min_a:
        print(f"     SAFE FOROOSH! (Last = kaf)")
    else:
        print(f"     motadel")
    print()

    if vol_buy_n > vol_sell_n:
        print(f"     HOQOQI KHARIDAR")
        print(f"        Kharid: {int(vol_buy_n):,}")
        print(f"        Foroosh: {int(vol_sell_n):,}")
        if vol_sell_n > 0:
            print(f"        Nesbat: {vol_buy_n/vol_sell_n:.1f}x")
    elif vol_sell_n > vol_buy_n:
        print(f"     HOQOQI FOROOSHANDE")
    else:
        print(f"     HOQOQI MOTADEL")
    print()

    if vol_buy > vol_sell:
        print(f"     HAGHIGHI KHARIDAR ({int(vol_buy):,} vs {int(vol_sell):,})")
    else:
        print(f"     HAGHIGHI FOROOSHANDE ({int(vol_buy):,} vs {int(vol_sell):,})")
    print()

    # استراتژی
    print(f"  Estrategi:")
    print(f"     KHARID:    {int(min_a):,}")
    print(f"     FOROOSH:   {int(max_a):,}")
    print(f"     HAD-ZARAR: {int(min_a * 0.98):,}")
    if min_a > 0 and max_a > 0:
        profit = (max_a / min_a - 1) * 100 - 1.25
        print(f"     SOOD:      {profit:.2f}%")
    print()

    print("=" * 90)
    print()


if __name__ == "__main__":
    main()

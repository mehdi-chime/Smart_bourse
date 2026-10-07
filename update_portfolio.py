# update_portfolio.py
# رصد پرتفوی + سود/ضرر
# اجرا: python update_portfolio.py

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

import algotik_tse as att

PORTFOLIO_FILE = PROJECT_ROOT / "data" / "my_portfolio.json"


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


def load_portfolio():
    if PORTFOLIO_FILE.exists():
        try:
            return json.loads(PORTFOLIO_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  📊 رصد پرتفوی")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    portfolio = load_portfolio()
    if not portfolio:
        safe_print("  ⚠️ پرتفوی خالیه!")
        return

    safe_print(f"  📊 {len(portfolio)} سهم")
    safe_print("")

    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print(f"     ✅ {len(df)} سهم")
    safe_print("")

    safe_print("=" * 100)
    safe_print("  📊 جدول پرتفوی")
    safe_print("=" * 100)
    safe_print("")
    safe_print(f"  {'نماد':<15} | {'خرید':>10} | {'فعلی':>10} | {'سود٪':>7} | {'سود تومان':>15}")
    safe_print("  " + "-" * 80)

    total_profit = 0
    total_investment = 0

    for pos in portfolio:
        symbol = pos["symbol"]
        buy_price = pos["buy_price"]
        qty = pos["quantity"]

        found = None
        for _, row in df.iterrows():
            live_symbol = str(row.get("Symbol", ""))
            if normalize(symbol) == normalize(live_symbol):
                found = row
                break

        if found is None:
            continue

        last = float(found.get("Last") or found.get("Close") or 0)
        profit = (last - buy_price) * qty
        profit_pct = (last - buy_price) / buy_price * 100 if buy_price > 0 else 0

        total_profit += profit
        total_investment += buy_price * qty

        emoji = "🟢" if profit > 0 else "🔴"
        safe_print(
            f"  {symbol[:15]:<15} | "
            f"{int(buy_price):>10,} | "
            f"{int(last):>10,} | "
            f"{profit_pct:>+6.2f}% | "
            f"{emoji} {int(profit):>+12,}"
        )

    safe_print("")
    safe_print(f"  💰 کل سرمایه: {int(total_investment):,} تومان")
    safe_print(f"  💰 سود/ضرر: {int(total_profit):+,} تومان")

    if total_investment > 0:
        total_pct = total_profit / total_investment * 100
        safe_print(f"  📊 درصد: {total_pct:+.2f}%")

    safe_print("")
    safe_print("=" * 100)


if __name__ == "__main__":
    main()

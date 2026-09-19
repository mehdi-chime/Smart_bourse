
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


HOLDINGS = [
    {"user_name": "تابان", "aliases": ["تابان"], "qty": 3697},
    {"user_name": "پکویر", "aliases": ["پكوير", "پکویر"], "qty": 23518},
    {"user_name": "سمهریز", "aliases": ["سهرمز", "سمهریز"], "qty": 5350},
    {"user_name": "احیا", "aliases": ["احیا"], "qty": 49122},
    {"user_name": "پیزد", "aliases": ["پیزد"], "qty": 23220},
    {"user_name": "خپارس", "aliases": ["خپارس"], "qty": 217948},
    {"user_name": "فولاد", "aliases": ["فولاد"], "qty": 431948},
]


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


def find_symbol(df, aliases):
    for alias in aliases:
        target = normalize(alias)
        for _, row in df.iterrows():
            if normalize(row.get("Symbol", "")) == target:
                return row
    for alias in aliases:
        target = normalize(alias)
        for _, row in df.iterrows():
            if normalize(row.get("Symbol", "")).startswith(target):
                return row
    return None


def main():
    print()
    print("=" * 110)
    print("  Smart_Bourse Live Portfolio")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 110)

    df = att.get_live_market()
    if df is None or df.empty:
        print("no data")
        return

    df_full = df.copy()

    total_value = 0
    found_count = 0

    print()
    header = "  " + "symbol".ljust(12) + " | "
    header += "qty".rjust(10) + " | "
    header += "price".rjust(10) + " | "
    header += "change".rjust(8) + " | "
    header += "value (M rials)".rjust(16) + " | status"
    print(header)
    print("  " + "-" * 106)

    for h in HOLDINGS:
        r = find_symbol(df_full, h["aliases"])

        if r is None:
            print("  " + h["user_name"].ljust(12) + " | NOT FOUND")
            continue

        found_count += 1
        symbol = str(r.get("Symbol", h["user_name"]))
        price = float(r.get("Last") or r.get("Close") or 0)
        change = float(r.get("ChangePct") or 0)
        value = price * h["qty"]
        total_value += value

        buy_q = float(r.get("BuyQueueVolume") or 0)
        sell_q = float(r.get("SellQueueVolume") or 0)
        market_state = str(r.get("market_state") or "")
        state_title = str(r.get("marketStateTitle") or r.get("state_title") or "")
        is_today = r.get("is_today_trade_date")

        # تشخیص وضعیت
        status = ""
        if buy_q > 0 and sell_q == 0:
            status = "BUY QUEUE"
        elif sell_q > 0 and buy_q == 0:
            status = "SELL QUEUE"

        if market_state == "F" or state_title == "بسته" or is_today == False:
            status = "CLOSED (halted)"

        print(
            "  " + symbol.ljust(12)
            + " | " + "{:,}".format(h["qty"]).rjust(10)
            + " | " + "{:,}".format(int(price)).rjust(10)
            + " | " + "{:+.2f}%".format(change).rjust(8)
            + " | " + "{:,.1f}".format(value / 1_000_000).rjust(16)
            + " | " + status
        )

    print("  " + "-" * 106)
    print()
    print("  Found: " + str(found_count) + " / " + str(len(HOLDINGS)))
    print()
    print("  Total value (M rials): " + "{:,.1f}".format(total_value / 1_000_000))
    print("  Total value (M toman): " + "{:,.0f}".format(total_value / 10_000_000))
    print()
    print("=" * 110)


if __name__ == "__main__":
    main()

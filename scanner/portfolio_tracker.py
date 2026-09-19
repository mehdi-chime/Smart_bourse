
import sys
import json
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

DATA_DIR = PROJECT_ROOT / "data" / "portfolio_history"
DATA_DIR.mkdir(parents=True, exist_ok=True)


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
    print("=" * 90)
    print("  Portfolio Tracker - Save to History")
    print("=" * 90)

    df = att.get_live_market()
    if df is None or df.empty:
        print("no data")
        return

    total_value = 0
    holdings_data = []

    for h in HOLDINGS:
        r = find_symbol(df, h["aliases"])
        if r is None:
            continue

        symbol = str(r.get("Symbol", h["user_name"]))
        price = float(r.get("Last") or r.get("Close") or 0)
        change = float(r.get("ChangePct") or 0)
        value = price * h["qty"]
        total_value += value

        buy_q = float(r.get("BuyQueueVolume") or 0)
        sell_q = float(r.get("SellQueueVolume") or 0)

        status = ""
        if buy_q > 0 and sell_q == 0:
            status = "BUY_QUEUE"
        elif sell_q > 0 and buy_q == 0:
            status = "SELL_QUEUE"

        holdings_data.append({
            "symbol": symbol,
            "user_name": h["user_name"],
            "qty": h["qty"],
            "price": price,
            "change_pct": round(change, 2),
            "value": value,
            "status": status,
        })

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "timestamp": datetime.now().isoformat(),
        "total_value_rials": total_value,
        "total_value_m_rials": round(total_value / 1_000_000, 1),
        "total_value_m_toman": round(total_value / 10_000_000, 0),
        "holdings": holdings_data,
    }

    # ذخیره به فایل
    today = datetime.now().strftime("%Y-%m-%d")
    history_file = DATA_DIR / (today + ".jsonl")
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")

    # خلاصه
    print()
    print("  Date: " + snapshot["date"] + " " + snapshot["time"])
    print("  Holdings: " + str(len(holdings_data)) + " / " + str(len(HOLDINGS)))
    print("  Total: " + "{:,.1f}".format(snapshot["total_value_m_rials"]) + " M rials")
    print("  Total: " + "{:,.0f}".format(snapshot["total_value_m_toman"]) + " M toman")
    print()
    print("  Saved to: " + str(history_file))
    print()
    print("=" * 90)


if __name__ == "__main__":
    main()

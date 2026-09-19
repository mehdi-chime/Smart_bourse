
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

RECORDS_DIR = PROJECT_ROOT / "data" / "live_records"


def analyze_symbol(symbol, date_str):
    file = RECORDS_DIR / date_str / (symbol + ".jsonl")
    if not file.exists():
        return None

    records = []
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except Exception:
                pass

    if not records:
        return None

    prices = [r["price"] for r in records]
    buy_queues = [r.get("buy_queue", 0) for r in records]
    sell_queues = [r.get("sell_queue", 0) for r in records]
    real_ratios = [r.get("real_ratio", 0) for r in records]

    first = prices[0]
    last = prices[-1]
    high = max(prices)
    low = min(prices)

    return {
        "symbol": symbol,
        "records": len(records),
        "first": first,
        "last": last,
        "high": high,
        "low": low,
        "change_pct": round((last - first) / first * 100, 2) if first > 0 else 0,
        "max_buy_queue": max(buy_queues) if buy_queues else 0,
        "max_sell_queue": max(sell_queues) if sell_queues else 0,
        "avg_real_ratio": round(sum(real_ratios) / len(real_ratios), 2) if real_ratios else 0,
    }


def main():
    if len(sys.argv) < 2:
        date_str = datetime.now().strftime("%Y-%m-%d")
    else:
        date_str = sys.argv[1]

    print()
    print("=" * 90)
    print("  Live Records Analyzer - " + date_str)
    print("=" * 90)

    today_dir = RECORDS_DIR / date_str
    if not today_dir.exists():
        print()
        print("  No records for this date: " + str(today_dir))
        return

    print()
    print("   " + "symbol".ljust(12) + " | " + "records".rjust(7) + " | " + "first".rjust(10) + " | " + "last".rjust(10) + " | " + "high".rjust(10) + " | " + "low".rjust(10) + " | " + "change".rjust(8) + " | " + "max buy q".rjust(15) + " | " + "max sell q".rjust(15))
    print("   " + "-" * 130)

    for file in sorted(today_dir.glob("*.jsonl")):
        symbol = file.stem
        r = analyze_symbol(symbol, date_str)
        if not r:
            continue

        print(
            "   " + r["symbol"].ljust(12)
            + " | " + str(r["records"]).rjust(7)
            + " | " + "{:,}".format(int(r["first"])).rjust(10)
            + " | " + "{:,}".format(int(r["last"])).rjust(10)
            + " | " + "{:,}".format(int(r["high"])).rjust(10)
            + " | " + "{:,}".format(int(r["low"])).rjust(10)
            + " | " + "{:+.2f}%".format(r["change_pct"]).rjust(8)
            + " | " + "{:,}".format(int(r["max_buy_queue"])).rjust(15)
            + " | " + "{:,}".format(int(r["max_sell_queue"])).rjust(15)
        )

    print()
    print("=" * 90)


if __name__ == "__main__":
    main()

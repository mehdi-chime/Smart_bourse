
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

SYMBOLS = ["خگستر", "فولاد", "خودرو", "خساپا", "شستا", "وکغدیر", "نوری"]

SCENARIOS = [
    ("A", -2.0, -2.0),
    ("B", -3.0, -3.0),
    ("C", -4.0, -4.0),
    ("D", -5.0, -5.0),
    ("E", -3.0, -5.0),
    ("F", -2.0, -4.0),
]

INITIAL_SHARES = 1000
COMMISSION_PCT = 1.25
MAX_WAIT_DAYS = 10


def simulate(prices, sell_drop, buy_drop):
    shares = INITIAL_SHARES
    cash = 0.0
    state = "HOLDING"
    last_price = prices[0]
    num_trades = 0
    days_waiting = 0

    for i in range(1, len(prices)):
        price = prices[i]

        if state == "HOLDING":
            drop = (price - last_price) / last_price * 100
            if drop <= sell_drop:
                cash = shares * price * (1 - COMMISSION_PCT / 100)
                shares = 0
                state = "CASH"
                last_price = price
                num_trades += 1
                days_waiting = 0
            else:
                if price > last_price:
                    last_price = price
        elif state == "CASH":
            days_waiting += 1
            drop = (price - last_price) / last_price * 100
            if drop <= buy_drop or days_waiting >= MAX_WAIT_DAYS:
                shares = cash / (price * (1 + COMMISSION_PCT / 100))
                cash = 0
                state = "HOLDING"
                last_price = price
                num_trades += 1

    final_value = shares * prices[-1] + cash
    initial_value = INITIAL_SHARES * prices[0]

    return {
        "final_shares": int(shares),
        "share_change": int(shares) - INITIAL_SHARES,
        "value_change_pct": (final_value - initial_value) / initial_value * 100,
        "num_trades": num_trades,
    }


def analyze(name):
    print()
    print("=" * 85)
    print("  " + name)
    print("=" * 85)

    try:
        df = att.get_history(name)
    except Exception as e:
        print("   error: " + str(e)[:50])
        return None

    if df is None or df.empty:
        print("   no data")
        return None

    all_prices = df["Close"].tolist()
    prices = all_prices[-250:] if len(all_prices) > 250 else all_prices

    if len(prices) < 60:
        print("   not enough data")
        return None

    last_price = prices[-1]
    change_1y = (prices[-1] - prices[0]) / prices[0] * 100

    print()
    print("   price now      : " + "{:,}".format(int(last_price)))
    print("   change 1y      : " + "{:+.2f}%".format(change_1y))
    print("   days           : " + str(len(prices)))
    print()
    print("   " + "-" * 82)
    print("   scenario | sell  | buy   | trades | final shares | share chg | value chg")
    print("   " + "-" * 82)

    results = []
    for sname, sell_d, buy_d in SCENARIOS:
        r = simulate(prices, sell_d, buy_d)
        results.append((sname, sell_d, buy_d, r))

        sign = "+" if r["value_change_pct"] > 0 else ""
        share_sign = "+" if r["share_change"] >= 0 else ""

        line = "   " + sname.ljust(8)
        line += " | " + (str(sell_d) + "%").rjust(6)
        line += " | " + (str(buy_d) + "%").rjust(6)
        line += " | " + str(r["num_trades"]).rjust(6)
        line += " | " + "{:,}".format(r["final_shares"]).rjust(12)
        line += " | " + (share_sign + "{:,}".format(r["share_change"])).rjust(9)
        line += " | " + sign + "{:.2f}%".format(r["value_change_pct"]).rjust(9)
        print(line)

    best = max(results, key=lambda x: x[3]["share_change"])
    print()
    print("   BEST: " + best[0])
    print("   shares change: " + ("+" if best[3]["share_change"] >= 0 else "") + "{:,}".format(best[3]["share_change"]))
    return best


if __name__ == "__main__":
    print()
    print("Accumulation Simulator - last 1 year (commission 1.25%)")
    print()

    for name in SYMBOLS:
        try:
            analyze(name)
        except Exception as e:
            print("   error: " + str(e)[:60])

    print()
    print("=" * 85)

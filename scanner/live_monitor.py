
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

WATCH_SYMBOLS = ["فولاد", "خگستر", "پکویر", "خپارس", "خودرو", "شستا", "وکغدیر", "نوری"]
REFRESH_SECONDS = 15


def clear_screen():
    print("\n" * 2)


def get_market_breadth():
    try:
        df = att.get_live_market()
        if df is None or df.empty:
            return None
        if "InstrumentType" in df.columns:
            stocks = df[df["InstrumentType"] == 300]
        else:
            stocks = df
        changes = stocks["ChangePct"].dropna()
        return {
            "up": int((changes > 0).sum()),
            "down": int((changes < 0).sum()),
            "avg": round(float(changes.mean()), 2),
            "df": stocks,
        }
    except Exception:
        return None


def show_row(symbol, df):
    row = df[df["Symbol"] == symbol]
    if row.empty:
        return None

    r = row.iloc[0]
    price = float(r.get("Last") or r.get("Close") or 0)
    change = float(r.get("ChangePct") or 0)
    bid_vol = float(r.get("BidVolume1") or 0)
    ask_vol = float(r.get("AskVolume1") or 0)
    buy_queue = float(r.get("BuyQueueVolume") or 0)
    sell_queue = float(r.get("SellQueueVolume") or 0)
    vol_buy = float(r.get("Vol_buy_retail") or 0)
    vol_sell = float(r.get("Vol_sell_retail") or 0)

    if vol_sell > 0:
        ratio = vol_buy / vol_sell
    elif vol_buy > 0:
        ratio = 9999
    else:
        ratio = 0

    # سیگنال
    signal = ""
    if sell_queue > 0 and buy_queue == 0:
        signal = "SELL QUEUE"
    elif buy_queue > 0 and sell_queue == 0:
        signal = "BUY QUEUE"
    elif ratio > 5:
        signal = "STRONG BUY"
    elif ratio < 0.3:
        signal = "STRONG SELL"

    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "buy_queue": buy_queue,
        "sell_queue": sell_queue,
        "vol_buy": vol_buy,
        "vol_sell": vol_sell,
        "ratio": ratio,
        "signal": signal,
        "bid_vol": bid_vol,
        "ask_vol": ask_vol,
    }


def format_vol(v):
    if v >= 1_000_000_000:
        return "{:.1f}B".format(v / 1_000_000_000)
    if v >= 1_000_000:
        return "{:.1f}M".format(v / 1_000_000)
    if v >= 1_000:
        return "{:.1f}K".format(v / 1_000)
    return str(int(v))


def main():
    print()
    print("=" * 110)
    print("  Smart_Bourse Live Monitor")
    print("=" * 110)
    print("  Press Ctrl+C to stop")
    print()

    try:
        while True:
            now = datetime.now().strftime("%H:%M:%S")

            breadth = get_market_breadth()
            if breadth is None:
                print("[" + now + "] no data")
                time.sleep(REFRESH_SECONDS)
                continue

            df = breadth["df"]

            print()
            print("=" * 110)
            print("  Live Monitor - " + now + "  |  Market: " + str(breadth["up"]) + " up / " + str(breadth["down"]) + " down / avg " + str(breadth["avg"]) + "%")
            print("=" * 110)
            print()

            header = "  " + "symbol".ljust(10) + " | "
            header += "price".rjust(8) + " | "
            header += "change".rjust(8) + " | "
            header += "buy_q".rjust(10) + " | "
            header += "sell_q".rjust(10) + " | "
            header += "ratio".rjust(7) + " | "
            header += "signal"
            print(header)
            print("  " + "-" * 106)

            for symbol in WATCH_SYMBOLS:
                data = show_row(symbol, df)
                if not data:
                    continue

                line = "  " + symbol.ljust(10) + " | "
                line += "{:,}".format(int(data["price"])).rjust(8) + " | "
                line += "{:+.2f}%".format(data["change"]).rjust(8) + " | "
                line += format_vol(data["buy_queue"]).rjust(10) + " | "
                line += format_vol(data["sell_queue"]).rjust(10) + " | "
                line += "{:.2f}".format(data["ratio"]).rjust(7) + " | "
                line += data["signal"]
                print(line)

            print()
            print("  " + "-" * 106)
            print("  Legend: BUY QUEUE = buy only | SELL QUEUE = sell only")
            print("          STRONG BUY = real_ratio > 5 | STRONG SELL = real_ratio < 0.3")
            print()
            print("  Refreshing in " + str(REFRESH_SECONDS) + "s... (Ctrl+C to stop)")

            time.sleep(REFRESH_SECONDS)

    except KeyboardInterrupt:
        print()
        print("=" * 110)
        print("  Stopped.")
        print("=" * 110)
        print()


if __name__ == "__main__":
    main()

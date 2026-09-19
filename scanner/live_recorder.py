
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import json


WATCH_SYMBOLS = ["خگستر", "فولاد", "خودرو", "خساپا", "شستا", "وکغدیر", "نوری"]
INTERVAL_SECONDS = 30
SAVE_DIR = PROJECT_ROOT / "data" / "live_records"


def get_today_dir():
    today = datetime.now().strftime("%Y-%m-%d")
    d = SAVE_DIR / today
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_record(symbol, record):
    today_dir = get_today_dir()
    file = today_dir / (symbol + ".jsonl")
    with open(file, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def fetch_snapshot():
    try:
        df = att.get_live_market()
        if df is None or df.empty:
            return None
        if "InstrumentType" in df.columns:
            df = df[df["InstrumentType"] == 300]
        return df
    except Exception as e:
        print("   error: " + str(e)[:60])
        return None


def record_once():
    now = datetime.now().strftime("%H:%M:%S")
    df = fetch_snapshot()
    if df is None:
        print("   [" + now + "] no data")
        return

    saved = 0
    for symbol in WATCH_SYMBOLS:
        row = df[df["Symbol"] == symbol]
        if row.empty:
            continue

        row = row.iloc[0]
        price = float(row.get("Last") or row.get("Close") or 0)
        change = float(row.get("ChangePct") or 0)

        bid_vol = float(row.get("BidVolume1") or 0)
        ask_vol = float(row.get("AskVolume1") or 0)
        bid_price = float(row.get("BidPrice1") or 0)
        ask_price = float(row.get("AskPrice1") or 0)

        # صف خرید و فروش
        buy_queue = float(row.get("BuyQueueVolume") or 0)
        sell_queue = float(row.get("SellQueueVolume") or 0)

        # خرید/فروش حقیقی
        vol_buy_retail = float(row.get("Vol_buy_retail") or 0)
        vol_sell_retail = float(row.get("Vol_sell_retail") or 0)

        if vol_sell_retail > 0:
            real_ratio = vol_buy_retail / vol_sell_retail
        elif vol_buy_retail > 0:
            real_ratio = 9999
        else:
            real_ratio = 0

        record = {
            "time": now,
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "change_pct": round(change, 2),
            "bid_vol": bid_vol,
            "ask_vol": ask_vol,
            "bid_price": bid_price,
            "ask_price": ask_price,
            "buy_queue": buy_queue,
            "sell_queue": sell_queue,
            "vol_buy_retail": vol_buy_retail,
            "vol_sell_retail": vol_sell_retail,
            "real_ratio": round(real_ratio, 2),
        }

        save_record(symbol, record)
        saved += 1

    print("   [" + now + "] saved: " + str(saved) + " symbols")


def is_market_hours():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    # 8:45 تا 12:30
    if hour == 8 and minute >= 45:
        return True
    if 9 <= hour < 12:
        return True
    if hour == 12 and minute <= 30:
        return True
    return False


def main():
    print()
    print("=" * 75)
    print("  Live Recorder - Smart_Bourse")
    print("=" * 75)
    print()
    print("  symbols      : " + ", ".join(WATCH_SYMBOLS))
    print("  interval     : " + str(INTERVAL_SECONDS) + " seconds")
    print("  save dir     : " + str(SAVE_DIR))
    print()
    print("  Press Ctrl+C to stop")
    print()

    count = 0
    while True:
        try:
            now_str = datetime.now().strftime("%H:%M:%S")

            if is_market_hours():
                record_once()
                count += 1
            else:
                print("   [" + now_str + "] market closed - waiting...")

            time.sleep(INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print()
            print("=" * 75)
            print("  Stopped. Total records: " + str(count))
            print("=" * 75)
            break
        except Exception as e:
            print("   error: " + str(e)[:80])
            time.sleep(10)


if __name__ == "__main__":
    main()

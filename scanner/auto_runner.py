
import sys
import time
import json
import os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att

WATCH_SYMBOLS = ["خگستر", "فولاد", "خودرو", "خساپا", "شستا", "وکغدیر", "نوری"]
INTERVAL_SECONDS = 30
SAVE_DIR = PROJECT_ROOT / "data" / "live_records"
LOG_DIR = PROJECT_ROOT / "logs"
LOCK_FILE = PROJECT_ROOT / "data" / "auto_runner.lock"


def log(msg):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / ("auto_runner_" + datetime.now().strftime("%Y-%m-%d") + ".log")
    line = "[" + datetime.now().strftime("%H:%M:%S") + "] " + msg
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def check_lock():
    if LOCK_FILE.exists():
        try:
            age = time.time() - LOCK_FILE.stat().st_mtime
            if age < 120:
                log("already running (lock age " + str(int(age)) + "s) - exiting")
                return False
        except Exception:
            pass
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def update_lock():
    try:
        LOCK_FILE.write_text(str(os.getpid()))
    except Exception:
        pass


def release_lock():
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def is_weekend():
    wd = datetime.now().weekday()
    # Iran market days: Sat=5, Sun=6, Mon=0, Tue=1, Wed=2
    return wd not in [5, 6, 0, 1, 2]


def is_market_time():
    now = datetime.now()
    h = now.hour
    m = now.minute
    # 8:45 تا 12:30
    if h < 8:
        return False
    if h == 8 and m < 45:
        return False
    if h > 12:
        return False
    if h == 12 and m > 30:
        return False
    return True


def wait_until_market():
    while True:
        now = datetime.now()
        h = now.hour
        m = now.minute
        if h == 8 and m < 45:
            secs = (45 - m) * 60
            log("waiting " + str(secs) + "s until 8:45")
            time.sleep(min(secs, 60))
            continue
        if h < 8:
            log("too early - waiting 60s")
            time.sleep(60)
            continue
        return True


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
        log("fetch error: " + str(e)[:60])
        return None


def record_once():
    df = fetch_snapshot()
    if df is None:
        return 0

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
        buy_queue = float(row.get("BuyQueueVolume") or 0)
        sell_queue = float(row.get("SellQueueVolume") or 0)
        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)

        if vol_sell > 0:
            real_ratio = vol_buy / vol_sell
        elif vol_buy > 0:
            real_ratio = 9999
        else:
            real_ratio = 0

        record = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "change_pct": round(change, 2),
            "bid_vol": bid_vol,
            "ask_vol": ask_vol,
            "buy_queue": buy_queue,
            "sell_queue": sell_queue,
            "vol_buy_retail": vol_buy,
            "vol_sell_retail": vol_sell,
            "real_ratio": round(real_ratio, 2),
        }

        save_record(symbol, record)
        saved += 1

    return saved


def main():
    log("=" * 50)
    log("Auto Runner started")

    if is_weekend():
        log("weekend - exiting")
        return

    now = datetime.now()
    if now.hour > 12 or (now.hour == 12 and now.minute > 30):
        log("after market hours - exiting")
        return

    if not check_lock():
        return

    try:
        if now.hour < 8 or (now.hour == 8 and now.minute < 45):
            log("before 8:45 - will wait")
            wait_until_market()

        count = 0
        while is_market_time():
            saved = record_once()
            if saved > 0:
                count += 1
                if count % 10 == 0:
                    log("saved " + str(count) + " snapshots")
            update_lock()
            time.sleep(INTERVAL_SECONDS)

        log("market closed - exiting. total: " + str(count))
    except KeyboardInterrupt:
        log("stopped by user")
    except Exception as e:
        log("error: " + str(e)[:80])
    finally:
        release_lock()


if __name__ == "__main__":
    main()

# Smart_Bourse
# TAL Monitor - TSETMC Market Watch
# File: monitors/tal_monitor.py

import json
import time
from datetime import datetime, time as dt_time
from pathlib import Path

import requests


# ============================================================
# SETTINGS
# ============================================================

TAL_START = dt_time(12, 45)
TAL_END = dt_time(13, 0)

INTERVAL = 5

API_URL = "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketWatch"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports" / "tal"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.tsetmc.com/",
}


# ============================================================
# TIME
# ============================================================

def now_time():
    return datetime.now().time()


def is_tal_time():
    current = now_time()
    return TAL_START <= current < TAL_END


# ============================================================
# MARKET WATCH
# ============================================================

def get_market_watch():
    try:
        response = requests.get(
            API_URL,
            headers=HEADERS,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return data

    except requests.RequestException as e:
        print(f"\n❌ خطا در دریافت Market Watch: {e}")
        return None

    except ValueError as e:
        print(f"\n❌ پاسخ TSETMC قابل تبدیل به JSON نیست: {e}")
        return None


# ============================================================
# PARSE
# ============================================================

def get_value(item, *keys):
    for key in keys:
        if key in item and item[key] is not None:
            return item[key]

    return None


def parse_market_watch(data):

    if not data:
        return []

    rows = []

    market_data = None

    if isinstance(data, dict):

        for key in [
            "marketwatch",
            "marketWatch",
            "marketWatchData",
            "data"
        ]:

            if key in data:
                market_data = data[key]
                break

    elif isinstance(data, list):
        market_data = data

    if not market_data:
        return []

    for item in market_data:

        if not isinstance(item, dict):
            continue

        symbol = get_value(
            item,
            "lVal18AFC",
            "l18",
            "symbol",
            "Symbol"
        )

        if not symbol:
            continue

        last_price = get_value(
            item,
            "pDrCotVal",
            "pl",
            "lastPrice"
        )

        close_price = get_value(
            item,
            "pClosing",
            "pc",
            "closePrice"
        )

        trades = get_value(
            item,
            "zTotTran",
            "z",
            "trades"
        )

        volume = get_value(
            item,
            "qTotTran5J",
            "tvol",
            "volume"
        )

        value = get_value(
            item,
            "qTotCap",
            "tval",
            "value"
        )

        trade_time = get_value(
            item,
            "heven",
            "time",
            "tradeTime"
        )

        row = {
            "symbol": symbol,
            "last_price": last_price,
            "close_price": close_price,
            "trades": trades,
            "volume": volume,
            "value": value,
            "trade_time": trade_time,
            "timestamp": datetime.now().isoformat()
        }

        rows.append(row)

    return rows


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(rows):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = REPORT_DIR / f"tal_{timestamp}.json"

    report = {
        "project": "Smart_Bourse",
        "monitor": "TAL",
        "timestamp": datetime.now().isoformat(),
        "count": len(rows),
        "data": rows
    }

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2
        )

    return filename


# ============================================================
# DISPLAY
# ============================================================

def show_market(rows):

    print("\n")
    print("=" * 100)
    print(
        f"TAL MARKET WATCH | "
        f"{datetime.now():%H:%M:%S}"
    )
    print("=" * 100)

    if not rows:

        print("⚠️ اطلاعاتی از Market Watch دریافت نشد.")
        return

    # مرتب‌سازی بر اساس ارزش معاملات
    def value_number(row):

        try:
            return float(row["value"] or 0)
        except:
            return 0

    rows_sorted = sorted(
        rows,
        key=value_number,
        reverse=True
    )

    print(
        f"{'نماد':<15}"
        f"{'آخرین':<15}"
        f"{'پایانی':<15}"
        f"{'تعداد':<12}"
        f"{'حجم':<15}"
        f"{'ارزش':<18}"
    )

    print("-" * 100)

    for row in rows_sorted[:30]:

        print(
            f"{str(row['symbol']):<15}"
            f"{str(row['last_price']):<15}"
            f"{str(row['close_price']):<15}"
            f"{str(row['trades']):<12}"
            f"{str(row['volume']):<15}"
            f"{str(row['value']):<18}"
        )

    print("-" * 100)

    print(
        f"تعداد رکوردهای دریافت‌شده: {len(rows)}"
    )


# ============================================================
# MAIN MONITOR
# ============================================================

def monitor():

    print("=" * 70)
    print("Smart_Bourse | REAL TAL MONITOR")
    print("=" * 70)

    print(
        f"شروع TAL: {TAL_START.strftime('%H:%M')}"
    )

    print(
        f"پایان TAL: {TAL_END.strftime('%H:%M')}"
    )

    print(
        f"فاصله دریافت اطلاعات: {INTERVAL} ثانیه"
    )

    print("=" * 70)

    while True:

        current = datetime.now()

        if current.time() < TAL_START:

            remaining_seconds = (
                datetime.combine(
                    current.date(),
                    TAL_START
                ) - current
            ).total_seconds()

            remaining_minutes = int(
                remaining_seconds // 60
            )

            print(
                f"\r⏳ زمان فعلی: "
                f"{current:%H:%M:%S} | "
                f"شروع TAL حدود "
                f"{remaining_minutes} دقیقه دیگر...",
                end=""
            )

            time.sleep(5)

            continue

        if current.time() >= TAL_END:

            print("\n")
            print("=" * 70)
            print("🟢 TAL امروز تمام شده است.")
            print("=" * 70)

            break

        # ----------------------------------------------------
        # TAL ACTIVE
        # ----------------------------------------------------

        print(
            f"\n🔴 TAL فعال است | "
            f"{current:%H:%M:%S}"
        )

        data = get_market_watch()

        rows = parse_market_watch(data)

        if rows:

            show_market(rows)

            filename = save_report(rows)

            print(
                f"\n💾 گزارش ذخیره شد:"
            )

            print(filename)

        else:

            print(
                "⚠️ این مرحله اطلاعات Market Watch دریافت نشد."
            )

        time.sleep(INTERVAL)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    monitor()

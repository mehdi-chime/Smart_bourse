"""
Project : Smart_Bourse

File : test_indicators.py

Version : 1.2.0

Author :
Mehdi Jalali
ChatGPT

Description :
Test Technical Indicators
"""

import sys
from pathlib import Path


# =====================================================
# PROJECT ROOT
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =====================================================
# IMPORTS
# =====================================================

from history.history_database import HistoryDatabase
from indicators.indicator_manager import IndicatorManager


# =====================================================
# TEST CONFIGURATION
# =====================================================

SYMBOL = "Foolad"
DAYS = 365


# =====================================================
# DATA QUALITY CHECK
# =====================================================

def check_data_quality(stocks):

    print()
    print("=" * 80)
    print("DATA QUALITY CHECK")
    print("=" * 80)

    total = len(stocks)

    print("Total Records :", total)

    if not stocks:

        print("No Data Found")
        print("=" * 80)

        return False

    bad_records = []

    for stock in stocks:

        try:

            open_price = float(stock.open_price)
            high = float(stock.high_price)
            low = float(stock.low_price)
            close = float(stock.close_price)

        except (TypeError, ValueError):

            bad_records.append(
                (
                    stock,
                    "Invalid Number"
                )
            )

            continue

        # ---------------------------------------------
        # Zero / negative prices
        # ---------------------------------------------

        if open_price <= 0:

            bad_records.append(
                (
                    stock,
                    "Open <= 0"
                )
            )

            continue

        if high <= 0:

            bad_records.append(
                (
                    stock,
                    "High <= 0"
                )
            )

            continue

        if low <= 0:

            bad_records.append(
                (
                    stock,
                    "Low <= 0"
                )
            )

            continue

        if close <= 0:

            bad_records.append(
                (
                    stock,
                    "Close <= 0"
                )
            )

            continue

        # ---------------------------------------------
        # Invalid High / Low
        # ---------------------------------------------

        if high < low:

            bad_records.append(
                (
                    stock,
                    "High < Low"
                )
            )

            continue

        # ---------------------------------------------
        # Open outside High / Low
        # ---------------------------------------------

        if open_price > high or open_price < low:

            bad_records.append(
                (
                    stock,
                    "Open outside High/Low"
                )
            )

            continue

        # ---------------------------------------------
        # Close outside High / Low
        # ---------------------------------------------

        if close > high or close < low:

            bad_records.append(
                (
                    stock,
                    "Close outside High/Low"
                )
            )

            continue

    # ---------------------------------------------
    # Statistics
    # ---------------------------------------------

    print("Bad Records   :", len(bad_records))
    print("Good Records  :", total - len(bad_records))

    # =================================================
    # SHOW BAD RECORDS
    # =================================================

    if bad_records:

        print()
        print("-" * 80)
        print("BAD RECORDS")
        print("-" * 80)

        for stock, reason in bad_records[:20]:

            print(
                f"{stock.trade_date} | "
                f"{stock.symbol} | "
                f"Open={stock.open_price} | "
                f"High={stock.high_price} | "
                f"Low={stock.low_price} | "
                f"Close={stock.close_price} | "
                f"Reason={reason}"
            )

        if len(bad_records) > 20:

            print()
            print(
                f"... {len(bad_records) - 20} "
                "more bad records"
            )

    else:

        print()
        print("No Invalid OHLC Records Found")

    print("=" * 80)

    return True


# =====================================================
# CLEAN MARKET DATA
# =====================================================

def clean_market_data(stocks):

    print()
    print("=" * 80)
    print("CLEANING MARKET DATA")
    print("=" * 80)

    clean_stocks = []

    removed = 0

    for stock in stocks:

        try:

            open_price = float(stock.open_price)
            high = float(stock.high_price)
            low = float(stock.low_price)
            close = float(stock.close_price)

        except (TypeError, ValueError):

            removed += 1
            continue

        # ---------------------------------------------
        # Invalid prices
        # ---------------------------------------------

        if open_price <= 0:
            removed += 1
            continue

        if high <= 0:
            removed += 1
            continue

        if low <= 0:
            removed += 1
            continue

        if close <= 0:
            removed += 1
            continue

        # ---------------------------------------------
        # Invalid OHLC relationship
        # ---------------------------------------------

        if high < low:
            removed += 1
            continue

        if open_price > high or open_price < low:
            removed += 1
            continue

        if close > high or close < low:
            removed += 1
            continue

        clean_stocks.append(stock)

    # ---------------------------------------------
    # VERY IMPORTANT
    # Sort old -> new
    # ---------------------------------------------

    clean_stocks.sort(
        key=lambda stock: stock.trade_date
    )

    print("Original Records :", len(stocks))
    print("Clean Records    :", len(clean_stocks))
    print("Removed Records  :", removed)

    print("=" * 80)

    return clean_stocks


# =====================================================
# SHOW LAST RECORDS
# =====================================================

def show_last_records(stocks, count=5):

    print()
    print("=" * 80)
    print(f"LAST {count} VALID HISTORY RECORDS")
    print("=" * 80)

    if not stocks:

        print("No Valid Records")

        print("=" * 80)

        return

    for stock in stocks[-count:]:

        print(
            f"{stock.trade_date} | "
            f"{stock.symbol} | "
            f"Open={stock.open_price} | "
            f"High={stock.high_price} | "
            f"Low={stock.low_price} | "
            f"Close={stock.close_price} | "
            f"Volume={stock.volume}"
        )

    print("=" * 80)


# =====================================================
# MAIN TEST
# =====================================================

def main():

    print()
    print("=" * 80)
    print("SMART BOURSE - INDICATOR TEST")
    print("=" * 80)

    print("Symbol :", SYMBOL)
    print("Days   :", DAYS)

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    history_db = HistoryDatabase()

    try:

        history_db.connect()

        stocks = history_db.get_history(
            SYMBOL,
            DAYS
        )

    finally:

        history_db.close()

    # --------------------------------------------------
    # History Check
    # --------------------------------------------------

    print()
    print("History Records :", len(stocks))

    if not stocks:

        print()
        print("ERROR: No History Found")

        return

    if len(stocks) < 30:

        print()
        print("ERROR: Not Enough History")

        return

    # --------------------------------------------------
    # Original Last Records
    # --------------------------------------------------

    show_last_records(
        stocks,
        5
    )

    # --------------------------------------------------
    # Data Quality
    # --------------------------------------------------

    if not check_data_quality(stocks):

        print()
        print("ERROR: Data Quality Check Failed")

        return

    # --------------------------------------------------
    # Clean Data
    # --------------------------------------------------

    stocks = clean_market_data(stocks)

    if not stocks:

        print()
        print("ERROR: No Clean History Available")

        return

    if len(stocks) < 30:

        print()
        print(
            "ERROR: Not Enough Clean History"
        )

        print(
            "Clean Records :",
            len(stocks)
        )

        return

    # --------------------------------------------------
    # Valid History Summary
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("CLEAN HISTORY SUMMARY")
    print("=" * 80)

    print("Valid Records :", len(stocks))

    print(
        "First Date    :",
        stocks[0].trade_date
    )

    print(
        "Last Date     :",
        stocks[-1].trade_date
    )

    print(
        "Last Price    :",
        stocks[-1].close_price
    )

    print("=" * 80)

    # --------------------------------------------------
    # Last Valid Records
    # --------------------------------------------------

    show_last_records(
        stocks,
        5
    )

    # --------------------------------------------------
    # Indicators
    # --------------------------------------------------

    indicators = IndicatorManager()

    print()
    print("=" * 80)
    print("CALCULATING INDICATORS")
    print("=" * 80)

    try:

        results = indicators.run(
            stocks
        )

    except Exception as e:

        print()
        print("=" * 80)
        print("INDICATOR ERROR")
        print("=" * 80)

        print(
            "Error Type :",
            type(e).__name__
        )

        print(
            "Error      :",
            e
        )

        print("=" * 80)

        return

    # --------------------------------------------------
    # Show Results
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("TECHNICAL INDICATORS")
    print("=" * 80)

    for name, value in results.items():

        print(
            f"{name:<20} : {value}"
        )

    print("=" * 80)

    # --------------------------------------------------
    # Last Price
    # --------------------------------------------------

    last_price = float(
        stocks[-1].close_price
    )

    print()
    print("Last Price :", last_price)

    # --------------------------------------------------
    # Quick Market Check
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("QUICK MARKET CHECK")
    print("=" * 80)

    print(
        "Last Price :",
        last_price
    )

    # -----------------------------------------------
    # Moving Average
    # -----------------------------------------------

    if "Moving Average" in results:

        ma = results["Moving Average"]

        if isinstance(ma, (int, float)):

            print(
                "Price vs MA :",
                "Above" if last_price > ma else "Below"
            )

    # -----------------------------------------------
    # EMA
    # -----------------------------------------------

    if "EMA" in results:

        ema = results["EMA"]

        if isinstance(ema, (int, float)):

            print(
                "Price vs EMA :",
                "Above" if last_price > ema else "Below"
            )

    # -----------------------------------------------
    # RSI
    # -----------------------------------------------

    if "RSI" in results:

        print(
            "RSI Status :",
            results["RSI"]
        )

    # -----------------------------------------------
    # ADX
    # -----------------------------------------------

    if "ADX" in results:

        print(
            "ADX Status :",
            results["ADX"]
        )

    # -----------------------------------------------
    # ATR
    # -----------------------------------------------

    if "ATR" in results:

        print(
            "ATR Status :",
            results["ATR"]
        )

    # -----------------------------------------------
    # SuperTrend
    # -----------------------------------------------

    if "SuperTrend" in results:

        print(
            "SuperTrend :",
            results["SuperTrend"]
        )

    print("=" * 80)

    # --------------------------------------------------
    # Done
    # --------------------------------------------------

    print()
    print("=" * 80)
    print("INDICATOR TEST FINISHED")
    print("=" * 80)


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    main()

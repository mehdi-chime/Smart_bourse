"""
Project : Smart_Bourse

File : test_signal_engine.py

Version : 0.2.0

Description :
Test Signal Engine with Clean Market Data
"""

print(">>> TEST SIGNAL ENGINE FILE IS RUNNING <<<")

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
from strategy.signal_engine import SignalEngine


# =====================================================
# CONFIGURATION
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
        # Invalid OHLC relationship
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

    clean_stocks = []

    for stock in stocks:

        try:

            open_price = float(stock.open_price)
            high = float(stock.high_price)
            low = float(stock.low_price)
            close = float(stock.close_price)

        except (TypeError, ValueError):

            continue

        # ---------------------------------------------
        # Positive prices
        # ---------------------------------------------

        if open_price <= 0:
            continue

        if high <= 0:
            continue

        if low <= 0:
            continue

        if close <= 0:
            continue

        # ---------------------------------------------
        # OHLC relationship
        # ---------------------------------------------

        if high < low:
            continue

        if close > high or close < low:
            continue

        if open_price > high or open_price < low:
            continue

        clean_stocks.append(stock)

    return clean_stocks


# =====================================================
# SHOW LAST RECORDS
# =====================================================

def show_last_records(stocks, count=5):

    print()
    print("=" * 80)
    print(f"LAST {count} VALID HISTORY RECORDS")
    print("=" * 80)

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
# MAIN
# =====================================================

def main():

    print()
    print("=" * 80)
    print("SMART BOURSE - SIGNAL ENGINE TEST")
    print("=" * 80)

    print("Symbol :", SYMBOL)
    print("Days   :", DAYS)

    # =================================================
    # DATABASE
    # =================================================

    history_db = HistoryDatabase()

    try:

        history_db.connect()

        stocks = history_db.get_history(
            SYMBOL,
            DAYS
        )

    finally:

        history_db.close()

    # =================================================
    # HISTORY CHECK
    # =================================================

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

    # =================================================
    # LAST RAW RECORDS
    # =================================================

    show_last_records(
        stocks,
        5
    )

    # =================================================
    # DATA QUALITY
    # =================================================

    if not check_data_quality(stocks):

        print()
        print("ERROR: Data Quality Check Failed")
        return

    # =================================================
    # CLEAN DATA
    # =================================================

    print()
    print("=" * 80)
    print("CLEANING MARKET DATA")
    print("=" * 80)

    clean_stocks = clean_market_data(stocks)

    print(
        "Original Records :",
        len(stocks)
    )

    print(
        "Clean Records    :",
        len(clean_stocks)
    )

    print(
        "Removed Records  :",
        len(stocks) - len(clean_stocks)
    )

    print("=" * 80)

    # =================================================
    # CLEAN HISTORY CHECK
    # =================================================

    if len(clean_stocks) < 52:

        print()
        print(
            "ERROR: Not Enough Clean Data "
            "for Technical Indicators"
        )

        return

    # =================================================
    # CLEAN HISTORY SUMMARY
    # =================================================

    print()
    print("=" * 80)
    print("CLEAN HISTORY SUMMARY")
    print("=" * 80)

    print(
        "Valid Records :",
        len(clean_stocks)
    )

    print(
        "First Date    :",
        clean_stocks[0].trade_date
    )

    print(
        "Last Date     :",
        clean_stocks[-1].trade_date
    )

    print(
        "Last Price    :",
        clean_stocks[-1].close_price
    )

    print("=" * 80)

    # =================================================
    # LAST VALID RECORDS
    # =================================================

    show_last_records(
        clean_stocks,
        5
    )

    # =================================================
    # INDICATORS
    # =================================================

    print()
    print("=" * 80)
    print("CALCULATING INDICATORS")
    print("=" * 80)

    indicator_manager = IndicatorManager()

    try:

        results = indicator_manager.run(
            clean_stocks
        )

    except Exception as error:

        print()
        print("=" * 80)
        print("INDICATOR ERROR")
        print("=" * 80)

        print(
            type(error).__name__
        )

        print(error)

        print("=" * 80)

        return

    # =================================================
    # LAST PRICE
    # =================================================

    last_price = clean_stocks[-1].close_price

    print()
    print("Last Price :", last_price)

    # =================================================
    # SIGNAL ENGINE
    # =================================================

    print()
    print("=" * 80)
    print("RUNNING SIGNAL ENGINE")
    print("=" * 80)

    signal_engine = SignalEngine()

    try:

        analysis = signal_engine.calculate(
            results,
            last_price
        )

    except Exception as error:

        print()
        print("=" * 80)
        print("SIGNAL ENGINE ERROR")
        print("=" * 80)

        print(
            type(error).__name__
        )

        print(error)

        print("=" * 80)

        return

    # =================================================
    # SIGNAL RESULT
    # =================================================

    print()
    print("=" * 80)
    print("SIGNAL ENGINE RESULT")
    print("=" * 80)

    print(
        "Signal         :",
        analysis["Signal"]
    )

    print(
        "Score          :",
        analysis["Score"]
    )

    print(
        "Confidence     :",
        analysis["Confidence"]
    )

    # =================================================
    # TREND
    # =================================================

    if "Trend" in analysis:

        print(
            "Trend          :",
            analysis["Trend"]
        )

    if "Trend Strength" in analysis:

        print(
            "Trend Strength :",
            analysis["Trend Strength"]
        )

    if "Reversal Risk" in analysis:

        print(
            "Reversal Risk  :",
            analysis["Reversal Risk"]
        )

    # =================================================
    # INDICATOR SIGNALS
    # =================================================

    print()
    print("-" * 80)
    print("INDICATOR SIGNALS")
    print("-" * 80)

    for name, signal in analysis["Details"].items():

        print(
            f"{name:<15} : {signal}"
        )

    # =================================================
    # WARNINGS
    # =================================================

    warnings = analysis.get(
        "Warnings",
        []
    )

    if warnings:

        print()
        print("-" * 80)
        print("WARNINGS")
        print("-" * 80)

        for warning in warnings:

            print(
                "!",
                warning
            )

    print("=" * 80)

    # =================================================
    # FINAL
    # =================================================

    print()
    print("=" * 80)
    print("SIGNAL ENGINE TEST FINISHED")
    print("=" * 80)


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    main()

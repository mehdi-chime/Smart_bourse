import os
import sys

# Add Smart_Bourse root folder to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from history.history_database import HistoryDatabase
from indicators.rsi import RSI


SYMBOL = "Foolad"
DAYS = 365


def main():

    print("=" * 70)
    print("SMART BOURSE - RSI TEST")
    print("=" * 70)

    print("Symbol :", SYMBOL)
    print("Days   :", DAYS)

    # ------------------------------------------
    # Database
    # ------------------------------------------

    db = HistoryDatabase()

    db.connect()

    stocks = db.get_history(
        SYMBOL,
        DAYS
    )

    db.close()

    # ------------------------------------------
    # Check history
    # ------------------------------------------

    print()
    print("History Records :", len(stocks))

    if not stocks:

        print("No history data found.")

        return

    # ------------------------------------------
    # Prices
    # ------------------------------------------

    prices = [

        stock.close_price

        for stock in stocks

        if isinstance(
            stock.close_price,
            (int, float)
        )

    ]

    print()
    print("First Price :", prices[0])
    print("Last Price  :", prices[-1])

    # ------------------------------------------
    # RSI
    # ------------------------------------------

    rsi = RSI(
        period=14
    )

    result = rsi.calculate(
        prices
    )

    # ------------------------------------------
    # Result
    # ------------------------------------------

    print()
    print("=" * 70)
    print("RSI RESULT")
    print("=" * 70)

    print("RSI    :", result)

    print(
        "Signal :",
        rsi.signal(result)
    )

    print("=" * 70)


if __name__ == "__main__":

    main()

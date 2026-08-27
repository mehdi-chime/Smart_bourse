"""
Project : Smart_Bourse

File : fibonacci.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Fibonacci Retracement Indicator
"""


class Fibonacci:

    def __init__(self, period=120):

        self.name = "Fibonacci"

        self.period = period

    # --------------------------------------------------

    def calculate(self, stocks):

        if not stocks:

            return "No Data"

        # ----------------------------------------------
        # Limit analysis window
        # ----------------------------------------------

        stocks = stocks[-self.period:]

        # ----------------------------------------------
        # Extract High / Low
        # ----------------------------------------------

        if hasattr(stocks[0], "high_price"):

            highs = [

                float(stock.high_price)

                for stock in stocks

                if stock.high_price is not None
            ]

            lows = [

                float(stock.low_price)

                for stock in stocks

                if stock.low_price is not None
            ]

        else:

            prices = [

                float(price)

                for price in stocks

                if isinstance(price, (int, float))
            ]

            highs = prices

            lows = prices

        # ----------------------------------------------

        if not highs or not lows:

            return "No Data"

        # ----------------------------------------------
        # Find Swing High / Swing Low
        # ----------------------------------------------

        highest = max(highs)

        lowest = min(lows)

        # ----------------------------------------------

        if highest <= lowest:

            return "Invalid Data"

        # ----------------------------------------------

        diff = highest - lowest

        # ----------------------------------------------
        # Fibonacci Levels
        # ----------------------------------------------

        levels = {

            "0%": round(highest, 2),

            "23.6%": round(
                highest - diff * 0.236,
                2
            ),

            "38.2%": round(
                highest - diff * 0.382,
                2
            ),

            "50%": round(
                highest - diff * 0.500,
                2
            ),

            "61.8%": round(
                highest - diff * 0.618,
                2
            ),

            "78.6%": round(
                highest - diff * 0.786,
                2
            ),

            "100%": round(lowest, 2)

        }

        # ----------------------------------------------
        # Extra information
        # ----------------------------------------------

        levels["Swing High"] = round(highest, 2)

        levels["Swing Low"] = round(lowest, 2)

        return levels

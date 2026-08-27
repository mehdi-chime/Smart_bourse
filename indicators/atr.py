"""
Project : Smart_Bourse

File : atr.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Average True Range - Wilder ATR
"""


class ATR:

    def __init__(self, period=14):

        self.name = "ATR"

        self.period = period

    # ----------------------------------

    def calculate(self, stocks):

        if not stocks:
            return "No Data"

        if len(stocks) <= self.period:

            return "Need More Data"

        # ----------------------------------
        # Calculate True Range
        # ----------------------------------

        true_ranges = []

        for i in range(1, len(stocks)):

            current = stocks[i]
            previous = stocks[i - 1]

            high = float(current.high_price)
            low = float(current.low_price)
            previous_close = float(previous.close_price)

            tr1 = high - low

            tr2 = abs(high - previous_close)

            tr3 = abs(low - previous_close)

            true_range = max(
                tr1,
                tr2,
                tr3
            )

            true_ranges.append(true_range)

        # ----------------------------------
        # Initial ATR
        # ----------------------------------

        if len(true_ranges) < self.period:

            return "Need More Data"

        atr = sum(
            true_ranges[:self.period]
        ) / self.period

        # ----------------------------------
        # Wilder Smoothing
        # ----------------------------------

        for true_range in true_ranges[self.period:]:

            atr = (
                (atr * (self.period - 1))
                + true_range
            ) / self.period

        return round(atr, 2)

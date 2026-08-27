"""
Project : Smart_Bourse

File : supertrend.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
SuperTrend Indicator
"""


class SuperTrend:

    def __init__(self, period=14, multiplier=3):

        self.name = "SuperTrend"

        self.period = period

        self.multiplier = multiplier

    # --------------------------------------------------

    def calculate(self, stocks):

        if not stocks:

            return "Need More Data"

        if len(stocks) < self.period + 1:

            return "Need More Data"

        # =================================================
        # TRUE RANGE
        # =================================================

        true_ranges = []

        for i in range(len(stocks)):

            current = stocks[i]

            high = float(current.high_price)
            low = float(current.low_price)

            # First candle
            if i == 0:

                tr = high - low

            else:

                previous_close = float(
                    stocks[i - 1].close_price
                )

                tr = max(

                    high - low,

                    abs(high - previous_close),

                    abs(low - previous_close)

                )

            true_ranges.append(tr)

        # =================================================
        # ATR
        # =================================================

        atr_values = [None] * len(stocks)

        initial_atr = (

            sum(
                true_ranges[:self.period]
            )
            / self.period

        )

        atr_values[self.period - 1] = initial_atr

        # Wilder ATR smoothing

        for i in range(
            self.period,
            len(stocks)
        ):

            atr_values[i] = (

                (
                    atr_values[i - 1]
                    * (self.period - 1)
                )
                + true_ranges[i]

            ) / self.period

        # =================================================
        # BASIC BANDS
        # =================================================

        basic_upper = [None] * len(stocks)
        basic_lower = [None] * len(stocks)

        for i in range(
            self.period - 1,
            len(stocks)
        ):

            high = float(
                stocks[i].high_price
            )

            low = float(
                stocks[i].low_price
            )

            middle = (
                high + low
            ) / 2

            basic_upper[i] = (
                middle
                + self.multiplier
                * atr_values[i]
            )

            basic_lower[i] = (
                middle
                - self.multiplier
                * atr_values[i]
            )

        # =================================================
        # FINAL BANDS
        # =================================================

        final_upper = [None] * len(stocks)
        final_lower = [None] * len(stocks)

        for i in range(
            self.period - 1,
            len(stocks)
        ):

            if i == self.period - 1:

                final_upper[i] = basic_upper[i]

                final_lower[i] = basic_lower[i]

                continue

            previous_close = float(
                stocks[i - 1].close_price
            )

            previous_upper = final_upper[i - 1]

            previous_lower = final_lower[i - 1]

            # Final upper band

            if (
                basic_upper[i] < previous_upper
                or previous_close > previous_upper
            ):

                final_upper[i] = basic_upper[i]

            else:

                final_upper[i] = previous_upper

            # Final lower band

            if (
                basic_lower[i] > previous_lower
                or previous_close < previous_lower
            ):

                final_lower[i] = basic_lower[i]

            else:

                final_lower[i] = previous_lower

        # =================================================
        # SUPERTREND
        # =================================================

        supertrend = [None] * len(stocks)

        trend = [None] * len(stocks)

        start = self.period - 1

        supertrend[start] = final_upper[start]

        trend[start] = "Sell"

        for i in range(
            start + 1,
            len(stocks)
        ):

            close = float(
                stocks[i].close_price
            )

            previous_close = float(
                stocks[i - 1].close_price
            )

            previous_supertrend = (
                supertrend[i - 1]
            )

            if previous_supertrend == final_upper[i - 1]:

                if close <= final_upper[i]:

                    supertrend[i] = final_upper[i]

                    trend[i] = "Sell"

                else:

                    supertrend[i] = final_lower[i]

                    trend[i] = "Buy"

            else:

                if close >= final_lower[i]:

                    supertrend[i] = final_lower[i]

                    trend[i] = "Buy"

                else:

                    supertrend[i] = final_upper[i]

                    trend[i] = "Sell"

        # =================================================
        # FINAL RESULT
        # =================================================

        last_index = len(stocks) - 1

        last_atr = atr_values[last_index]

        last_supertrend = supertrend[last_index]

        last_trend = trend[last_index]

        return {

            "ATR": round(
                last_atr,
                2
            ),

            "SuperTrend": round(
                last_supertrend,
                2
            ),

            "Trend": last_trend

        }

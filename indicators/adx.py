"""
Project : Smart_Bourse

File : adx.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Average Directional Index - Wilder ADX
"""


class ADX:

    def __init__(self, period=14):

        self.name = "ADX"

        self.period = period

    # ----------------------------------

    def calculate(self, stocks):

        if not stocks:

            return "No Data"

        if len(stocks) < (self.period * 2):

            return "Need More Data"

        # ----------------------------------
        # Raw values
        # ----------------------------------

        plus_dm = []
        minus_dm = []
        true_ranges = []

        # ----------------------------------
        # Calculate DM and TR
        # ----------------------------------

        for i in range(1, len(stocks)):

            current = stocks[i]
            previous = stocks[i - 1]

            high = float(current.high_price)
            low = float(current.low_price)

            previous_high = float(
                previous.high_price
            )

            previous_low = float(
                previous.low_price
            )

            previous_close = float(
                previous.close_price
            )

            # ------------------------------
            # Directional Movement
            # ------------------------------

            up_move = high - previous_high

            down_move = previous_low - low

            if up_move > down_move and up_move > 0:

                plus_dm.append(up_move)

            else:

                plus_dm.append(0.0)

            if down_move > up_move and down_move > 0:

                minus_dm.append(down_move)

            else:

                minus_dm.append(0.0)

            # ------------------------------
            # True Range
            # ------------------------------

            tr1 = high - low

            tr2 = abs(
                high - previous_close
            )

            tr3 = abs(
                low - previous_close
            )

            true_range = max(
                tr1,
                tr2,
                tr3
            )

            true_ranges.append(true_range)

        # ----------------------------------
        # Initial Wilder smoothing
        # ----------------------------------

        period = self.period

        smoothed_tr = sum(
            true_ranges[:period]
        )

        smoothed_plus_dm = sum(
            plus_dm[:period]
        )

        smoothed_minus_dm = sum(
            minus_dm[:period]
        )

        dx_values = []

        # ----------------------------------
        # Calculate first DI / DX
        # ----------------------------------

        for i in range(
            period,
            len(true_ranges)
        ):

            if smoothed_tr == 0:

                plus_di = 0.0
                minus_di = 0.0

            else:

                plus_di = (
                    smoothed_plus_dm
                    / smoothed_tr
                ) * 100

                minus_di = (
                    smoothed_minus_dm
                    / smoothed_tr
                ) * 100

            denominator = (
                plus_di + minus_di
            )

            if denominator == 0:

                dx = 0.0

            else:

                dx = (
                    abs(
                        plus_di - minus_di
                    )
                    / denominator
                ) * 100

            dx_values.append(dx)

            # ----------------------------------
            # Wilder smoothing for next period
            # ----------------------------------

            smoothed_tr = (
                smoothed_tr
                - (smoothed_tr / period)
                + true_ranges[i]
            )

            smoothed_plus_dm = (
                smoothed_plus_dm
                - (smoothed_plus_dm / period)
                + plus_dm[i]
            )

            smoothed_minus_dm = (
                smoothed_minus_dm
                - (smoothed_minus_dm / period)
                + minus_dm[i]
            )

        # ----------------------------------
        # Need enough DX values for ADX
        # ----------------------------------

        if len(dx_values) < period:

            return "Need More Data"

        # ----------------------------------
        # Initial ADX
        # ----------------------------------

        adx = sum(
            dx_values[:period]
        ) / period

        # ----------------------------------
        # Wilder ADX smoothing
        # ----------------------------------

        for dx in dx_values[period:]:

            adx = (
                (
                    adx
                    * (period - 1)
                )
                + dx
            ) / period

        return round(adx, 2)

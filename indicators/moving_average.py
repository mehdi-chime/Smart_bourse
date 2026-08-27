"""
Project : Smart_Bourse

File : moving_average.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Simple Moving Average Indicator
"""


class MovingAverage:

    def __init__(self, period=20):

        self.name = "Moving Average"

        self.period = period

    # --------------------------------------------------

    def calculate(self, prices):

        """
        prices : list[float]

        Returns:
            Simple Moving Average of the latest period.
        """

        if not prices:

            return 0.0

        # Remove invalid values
        prices = [

            float(price)

            for price in prices

            if isinstance(price, (int, float))

        ]

        if not prices:

            return 0.0

        # اگر داده کمتر از period باشد،
        # از تمام داده موجود استفاده می‌کنیم.

        period = min(
            self.period,
            len(prices)
        )

        recent_prices = prices[-period:]

        average = (
            sum(recent_prices)
            / len(recent_prices)
        )

        return round(average, 2)

    # --------------------------------------------------

    def calculate_multiple(self, prices):

        """
        Calculate multiple moving averages.

        Returns:
            MA20
            MA50
            MA100
            MA200
        """

        periods = [20, 50, 100, 200]

        result = {}

        for period in periods:

            if len(prices) < period:

                result[f"MA{period}"] = None

                continue

            recent_prices = prices[-period:]

            average = (
                sum(recent_prices)
                / period
            )

            result[f"MA{period}"] = round(
                average,
                2
            )

        return result

    # --------------------------------------------------

    def signal(self, close_price, average):

        if average is None:

            return "HOLD"

        if close_price > average:

            return "BUY"

        elif close_price < average:

            return "SELL"

        return "HOLD"

"""
Project : Smart_Bourse

File : rsi.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Relative Strength Index - Wilder RSI
"""


class RSI:

    def __init__(self, period=14):

        self.name = "RSI"

        self.period = period

    # --------------------------------------------------

    def calculate(self, data):

        if not data:

            return 0.0

        # =================================================
        # Convert input to price list
        # =================================================

        if hasattr(data[0], "close_price"):

            prices = [

                stock.close_price

                for stock in data

            ]

        else:

            prices = list(data)

        # =================================================
        # Clean prices
        # =================================================

        clean_prices = []

        for price in prices:

            if isinstance(price, (int, float)):

                clean_prices.append(float(price))

        prices = clean_prices

        # =================================================
        # Check data
        # =================================================

        if len(prices) < self.period + 1:

            return None

        # =================================================
        # Calculate price changes
        # =================================================

        changes = [

            prices[i] - prices[i - 1]

            for i in range(1, len(prices))

        ]

        # =================================================
        # Initial Wilder averages
        # =================================================

        initial_changes = changes[:self.period]

        gains = [

            max(change, 0.0)

            for change in initial_changes

        ]

        losses = [

            max(-change, 0.0)

            for change in initial_changes

        ]

        average_gain = (
            sum(gains)
            / self.period
        )

        average_loss = (
            sum(losses)
            / self.period
        )

        # =================================================
        # Wilder smoothing
        # =================================================

        for change in changes[self.period:]:

            gain = max(change, 0.0)

            loss = max(-change, 0.0)

            average_gain = (

                (
                    average_gain
                    * (self.period - 1)
                )
                + gain

            ) / self.period

            average_loss = (

                (
                    average_loss
                    * (self.period - 1)
                )
                + loss

            ) / self.period

        # =================================================
        # RSI calculation
        # =================================================

        if average_gain == 0 and average_loss == 0:

            return 50.0

        if average_loss == 0:

            return 100.0

        if average_gain == 0:

            return 0.0

        rs = (
            average_gain
            / average_loss
        )

        rsi = 100 - (
            100 / (1 + rs)
        )

        # =================================================
        # Safety clamp
        # =================================================

        rsi = max(
            0.0,
            min(100.0, rsi)
        )

        return round(rsi, 2)

    # --------------------------------------------------

    def signal(self, rsi):

        if rsi is None:

            return "HOLD"

        if rsi <= 30:

            return "OVERSOLD"

        elif rsi >= 70:

            return "OVERBOUGHT"

        return "NEUTRAL"

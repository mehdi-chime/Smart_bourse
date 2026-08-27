"""
Project : Smart_Bourse

File : ema.py

Version : 0.3.0

Author :
Mehdi Jalali
ChatGPT

Description :
Exponential Moving Average
"""


class EMA:

    def __init__(self):

        self.name = "EMA"

    # --------------------------------------------------

    def calculate(self, data, period=14):

        if not data:
            return 0

        # اگر Stock باشد
        if hasattr(data[0], "close_price"):
            prices = [stock.close_price for stock in data]

        # اگر لیست قیمت باشد
        else:
            prices = data

        if len(prices) == 1:
            return round(prices[0], 2)

        multiplier = 2 / (period + 1)

        ema = prices[0]

        for price in prices[1:]:

            ema = ((price - ema) * multiplier) + ema

        return round(ema, 2)

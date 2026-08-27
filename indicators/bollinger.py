"""
Project : Smart_Bourse

File : bollinger.py

Version : 0.3.0

Author :
Mehdi Jalali
ChatGPT

Description :
Bollinger Bands Indicator
"""

import math


class Bollinger:

    def __init__(self):

        self.name = "Bollinger Bands"

    # ----------------------------------

    def calculate(self, stocks, period=20):

        if not stocks:
            return "No Data"

        # اگر Stock Object باشد
        if hasattr(stocks[0], "close_price"):
            prices = [stock.close_price for stock in stocks]

        # اگر فقط لیست قیمت باشد
        else:
            prices = stocks

        if len(prices) < 2:
            return "Need More Data"

        # اگر داده کمتر از period باشد
        if len(prices) < period:
            period = len(prices)

        prices = prices[-period:]

        # ===========================
        # Moving Average
        # ===========================

        average = sum(prices) / len(prices)

        # ===========================
        # Standard Deviation
        # ===========================

        variance = 0

        for price in prices:

            variance += (price - average) ** 2

        variance = variance / len(prices)

        std = math.sqrt(variance)

        # ===========================
        # Bands
        # ===========================

        upper = average + (2 * std)

        lower = average - (2 * std)

        return {

            "Upper": round(upper, 2),
            "Middle": round(average, 2),
            "Lower": round(lower, 2)

        }

"""
Project : Smart_Bourse

File : macd.py

Version : 0.3.1

Author :
Mehdi Jalali
ChatGPT

Description :
Moving Average Convergence Divergence
"""


class MACD:

    def __init__(self):

        self.name = "MACD"

    # ----------------------------------

    def ema(self, prices, period):

        if not prices:
            return 0

        multiplier = 2 / (period + 1)

        ema = prices[0]

        for price in prices[1:]:

            ema = ((price - ema) * multiplier) + ema

        return ema

    # ----------------------------------

    def calculate(self, prices):

        if not prices:
            return None

        if len(prices) < 35:
            return "Need 35 Days"

        ema12_list = []
        ema26_list = []

        for i in range(len(prices)):

            ema12_list.append(self.ema(prices[: i + 1], 12))
            ema26_list.append(self.ema(prices[: i + 1], 26))

        macd_line = []

        for a, b in zip(ema12_list, ema26_list):
            macd_line.append(a - b)

        signal_line = self.ema(macd_line[-9:], 9)

        histogram = macd_line[-1] - signal_line

        if histogram > 0:
            trend = "Bullish"
        elif histogram < 0:
            trend = "Bearish"
        else:
            trend = "Neutral"

        return {

            "MACD": round(macd_line[-1], 2),

            "Signal": round(signal_line, 2),

            "Histogram": round(histogram, 2),

            "Trend": trend

        }       


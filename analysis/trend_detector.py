"""
Project : Smart_Bourse

File : trend_detector.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Detect Market Trend
"""


class TrendDetector:

    def __init__(self):

        self.trend = "UNKNOWN"

        self.strength = 0
# --------------------------------------------------

def detect(self, stocks):

    if not stocks:

        self.trend = "UNKNOWN"

        self.strength = 0

        return self.trend

    prices = []

    for stock in stocks:

        prices.append(stock.close_price)

    if len(prices) < 2:

        self.trend = "UNKNOWN"

        return self.trend

    first_price = prices[0]

    last_price = prices[-1]

    if last_price > first_price:

        self.trend = "UP"

    elif last_price < first_price:

        self.trend = "DOWN"

    else:

        self.trend = "SIDEWAYS"

    return self.trend
# --------------------------------------------------

def calculate_strength(self, stocks):

    if not stocks:

        self.strength = 0

        return self.strength

    prices = [stock.close_price for stock in stocks]

    if len(prices) < 2:

        self.strength = 0

        return self.strength

    first_price = prices[0]

    last_price = prices[-1]

    change = abs(last_price - first_price)

    percent = (change / first_price) * 100

    self.strength = round(percent, 2)

    return self.strength
# --------------------------------------------------

def show(self):

    print()

    print("=" * 60)
    print("TREND DETECTOR")
    print("=" * 60)

    print(f"Trend     : {self.trend}")

    print(f"Strength  : {self.strength} %")

    print("=" * 60)

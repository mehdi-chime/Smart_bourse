"""
Project : Smart_Bourse

File : indicator_manager.py

Version : 0.3.2

Author :
Mehdi Jalali
ChatGPT

Description :
Manage All Technical Indicators
"""

from indicators.moving_average import MovingAverage
from indicators.ema import EMA
from indicators.rsi import RSI
from indicators.macd import MACD
from indicators.bollinger import Bollinger
from indicators.fibonacci import Fibonacci
from indicators.ichimoku import Ichimoku
from indicators.atr import ATR
from indicators.adx import ADX
from indicators.supertrend import SuperTrend


class IndicatorManager:

    def __init__(self):

        self.indicators = {

            "Moving Average": MovingAverage(),
            "EMA": EMA(),
            "RSI": RSI(),
            "MACD": MACD(),
            "Bollinger": Bollinger(),
            "Fibonacci": Fibonacci(),
            "Ichimoku": Ichimoku(),
            "ATR": ATR(),
            "ADX": ADX(),
            "SuperTrend": SuperTrend(),

        }

    # --------------------------------------------------

    def run(self, stocks):
        """
        stocks : list[Stock]
        """

        results = {}

        prices = [stock.close_price for stock in stocks]

        for name, indicator in self.indicators.items():

            try:

                # اندیکاتورهایی که فقط قیمت بسته شدن لازم دارند
                if name in [
                    "Moving Average",
                    "EMA",
                    "RSI",
                    "MACD",
                    "Bollinger",
                ]:

                    results[name] = indicator.calculate(prices)

                # اندیکاتورهایی که کل کندل لازم دارند
                else:

                    results[name] = indicator.calculate(stocks)

            except Exception as error:

                results[name] = f"Error : {error}"

        return results

    # --------------------------------------------------

    def show(self, stocks):

        print()
        print("=" * 80)
        print("Technical Indicators")
        print("=" * 80)

        results = self.run(stocks)

        for name, value in results.items():

            print(f"{name:<20} : {value}")

        print("=" * 80)

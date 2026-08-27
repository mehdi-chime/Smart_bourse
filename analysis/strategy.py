"""
Project : Smart_Bourse

File : strategy.py

Version : 1.1.0

Author :
Mehdi Jalali
ChatGPT

Description :
Decision Engine
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


class Strategy:

    def __init__(self):

        self.ma = MovingAverage()
        self.ema = EMA()
        self.rsi = RSI()
        self.macd = MACD()
        self.bollinger = Bollinger()
        self.fibonacci = Fibonacci()
        self.ichimoku = Ichimoku()
        self.atr = ATR()
        self.adx = ADX()
        self.supertrend = SuperTrend()

        self.score = 0
        self.signal = "WAIT"
        self.confidence = 0
        self.risk = "MEDIUM"

        self.details = {}

    # -------------------------------------------------

    def reset(self):

        self.score = 0
        self.signal = "WAIT"
        self.confidence = 0
        self.risk = "MEDIUM"

        self.details = {}

    # -------------------------------------------------

    def analyze(self, stocks):

        self.reset()

        if not stocks:

            return None

        prices = [stock.close_price for stock in stocks]

        current_price = prices[-1]
        # ==================================================
        # Calculate Indicators
        # ==================================================

        ma = self.ma.calculate(prices)

        ema = self.ema.calculate(stocks)

        rsi = self.rsi.calculate(stocks)

        prices = [s.close_price for s in stocks]

        macd = self.macd.calculate(prices)

        bollinger = self.bollinger.calculate(stocks)

        fibonacci = self.fibonacci.calculate(stocks)

        ichimoku = self.ichimoku.calculate(stocks)

        atr = self.atr.calculate(stocks)

        adx = self.adx.calculate(stocks)

        supertrend = self.supertrend.calculate(stocks)

        # ==================================================
        # Save Indicator Results
        # ==================================================

        self.details = {

            "MA": ma,
            "EMA": ema,
            "RSI": rsi,
            "MACD": macd,
            "Bollinger": bollinger,
            "Fibonacci": fibonacci,
            "Ichimoku": ichimoku,
            "ATR": atr,
            "ADX": adx,
            "SuperTrend": supertrend,

        }

        # ==================================================
        # Moving Average
        # ==================================================

        if isinstance(ma, (int, float)):

            if current_price > ma:

                self.score += 2

            elif current_price < ma:

                self.score -= 2

        # ==================================================
        # EMA
        # ==================================================

        if isinstance(ema, (int, float)):

            if current_price > ema:

                self.score += 2

            elif current_price < ema:

                self.score -= 2

        # ==================================================
        # RSI
        # ==================================================

        if isinstance(rsi, (int, float)):

            if rsi < 30:

                self.score += 3

            elif rsi > 70:

                self.score -= 3

        # ==================================================
        # MACD
        # ==================================================

        if isinstance(macd, (int, float)):

            if macd > 0:

                self.score += 2

            elif macd < 0:

                self.score -= 2

        # ==================================================
        # Bollinger
        # ==================================================

        if isinstance(bollinger, dict):

            if current_price < bollinger["Lower"]:

                self.score += 2

            elif current_price > bollinger["Upper"]:

                self.score -= 2

        # ==================================================
        # Fibonacci
        # ==================================================

        if isinstance(fibonacci, dict):

            if current_price > fibonacci["61.8%"]:

                self.score += 1

            else:

                self.score -= 1

        # ==================================================
        # Ichimoku
        # ==================================================

        if isinstance(ichimoku, dict):

            if current_price > ichimoku["Tenkan"]:

                self.score += 2

        # ==================================================
        # ATR
        # ==================================================

        if isinstance(atr, (int, float)):

            if atr > 1000:

                self.risk = "HIGH"

            elif atr > 300:

                self.risk = "MEDIUM"

            else:

                self.risk = "LOW"

        # ==================================================
        # ADX
        # ==================================================

        if isinstance(adx, (int, float)):

            if adx > 25:

                self.score += 1

        # ==================================================
        # SuperTrend
        # ==================================================

        if isinstance(supertrend, dict):

            if supertrend["Trend"] == "Buy":

                self.score += 3

            elif supertrend["Trend"] == "Sell":

                self.score -= 3
        # ==================================================
        # Final Decision
        # ==================================================

        if self.score >= 8:

            self.signal = "STRONG BUY"

        elif self.score >= 4:

            self.signal = "BUY"

        elif self.score <= -8:

            self.signal = "STRONG SELL"

        elif self.score <= -4:

            self.signal = "SELL"

        else:

            self.signal = "HOLD"

        # ==================================================
        # Confidence
        # ==================================================

        self.confidence = min(abs(self.score) * 10, 100)

        return {

            "Signal": self.signal,
            "Score": self.score,
            "Confidence": self.confidence,
            "Risk": self.risk,
            "Details": self.details

        }

    # -------------------------------------------------

    def show(self, stocks):

        result = self.analyze(stocks)

        if result is None:

            print("No Data")
            return

        print()
        print("=" * 90)
        print("SMART STRATEGY ENGINE")
        print("=" * 90)

        print(f"Signal      : {result['Signal']}")
        print(f"Score       : {result['Score']}")
        print(f"Confidence  : {result['Confidence']} %")
        print(f"Risk        : {result['Risk']}")

        print("-" * 90)

        for key, value in result["Details"].items():

            print(f"{key:<15} : {value}")

        print("=" * 90)
        

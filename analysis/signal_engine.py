"""
Project : Smart_Bourse

File : signal_engine.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Smart Signal Engine
"""

from analysis.trend_detector import TrendDetector

from indicators.ma import MovingAverage
from indicators.ema import EMA
from indicators.rsi import RSI
from indicators.macd import MACD
from indicators.adx import ADX
from indicators.atr import ATR
from indicators.supertrend import SuperTrend


class SignalEngine:

    def __init__(self):

        self.ma = MovingAverage()

        self.ema = EMA()

        self.rsi = RSI()

        self.macd = MACD()

        self.adx = ADX()

        self.atr = ATR()

        self.supertrend = SuperTrend()

        self.trend = TrendDetector()

        self.score = 0

        self.signal = "WAIT"

        self.confidence = 0
    # --------------------------------------------------

    def analyze(self, stocks):

        self.score = 0

        ma = self.ma.calculate(stocks)

        ema = self.ema.calculate(stocks)

        rsi = self.rsi.calculate(stocks)

        macd = self.macd.calculate(stocks)

        adx = self.adx.calculate(stocks)

        atr = self.atr.calculate(stocks)

        supertrend = self.supertrend.calculate(stocks)

        trend = self.trend.detect(stocks)

        trend_strength = self.trend.calculate_strength(stocks)

        result = {

            "MA": ma,

            "EMA": ema,

            "RSI": rsi,

            "MACD": macd,

            "ADX": adx,

            "ATR": atr,

            "SuperTrend": supertrend,

            "Trend": trend,

            "TrendStrength": trend_strength

        }

        return result

# --------------------------------------------------

    def calculate_score(self, result):

        self.score = 0

        # =======================
        # MA
        # =======================

        if isinstance(result["MA"], (int, float)):

            self.score += 10

        # =======================
        # EMA
        # =======================

        if isinstance(result["EMA"], (int, float)):

            self.score += 10


        # =======================
        # RSI
        # =======================

        if isinstance(result["RSI"], (int, float)):

            if result["RSI"] < 30:

                self.score += 20

            elif result["RSI"] < 50:

                self.score += 10

            elif result["RSI"] > 70:

                self.score -= 15

        # =======================
        # Trend
        # =======================

        if result["Trend"] == "UP":

            self.score += 15

        elif result["Trend"] == "DOWN":

            self.score -= 15

        # =======================
        # Trend Strength
        # =======================

        if result["TrendStrength"] >= 10:

            self.score += 15

        elif result["TrendStrength"] >= 5:

            self.score += 8

        elif result["TrendStrength"] >= 2:

            self.score += 3

        return self.score
# --------------------------------------------------

    def make_decision(self):

        if self.score >= 80:

            self.signal = "STRONG BUY"

            self.confidence = 95

        elif self.score >= 60:

            self.signal = "BUY"

            self.confidence = 80

        elif self.score >= 40:

            self.signal = "WATCH"

            self.confidence = 60

        elif self.score >= 20:

            self.signal = "HOLD"

            self.confidence = 40

        else:

            self.signal = "SELL"

            self.confidence = 20

        return {

            "Signal": self.signal,

            "Score": self.score,

            "Confidence": self.confidence

        }

# --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("SMART SIGNAL ENGINE")
        print("=" * 70)

        print(f"Signal      : {self.signal}")
        print(f"Score       : {self.score}")
        print(f"Confidence  : {self.confidence} %")

        print("=" * 70)    
        

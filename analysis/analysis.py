"""
Project : Smart_Bourse

File : analysis.py

Version : 0.2.0

Author :
Mehdi Jalali
ChatGPT

Description :
Smart Market Analyzer
"""
from indicators.macd import MACD
from database.database import Database

from indicators.moving_average import MovingAverage
from indicators.ema import EMA
from indicators.rsi import RSI

from analysis.trend import Trend
from analysis.signal import Signal
from analysis.risk import Risk
from analysis.score import Score


class Analyzer:

    def __init__(self):

        self.results = []

        self.db = Database()

        self.ma = MovingAverage()
        self.ema = EMA()
        self.rsi = RSI()
        self.macd = MACD()
        
        self.trend = Trend()
        self.signal = Signal()
        self.risk = Risk()
        self.score = Score()

    # ----------------------------------

    def analyze(self, stocks):

        self.results.clear()

        self.db.connect()

        for stock in stocks:

            prices = []

            for row in stocks:

                prices.append(row.close_price)

            if len(prices) == 0:

                prices.append(stock.close_price)

            ma = self.ma.calculate(prices)

            ema = self.ema.calculate(prices)

            rsi = self.rsi.calculate(prices)

            macd = self.macd.calculate(prices)

            difference = stock.close_price - stock.open_price

            if difference > 0:

                status = "Positive"

            elif difference < 0:

                status = "Negative"

            else:

                status = "Neutral"

            trend = self.trend.analyze(

                stock.close_price,
                ma

            )

            strength = self.trend.strength(

                difference

            )

            signal = self.signal.generate(

                trend,
                rsi

            )

            risk = self.risk.calculate(

                abs(difference)

            )

            score = self.score.calculate(

                trend,
                signal

            )

            self.results.append(

                {

                    "symbol": stock.symbol,

                    "days": len(prices),

                    "difference": difference,

                    "status": status,

                    "ma": ma,

                    "ema": ema,

                    "rsi": rsi,

                    "macd": macd,

                    "trend": trend,

                    "strength": strength,

                    "signal": signal,

                    "risk": risk,

                    "score": score

                }

            )

        self.db.close()

    # ----------------------------------

    def show(self):

        print()

        print("=" * 120)
        print("SMART MARKET ANALYSIS")
        print("=" * 120)

        if len(self.results) > 0:

            item = self.results[-1]

            print(

                f"{item['symbol']:<10}"

                f" MA:{item['ma']:<10.2f}"

                f" EMA:{item['ema']:<10.2f}"

                f" RSI:{item['rsi']:<8}"

                f" MACD:{str(item['macd']):<25}"

                f" Trend:{item['trend']:<12}"

                f" Signal:{item['signal']:<14}"

                f" Risk:{item['risk']:<8}"

                f" Score:{item['score']:<6}"

            )

        print("=" * 120)

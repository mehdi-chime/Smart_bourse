"""
Project : Smart_Bourse

File : ichimoku.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Ichimoku Cloud Indicator
"""


class Ichimoku:

    def __init__(self):

        self.name = "Ichimoku"

        self.tenkan_period = 9
        self.kijun_period = 26
        self.senkou_b_period = 52

    # --------------------------------------------------

    def calculate(self, stocks):

        if not stocks:

            return "No Data"

        # ----------------------------------------------
        # Need enough history
        # ----------------------------------------------

        if len(stocks) < self.senkou_b_period:

            return "Need 52 Days"

        # ----------------------------------------------
        # Clean data
        # ----------------------------------------------

        stocks = [

            stock

            for stock in stocks

            if stock.high_price is not None
            and stock.low_price is not None
            and stock.close_price is not None
            and stock.high_price > 0
            and stock.low_price > 0
            and stock.close_price > 0

        ]

        if len(stocks) < self.senkou_b_period:

            return "Need 52 Valid Days"

        # ----------------------------------------------
        # Tenkan-sen
        # ----------------------------------------------

        recent_9 = stocks[-self.tenkan_period:]

        highs9 = [

            float(stock.high_price)

            for stock in recent_9
        ]

        lows9 = [

            float(stock.low_price)

            for stock in recent_9
        ]

        tenkan = (

            max(highs9)
            + min(lows9)

        ) / 2

        # ----------------------------------------------
        # Kijun-sen
        # ----------------------------------------------

        recent_26 = stocks[-self.kijun_period:]

        highs26 = [

            float(stock.high_price)

            for stock in recent_26
        ]

        lows26 = [

            float(stock.low_price)

            for stock in recent_26
        ]

        kijun = (

            max(highs26)
            + min(lows26)

        ) / 2

        # ----------------------------------------------
        # Senkou Span A
        # ----------------------------------------------

        senkou_a = (

            tenkan + kijun

        ) / 2

        # ----------------------------------------------
        # Senkou Span B
        # ----------------------------------------------

        recent_52 = stocks[-self.senkou_b_period:]

        highs52 = [

            float(stock.high_price)

            for stock in recent_52
        ]

        lows52 = [

            float(stock.low_price)

            for stock in recent_52
        ]

        senkou_b = (

            max(highs52)
            + min(lows52)

        ) / 2

        # ----------------------------------------------
        # Current price
        # ----------------------------------------------

        close_price = float(

            stocks[-1].close_price

        )

        # ----------------------------------------------
        # Cloud
        # ----------------------------------------------

        cloud_top = max(

            senkou_a,
            senkou_b

        )

        cloud_bottom = min(

            senkou_a,
            senkou_b

        )

        # ----------------------------------------------
        # Price vs Cloud
        # ----------------------------------------------

        if close_price > cloud_top:

            cloud_position = "Above"

        elif close_price < cloud_bottom:

            cloud_position = "Below"

        else:

            cloud_position = "Inside"

        # ----------------------------------------------
        # Tenkan vs Kijun
        # ----------------------------------------------

        if tenkan > kijun:

            tk_signal = "Bullish"

        elif tenkan < kijun:

            tk_signal = "Bearish"

        else:

            tk_signal = "Neutral"

        # ----------------------------------------------
        # Cloud trend
        # ----------------------------------------------

        if senkou_a > senkou_b:

            cloud_trend = "Bullish"

        elif senkou_a < senkou_b:

            cloud_trend = "Bearish"

        else:

            cloud_trend = "Neutral"

        # ----------------------------------------------
        # Final Ichimoku signal
        # ----------------------------------------------

        bullish_points = 0
        bearish_points = 0

        if cloud_position == "Above":

            bullish_points += 1

        elif cloud_position == "Below":

            bearish_points += 1

        if tk_signal == "Bullish":

            bullish_points += 1

        elif tk_signal == "Bearish":

            bearish_points += 1

        if cloud_trend == "Bullish":

            bullish_points += 1

        elif cloud_trend == "Bearish":

            bearish_points += 1

        # ----------------------------------------------

        if bullish_points >= 2:

            trend = "Bullish"

        elif bearish_points >= 2:

            trend = "Bearish"

        else:

            trend = "Neutral"

        # ----------------------------------------------
        # Result
        # ----------------------------------------------

        return {

            "Tenkan": round(tenkan, 2),

            "Kijun": round(kijun, 2),

            "Senkou A": round(senkou_a, 2),

            "Senkou B": round(senkou_b, 2),

            "Chikou": round(close_price, 2),

            "Cloud Top": round(cloud_top, 2),

            "Cloud Bottom": round(cloud_bottom, 2),

            "Cloud Position": cloud_position,

            "TK Signal": tk_signal,

            "Cloud Trend": cloud_trend,

            "Trend": trend

        }

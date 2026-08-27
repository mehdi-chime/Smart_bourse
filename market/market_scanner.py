"""
Project : Smart_Bourse

File : market_scanner.py

Version : 1.0.0

Description :
Scan market symbols and classify them for
long-term investment and swing trading.
"""

from indicators.indicator_manager import IndicatorManager


class MarketScanner:

    def __init__(self):

        self.indicators = IndicatorManager()

    # --------------------------------------------------

    def scan_symbol(self, stocks):

        if not stocks:

            return None

        if len(stocks) < 60:

            return None

        result = self.indicators.run(stocks)

        score = 50

        reasons = []

        # =================================================
        # RSI
        # =================================================

        rsi = result.get("RSI")

        if isinstance(rsi, (int, float)):

            if 40 <= rsi <= 60:

                score += 5
                reasons.append("RSI balanced")

            elif 60 < rsi < 70:

                score += 3

            elif rsi >= 70:

                score -= 10
                reasons.append("RSI overbought")

            elif rsi <= 30:

                score += 5
                reasons.append("RSI oversold")

        # =================================================
        # MACD
        # =================================================

        macd = result.get("MACD", {})

        if isinstance(macd, dict):

            trend = macd.get("Trend")

            if trend == "Bullish":

                score += 10
                reasons.append("MACD bullish")

            elif trend == "Bearish":

                score -= 10
                reasons.append("MACD bearish")

        # =================================================
        # EMA / MA
        # =================================================

        ema = result.get("EMA")
        ma = result.get("Moving Average")

        if (
            isinstance(ema, (int, float))
            and isinstance(ma, (int, float))
            and ma != 0
        ):

            if ema > ma:

                score += 10
                reasons.append("EMA above MA")

            else:

                score -= 5

        # =================================================
        # ADX
        # =================================================

        adx = result.get("ADX")

        if isinstance(adx, (int, float)):

            if adx >= 25:

                score += 10
                reasons.append("Strong trend")

            elif adx < 15:

                score -= 5
                reasons.append("Weak trend")

        # =================================================
        # SuperTrend
        # =================================================

        supertrend = result.get("SuperTrend", {})

        if isinstance(supertrend, dict):

            trend = supertrend.get("Trend")

            if trend == "Buy":

                score += 10
                reasons.append("SuperTrend Buy")

            elif trend == "Sell":

                score -= 10
                reasons.append("SuperTrend Sell")

        # =================================================
        # Clamp
        # =================================================

        score = max(0, min(100, score))

        # =================================================
        # Classification
        # =================================================

        if score >= 70:

            category = "LONG_TERM"

        elif score >= 55:

            category = "SWING"

        else:

            category = "WEAK"

        return {

            "symbol": stocks[-1].symbol,

            "price": stocks[-1].close_price,

            "score": score,

            "category": category,

            "reasons": reasons,

            "indicators": result

        }

    # --------------------------------------------------

    def show_result(self, result):

        if not result:

            return

        print()

        print("=" * 70)

        print("MARKET SCANNER")

        print("=" * 70)

        print("Symbol   :", result["symbol"])

        print("Price    :", result["price"])

        print("Score    :", result["score"])

        print("Category :", result["category"])

        print()

        print("Reasons:")

        for reason in result["reasons"]:

            print(" -", reason)

        print("=" * 70)

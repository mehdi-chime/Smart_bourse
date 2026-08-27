"""
Project : Smart_Bourse

File : score_manager.py

Version : 4.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Directional Score Manager

Responsibilities:
- Calculate directional market score
- Use only indicators that contain directional information
- Keep volatility and trend-strength indicators separate
"""

from math import isfinite


class ScoreManager:

    def __init__(self):
        self.score = 50

    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def _number(value):
        return isinstance(value, (int, float)) and isfinite(value)

    # ==================================================
    # CALCULATE
    # ==================================================

    def calculate(self, indicators):

        score = 50

        # ==================================================
        # RSI
        # ==================================================

        rsi = indicators.get("RSI")

        if self._number(rsi):

            if rsi <= 20:
                score += 5

            elif rsi <= 30:
                score += 3

            elif rsi >= 80:
                score -= 5

            elif rsi >= 70:
                score -= 3

        # ==================================================
        # MACD
        # ==================================================

        macd = indicators.get("MACD")

        if isinstance(macd, dict):

            trend = macd.get("Trend")

            if trend == "Bullish":
                score += 15

            elif trend == "Bearish":
                score -= 15

        # ==================================================
        # EMA VS MA
        # ==================================================

        ema = indicators.get("EMA")
        ma = indicators.get("Moving Average")

        if (
            self._number(ema)
            and self._number(ma)
        ):

            if ema > ma:
                score += 10

            elif ema < ma:
                score -= 10

        # ==================================================
        # SUPERTREND
        # ==================================================

        supertrend = indicators.get("SuperTrend")

        if isinstance(supertrend, dict):

            trend = supertrend.get("Trend")

            if trend in ("Buy", "Strong Buy"):
                score += 15

            elif trend == "Sell":
                score -= 15

        # ==================================================
        # ICHIMOKU
        # ==================================================

        ichimoku = indicators.get("Ichimoku")

        if isinstance(ichimoku, dict):

            trend = ichimoku.get("Trend")

            if trend == "Bullish":
                score += 10

            elif trend == "Bearish":
                score -= 10

            else:

                tenkan = ichimoku.get("Tenkan")
                kijun = ichimoku.get("Kijun")

                if (
                    self._number(tenkan)
                    and self._number(kijun)
                ):

                    if tenkan > kijun:
                        score += 5

                    elif tenkan < kijun:
                        score -= 5

        # ==================================================
        # BOLLINGER
        # ==================================================
        # No directional score.
        # Bollinger is handled separately.

        # ==================================================
        # FIBONACCI
        # ==================================================
        # No directional score.
        # Fibonacci levels alone do not determine direction.

        # ==================================================
        # ADX
        # ==================================================
        # ADX measures trend strength, not direction.

        # ==================================================
        # ATR
        # ==================================================
        # ATR measures volatility, not direction.

        # ==================================================
        # CLAMP
        # ==================================================

        score = max(0, min(100, score))

        self.score = score

        return score

    # ==================================================
    # SIGNAL
    # ==================================================

    def signal(self):

        if self.score >= 80:
            return "STRONG BUY"

        elif self.score >= 65:
            return "BUY"

        elif self.score <= 20:
            return "STRONG SELL"

        elif self.score <= 35:
            return "SELL"

        return "HOLD"

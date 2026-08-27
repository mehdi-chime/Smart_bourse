"""
Project : Smart_Bourse

File : risk_manager.py

Version : 4.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Risk Management Engine
"""

from math import isfinite


class RiskManager:

    def __init__(self):
        self.last_score = 0

    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def _number(value):
        return isinstance(value, (int, float)) and isfinite(value)

    # ==================================================
    # ANALYZE
    # ==================================================

    def analyze(self, indicators):

        risk_score = 0
        reasons = []

        # ==================================================
        # ATR
        # ==================================================

        atr = indicators.get("ATR")
        last_price = indicators.get("Last Price")

        if (
            self._number(atr)
            and self._number(last_price)
            and last_price > 0
        ):

            atr_percent = (atr / last_price) * 100

            if atr_percent >= 10:
                risk_score += 3
                reasons.append("Very high volatility")

            elif atr_percent >= 6:
                risk_score += 2
                reasons.append("High volatility")

            elif atr_percent >= 3:
                risk_score += 1
                reasons.append("Moderate volatility")

        elif not self._number(atr):

            risk_score += 1
            reasons.append("ATR unavailable")

        # ==================================================
        # ADX
        # ==================================================

        adx = indicators.get("ADX")

        if self._number(adx):

            if adx < 20:
                risk_score += 2
                reasons.append("Trend strength is weak")

            elif adx < 25:
                risk_score += 1
                reasons.append("Trend strength is moderate")

        else:

            risk_score += 1
            reasons.append("ADX unavailable")

        # ==================================================
        # RSI
        # ==================================================

        rsi = indicators.get("RSI")

        if self._number(rsi):

            if rsi <= 20:
                risk_score += 2
                reasons.append("RSI is deeply oversold")

            elif rsi >= 80:
                risk_score += 2
                reasons.append("RSI is deeply overbought")

            elif rsi <= 30 or rsi >= 70:
                risk_score += 1
                reasons.append("RSI is in an extreme zone")

        else:

            risk_score += 1
            reasons.append("RSI unavailable")

        # ==================================================
        # SIGNAL CONFLICT
        # ==================================================

        bullish = 0
        bearish = 0

        for key in (
            "MA",
            "EMA",
            "MACD",
            "Ichimoku",
            "SuperTrend",
        ):

            value = indicators.get(key)

            if value == "Bullish":
                bullish += 1

            elif value == "Bearish":
                bearish += 1

            elif value in ("Buy", "Strong Buy"):
                bullish += 1

            elif value == "Sell":
                bearish += 1

        if bullish > 0 and bearish > 0:

            risk_score += 2
            reasons.append(
                "Directional indicators are conflicting"
            )

        # ==================================================
        # FINAL LEVEL
        # ==================================================

        if risk_score >= 7:
            level = "HIGH"

        elif risk_score >= 4:
            level = "MEDIUM"

        else:
            level = "LOW"

        self.last_score = risk_score

        return {
            "level": level,
            "score": risk_score,
            "reasons": reasons,
        }

    # ==================================================
    # COMPATIBILITY
    # ==================================================

    def level(self, indicators):
        return self.analyze(indicators)["level"]

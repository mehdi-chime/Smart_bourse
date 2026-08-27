"""
Project : Smart_Bourse

File : strategy_manager.py

Version : 5.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Professional Strategy Manager
"""

from strategy.score_manager import ScoreManager
from strategy.risk_manager import RiskManager


class StrategyManager:

    def __init__(self):

        self.score_manager = ScoreManager()
        self.risk_manager = RiskManager()

    # ==================================================
    # CONFIDENCE
    # ==================================================

    def confidence(self, score):

        distance = abs(score - 50)

        confidence = (distance / 50) * 100

        return round(
            min(confidence, 100),
            2
        )

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self, indicators):

        score = self.score_manager.calculate(
            indicators
        )

        risk_result = self.risk_manager.analyze(
            indicators
        )

        risk = risk_result["level"]

        risk_reasons = risk_result["reasons"]

        # ==================================================
        # BASE SIGNAL
        # ==================================================

        if score >= 80:
            signal = "STRONG BUY"

        elif score >= 65:
            signal = "BUY"

        elif score <= 20:
            signal = "STRONG SELL"

        elif score <= 35:
            signal = "SELL"

        else:
            signal = "HOLD"

        # ==================================================
        # RISK ADJUSTMENT
        # ==================================================

        if risk == "HIGH":

            if signal == "STRONG BUY":
                signal = "BUY"

            elif signal == "STRONG SELL":
                signal = "SELL"

        # ==================================================
        # REASONS
        # ==================================================

        reasons = []

        rsi = indicators.get("RSI")

        if isinstance(rsi, (int, float)):

            if rsi <= 20:
                reasons.append(
                    "RSI is deeply oversold"
                )

            elif rsi <= 30:
                reasons.append(
                    "RSI is oversold"
                )

            elif rsi >= 80:
                reasons.append(
                    "RSI is deeply overbought"
                )

            elif rsi >= 70:
                reasons.append(
                    "RSI is overbought"
                )

        # ==================================================
        # MACD
        # ==================================================

        macd = indicators.get("MACD", {})

        if isinstance(macd, dict):

            trend = macd.get("Trend")

            if trend == "Bullish":
                reasons.append(
                    "MACD is bullish"
                )

            elif trend == "Bearish":
                reasons.append(
                    "MACD is bearish"
                )

        # ==================================================
        # EMA / MA
        # ==================================================

        ema = indicators.get("EMA")
        ma = indicators.get("Moving Average")

        if (
            isinstance(ema, (int, float))
            and isinstance(ma, (int, float))
        ):

            if ema > ma:
                reasons.append(
                    "EMA is above moving average"
                )

            elif ema < ma:
                reasons.append(
                    "EMA is below moving average"
                )

        # ==================================================
        # SUPERTREND
        # ==================================================

        supertrend = indicators.get(
            "SuperTrend",
            {}
        )

        if isinstance(supertrend, dict):

            trend = supertrend.get("Trend")

            if trend in ("Buy", "Strong Buy"):

                reasons.append(
                    "SuperTrend is bullish"
                )

            elif trend == "Sell":

                reasons.append(
                    "SuperTrend is bearish"
                )

        # ==================================================
        # RISK REASONS
        # ==================================================

        for reason in risk_reasons:

            if reason not in reasons:
                reasons.append(reason)

        # ==================================================
        # CONFIDENCE
        # ==================================================

        confidence = self.confidence(score)

        if risk == "HIGH":

            confidence = max(
                30,
                confidence - 15
            )

        elif risk == "MEDIUM":

            confidence = max(
                35,
                confidence - 5
            )

        # ==================================================
        # RESULT
        # ==================================================

        return {

            "signal": signal,

            "score": score,

            "risk": risk,

            "risk_score": risk_result["score"],

            "confidence": confidence,

            "reasons": reasons,

        }

    # ==================================================
    # DECISION
    # ==================================================

    def decision(self, indicators):

        result = self.generate(indicators)

        return result["signal"]

    # ==================================================
    # SHOW
    # ==================================================

    def show(self, indicators):

        result = self.generate(indicators)

        print()

        print("=" * 70)
        print("STRATEGY MANAGER")
        print("=" * 70)

        print(
            "Signal      :",
            result["signal"]
        )

        print(
            "Score       :",
            result["score"]
        )

        print(
            "Risk        :",
            result["risk"]
        )

        print(
            "Risk Score  :",
            result["risk_score"]
        )

        print(
            "Confidence  :",
            result["confidence"],
            "%"
        )

        print("-" * 70)

        print("Reasons:")

        for reason in result["reasons"]:

            print(" -", reason)

        print("=" * 70)

    # ==================================================
    # SUMMARY
    # ==================================================

    def summary(self, indicators):

        return self.generate(indicators)

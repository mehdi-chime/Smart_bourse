"""
Project : Smart_Bourse

File : signal_manager.py

Version : 3.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Legacy-compatible Signal Manager

The main decision logic belongs to:
    SignalEngine
    ScoreManager
    RiskManager
    StrategyManager

This class remains for compatibility with older modules.
"""

from strategy.score_manager import ScoreManager


class SignalManager:

    def __init__(self):

        self.score = 50

        self.signal = "HOLD"

        self.reasons = []

        self.score_manager = ScoreManager()

    # ==================================================
    # GENERATE SIGNAL
    # ==================================================

    def generate_signal(self, history):

        self.score = 50

        self.signal = "HOLD"

        self.reasons = []

        if not history or len(history) < 30:

            self.reasons.append(
                "Not enough history"
            )

            return self.signal

        last = history[-1]

        # ==================================================
        # LEGACY TREND
        # ==================================================

        trend = getattr(
            last,
            "trend",
            None
        )

        if trend == "UP TREND":

            self.score += 15

            self.reasons.append(
                "Trend Up"
            )

        elif trend == "DOWN TREND":

            self.score -= 15

            self.reasons.append(
                "Trend Down"
            )

        # ==================================================
        # LEGACY RSI
        # ==================================================

        rsi = getattr(
            last,
            "rsi",
            None
        )

        if isinstance(
            rsi,
            (int, float)
        ):

            if rsi <= 20:

                self.score += 5

                self.reasons.append(
                    "RSI Deeply Oversold"
                )

            elif rsi <= 30:

                self.score += 3

                self.reasons.append(
                    "RSI Oversold"
                )

            elif rsi >= 80:

                self.score -= 5

                self.reasons.append(
                    "RSI Deeply Overbought"
                )

            elif rsi >= 70:

                self.score -= 3

                self.reasons.append(
                    "RSI Overbought"
                )

        # ==================================================
        # CLAMP
        # ==================================================

        self.score = max(
            0,
            min(100, self.score)
        )

        # ==================================================
        # SIGNAL
        # ==================================================

        if self.score >= 80:

            self.signal = "STRONG BUY"

        elif self.score >= 65:

            self.signal = "BUY"

        elif self.score <= 20:

            self.signal = "STRONG SELL"

        elif self.score <= 35:

            self.signal = "SELL"

        else:

            self.signal = "HOLD"

        return self.signal

    # ==================================================
    # DETAILS
    # ==================================================

    def result(self):

        return {

            "signal": self.signal,

            "score": self.score,

            "reasons": self.reasons,

        }

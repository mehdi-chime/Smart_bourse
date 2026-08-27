"""
Project : Smart_Bourse

File : scenario_engine.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Scenario Engine

Converts technical market information into possible future
market scenarios.

This engine does NOT make a direct BUY/SELL decision.
It evaluates competing scenarios such as:

- continuation of the current trend
- short-term reversal
- trend reversal
- breakdown / further weakness

The purpose is to make Smart_Bourse think in terms of
possible market paths instead of relying on one indicator.
"""


class ScenarioEngine:

    def __init__(self):

        self.scenarios = []

    # ==================================================
    # RESET
    # ==================================================

    def reset(self):

        self.scenarios = []

    # ==================================================
    # NUMBER HELPER
    # ==================================================

    @staticmethod
    def _number(value):

        return isinstance(value, (int, float))

    # ==================================================
    # GENERATE
    # ==================================================

    def generate(self, analysis):

        self.reset()

        if not isinstance(analysis, dict):

            return []

        signal = analysis.get(
            "signal",
            "HOLD"
        )

        trend = analysis.get(
            "trend",
            "Unknown"
        )

        trend_strength = analysis.get(
            "trend_strength",
            "Unknown"
        )

        reversal_risk = analysis.get(
            "reversal_risk",
            "Unknown"
        )

        rsi = analysis.get("RSI")

        macd = analysis.get(
            "MACD",
            {}
        )

        ichimoku = analysis.get(
            "Ichimoku",
            {}
        )

        supertrend = analysis.get(
            "SuperTrend",
            {}
        )

        adx = analysis.get("ADX")

        # ==================================================
        # BASE PROBABILITIES
        # ==================================================

        continuation = 40
        short_reversal = 20
        full_reversal = 15
        breakdown = 25

        # ==================================================
        # TREND
        # ==================================================

        if trend == "Bearish":

            continuation += 15
            breakdown += 10

            short_reversal -= 5
            full_reversal -= 5

        elif trend == "Bullish":

            continuation += 15
            short_reversal += 5

            breakdown -= 10

        # ==================================================
        # TREND STRENGTH
        # ==================================================

        if trend_strength == "Strong":

            continuation += 10
            breakdown += 5

            short_reversal -= 5
            full_reversal -= 5

        elif trend_strength == "Weak":

            short_reversal += 5
            full_reversal += 5

        # ==================================================
        # RSI
        # ==================================================

        if self._number(rsi):

            if rsi <= 20:

                # Deep oversold does NOT automatically mean BUY.
                # It increases the probability of a bounce.

                short_reversal += 15
                continuation -= 5

            elif rsi <= 30:

                short_reversal += 10
                continuation -= 3

            elif rsi >= 80:

                short_reversal += 15
                continuation -= 5

            elif rsi >= 70:

                short_reversal += 10

        # ==================================================
        # MACD
        # ==================================================

        if isinstance(macd, dict):

            macd_trend = macd.get("Trend")

            if macd_trend == "Bearish":

                continuation += 5
                breakdown += 5

            elif macd_trend == "Bullish":

                short_reversal += 5
                full_reversal += 5

        # ==================================================
        # ICHIMOKU
        # ==================================================

        if isinstance(ichimoku, dict):

            ichimoku_trend = ichimoku.get(
                "Trend"
            )

            if ichimoku_trend == "Bearish":

                continuation += 5
                breakdown += 5

            elif ichimoku_trend == "Bullish":

                short_reversal += 5
                full_reversal += 5

        # ==================================================
        # SUPERTREND
        # ==================================================

        if isinstance(supertrend, dict):

            supertrend_trend = supertrend.get(
                "Trend"
            )

            if supertrend_trend == "Sell":

                continuation += 5
                breakdown += 5

            elif supertrend_trend in (
                "Buy",
                "Strong Buy"
            ):

                short_reversal += 5
                full_reversal += 5

        # ==================================================
        # ADX
        # ==================================================

        if self._number(adx):

            if adx >= 25:

                # Strong trend makes continuation more likely.
                continuation += 5
                breakdown += 3

            elif adx < 20:

                # Weak trend increases uncertainty/reversal.
                short_reversal += 5
                full_reversal += 3

        # ==================================================
        # STRONG SELL
        # ==================================================

        if signal == "STRONG SELL":

            continuation += 5
            breakdown += 5

        # ==================================================
        # NORMALIZE
        # ==================================================

        values = {

            "TREND_CONTINUATION": continuation,
            "SHORT_TERM_REVERSAL": short_reversal,
            "FULL_TREND_REVERSAL": full_reversal,
            "FURTHER_BREAKDOWN": breakdown,

        }

        # Remove negative probabilities.

        for key in values:

            values[key] = max(
                0,
                values[key]
            )

        total = sum(
            values.values()
        )

        if total <= 0:

            return []

        # ==================================================
        # CREATE SCENARIOS
        # ==================================================

        self.scenarios = [

            {
                "name": key,
                "probability": round(
                    (value / total) * 100,
                    2
                )
            }

            for key, value in values.items()

        ]

        # ==================================================
        # SORT
        # ==================================================

        self.scenarios.sort(
            key=lambda item:
            item["probability"],
            reverse=True
        )

        return self.scenarios

    # ==================================================
    # BEST SCENARIO
    # ==================================================

    def best_scenario(self, analysis):

        scenarios = self.generate(
            analysis
        )

        if not scenarios:

            return None

        return scenarios[0]

    # ==================================================
    # SHOW
    # ==================================================

    def show(self, analysis):

        scenarios = self.generate(
            analysis
        )

        print()

        print("=" * 70)
        print("SMART BOURSE - SCENARIO ENGINE")
        print("=" * 70)

        if not scenarios:

            print("No scenario available")

            print("=" * 70)

            return

        for scenario in scenarios:

            print(
                f"{scenario['name']:<25}"
                f": {scenario['probability']:>6.2f}%"
            )

        print("-" * 70)

        best = scenarios[0]

        print(
            "MOST LIKELY SCENARIO :",
            best["name"]
        )

        print(
            "PROBABILITY          :",
            f"{best['probability']:.2f}%"
        )

        print("=" * 70)

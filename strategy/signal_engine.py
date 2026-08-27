"""
Project : Smart_Bourse

File : signal_engine.py

Version : 0.4.0

Author :
Mehdi Jalali
ChatGPT

Description :
Combine technical indicators and generate
a unified market signal.
"""


class SignalEngine:

    def __init__(self):

        self.name = "Signal Engine"

    # --------------------------------------------------
    # MAIN CALCULATION
    # --------------------------------------------------

    def calculate(self, results, last_price):

        score = 0

        signals = {}

        warnings = []

        # =================================================
        # MOVING AVERAGE
        # Weight: 1
        # =================================================

        ma = results.get("Moving Average")

        if isinstance(ma, (int, float)):

            if last_price > ma:

                score += 1
                signals["MA"] = "Bullish"

            elif last_price < ma:

                score -= 1
                signals["MA"] = "Bearish"

            else:

                signals["MA"] = "Neutral"

        # =================================================
        # EMA
        # Weight: 1
        # =================================================

        ema = results.get("EMA")

        if isinstance(ema, (int, float)):

            if last_price > ema:

                score += 1
                signals["EMA"] = "Bullish"

            elif last_price < ema:

                score -= 1
                signals["EMA"] = "Bearish"

            else:

                signals["EMA"] = "Neutral"

        # =================================================
        # RSI
        #
        # RSI is NOT directly added to directional score.
        #
        # Oversold does not automatically mean BUY.
        # Overbought does not automatically mean SELL.
        # =================================================

        rsi = results.get("RSI")

        if isinstance(rsi, (int, float)):

            if rsi <= 20:

                signals["RSI"] = "Deeply Oversold"

                warnings.append(
                    "RSI is deeply oversold"
                )

            elif rsi <= 30:

                signals["RSI"] = "Oversold"

                warnings.append(
                    "RSI is in oversold territory"
                )

            elif rsi >= 80:

                signals["RSI"] = "Deeply Overbought"

                warnings.append(
                    "RSI is deeply overbought"
                )

            elif rsi >= 70:

                signals["RSI"] = "Overbought"

                warnings.append(
                    "RSI is in overbought territory"
                )

            else:

                signals["RSI"] = "Neutral"

        # =================================================
        # MACD
        # Weight: 2
        # =================================================

        macd = results.get("MACD")

        if isinstance(macd, dict):

            trend = macd.get("Trend")

            if trend == "Bullish":

                score += 2

            elif trend == "Bearish":

                score -= 2

            signals["MACD"] = trend

        # =================================================
        # ICHIMOKU
        # Weight: 2
        # =================================================

        ichimoku = results.get("Ichimoku")

        if isinstance(ichimoku, dict):

            trend = ichimoku.get("Trend")

            if trend == "Bullish":

                score += 2

            elif trend == "Bearish":

                score -= 2

            signals["Ichimoku"] = trend

        # =================================================
        # ADX
        #
        # ADX measures trend strength.
        # It does NOT determine direction.
        # =================================================

        adx = results.get("ADX")

        if isinstance(adx, (int, float)):

            if adx >= 40:

                signals["ADX"] = "Very Strong Trend"

            elif adx >= 25:

                signals["ADX"] = "Strong Trend"

            elif adx >= 20:

                signals["ADX"] = "Moderate Trend"

            else:

                signals["ADX"] = "Weak Trend"

        # =================================================
        # ATR
        #
        # ATR measures volatility.
        # It does NOT determine direction.
        # =================================================

        atr = results.get("ATR")

        if isinstance(atr, (int, float)):

            signals["ATR"] = round(
                atr,
                2
            )

        # =================================================
        # SUPERTREND
        # Weight: 2
        # =================================================

        supertrend = results.get("SuperTrend")

        if isinstance(supertrend, dict):

            trend = supertrend.get("Trend")

            if trend in [
                "Buy",
                "Strong Buy"
            ]:

                score += 2

            elif trend == "Sell":

                score -= 2

            signals["SuperTrend"] = trend

        # =================================================
        # FINAL SIGNAL
        #
        # Maximum score = +8
        # Minimum score = -8
        # =================================================

        if score >= 6:

            final_signal = "STRONG BUY"

        elif score >= 3:

            final_signal = "BUY"

        elif score <= -6:

            final_signal = "STRONG SELL"

        elif score <= -3:

            final_signal = "SELL"

        else:

            final_signal = "WAIT"

        # =================================================
        # TREND STATUS
        #
        # Only directional indicators participate.
        # RSI / ADX / ATR are excluded.
        # =================================================

        bullish_count = 0

        bearish_count = 0

        directional_signals = [

            signals.get("MA"),

            signals.get("EMA"),

            signals.get("MACD"),

            signals.get("Ichimoku"),

            signals.get("SuperTrend"),

        ]

        for value in directional_signals:

            if value == "Bullish":

                bullish_count += 1

            elif value == "Bearish":

                bearish_count += 1

            elif value in [
                "Buy",
                "Strong Buy"
            ]:

                bullish_count += 1

            elif value == "Sell":

                bearish_count += 1

        if bearish_count > bullish_count:

            trend_status = "Bearish"

        elif bullish_count > bearish_count:

            trend_status = "Bullish"

        else:

            trend_status = "Neutral"

        # =================================================
        # TREND STRENGTH
        # Based on ADX
        # =================================================

        if isinstance(adx, (int, float)):

            if adx >= 40:

                trend_strength = "Very Strong"

            elif adx >= 25:

                trend_strength = "Strong"

            elif adx >= 20:

                trend_strength = "Moderate"

            else:

                trend_strength = "Weak"

        else:

            trend_strength = "Unknown"

        # =================================================
        # REVERSAL RISK
        # =================================================

        if isinstance(rsi, (int, float)):

            if (
                rsi <= 30
                and trend_status == "Bearish"
            ):

                reversal_risk = "Elevated"

            elif (
                rsi >= 70
                and trend_status == "Bullish"
            ):

                reversal_risk = "Elevated"

            else:

                reversal_risk = "Normal"

        else:

            reversal_risk = "Unknown"

        # =================================================
        # EXTRA REVERSAL WARNINGS
        # =================================================

        if (
            isinstance(rsi, (int, float))
            and rsi <= 20
            and trend_status == "Bearish"
        ):

            warnings.append(
                "RSI is deeply oversold while the main trend remains bearish"
            )

        if (
            isinstance(rsi, (int, float))
            and rsi >= 80
            and trend_status == "Bullish"
        ):

            warnings.append(
                "RSI is deeply overbought while the main trend remains bullish"
            )

        # =================================================
        # CONFIDENCE
        #
        # Directional indicators:
        #
        # MA         = 1
        # EMA        = 1
        # MACD       = 2
        # Ichimoku   = 2
        # SuperTrend = 2
        #
        # Maximum = 8
        #
        # But confidence is not allowed to become
        # automatically 100% merely because all indicators
        # agree. Extreme RSI and reversal risk reduce it.
        # =================================================

        max_score = 8

        confidence = (
            abs(score)
            / max_score
        ) * 100

        # Extreme RSI means the market may be stretched.
        if (
            isinstance(rsi, (int, float))
            and (
                rsi <= 20
                or rsi >= 80
            )
        ):

            confidence -= 10

        elif (
            isinstance(rsi, (int, float))
            and (
                rsi <= 30
                or rsi >= 70
            )
        ):

            confidence -= 5

        # Weak trend reduces confidence.
        if isinstance(adx, (int, float)):

            if adx < 20:

                confidence -= 10

            elif adx < 25:

                confidence -= 5

        confidence = round(
            max(0, min(confidence, 100)),
            2
        )

        # =================================================
        # RETURN
        # =================================================

        return {

            "Signal": final_signal,

            "Score": score,

            "Confidence": confidence,

            "Trend": trend_status,

            "Trend Strength": trend_strength,

            "Reversal Risk": reversal_risk,

            "Details": signals,

            "Warnings": warnings

        }

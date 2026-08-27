"""
Project : Smart_Bourse

File : signal.py

Version : 0.1.0

Author :
Mehdi Jalali
ChatGPT

Description :
Signal Generator
"""


class Signal:

    def __init__(self):

        self.name = "Signal"

    # ----------------------------------

    def generate(self, trend, rsi):

        if trend == "UP TREND":

            if rsi < 30:

                return "STRONG BUY"

            elif rsi < 50:

                return "BUY"

            else:

                return "HOLD"

        elif trend == "DOWN TREND":

            if rsi > 70:

                return "STRONG SELL"

            elif rsi > 50:

                return "SELL"

            else:

                return "HOLD"

        return "WAIT"

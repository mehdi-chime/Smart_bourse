"""
Project : Smart_Bourse

File : trend.py

Version : 0.1.0

Author :
Mehdi Jalali
ChatGPT

Description :
Trend Analyzer
"""


class Trend:

    def __init__(self):

        self.name = "Trend"

    # ----------------------------------

    def analyze(self, close_price, moving_average):

        if close_price > moving_average:

            return "UP TREND"

        elif close_price < moving_average:

            return "DOWN TREND"

        else:

            return "SIDEWAYS"

    # ----------------------------------

    def strength(self, difference):

        difference = abs(difference)

        if difference >= 1000:

            return "VERY STRONG"

        elif difference >= 500:

            return "STRONG"

        elif difference >= 100:

            return "MEDIUM"

        else:

            return "WEAK"

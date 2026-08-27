"""
Project : Smart_Bourse

File : score.py

Version : 0.1.0

Author :
Mehdi Jalali
ChatGPT

Description :
Stock Score
"""


class Score:

    def __init__(self):

        self.name = "Score"

    # ----------------------------------

    def calculate(self, trend, signal):

        score = 0

        if trend == "UP TREND":
            score += 40

        if signal == "BUY":
            score += 30

        if signal == "STRONG BUY":
            score += 50

        if trend == "DOWN TREND":
            score -= 40

        if signal == "SELL":
            score -= 30

        if signal == "STRONG SELL":
            score -= 50

        return score

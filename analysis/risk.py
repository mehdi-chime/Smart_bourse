"""
Project : Smart_Bourse

File : risk.py

Version : 0.1.0

Author :
Mehdi Jalali
ChatGPT

Description :
Risk Management
"""


class Risk:

    def __init__(self):

        self.name = "Risk"

    # ----------------------------------

    def calculate(self, atr):

        if atr >= 500:

            return "HIGH"

        elif atr >= 200:

            return "MEDIUM"

        else:

            return "LOW"

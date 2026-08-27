"""
Project : Smart_Bourse

File : ai_engine.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
AI Decision Engine
"""


class AIEngine:

    def __init__(self):

        self.score = 0

    # --------------------------------------------------
    def decision(self, signal, risk, score):

        if signal == "BUY":

            return "BUY"

        elif signal == "SELL":

            return "SELL"

        return "HOLD"
    

    # --------------------------------------------------

    def confidence(self, score):

        if score >= 90:
            return "VERY HIGH"

        if score >= 70:
            return "HIGH"

        if score >= 50:
            return "MEDIUM"

        return "LOW"

    # --------------------------------------------------

    def show(self, signal, risk, score):

        decision = self.decision(signal, risk, score)

        print()

        print("=" * 60)

        print("AI ENGINE")

        print("=" * 60)

        print("Decision   :", decision)

        print("Confidence :", self.confidence(score))

        print("Risk       :", risk)

        print("Score      :", score)

        print("=" * 60)

        print("Reason :")

        if decision == "BUY":

            print("✓ Strategy Score Is Strong")

            print("✓ Buy Conditions Confirmed")

        elif decision == "SELL":

            print("✓ Sell Conditions Confirmed")

        else:

            print("✓ Waiting For Better Opportunity")

        print("=" * 60)    

"""
Project : Smart_Bourse

File : risk_manager.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Professional Risk Manager
"""


class RiskManager:

    def __init__(self):

        self.max_risk_percent = 2

        self.default_stop_loss = 3

        self.default_take_profit = 6

        self.capital = 100000000

    # --------------------------------------------------

    def set_capital(self, capital):

        self.capital = capital

    # --------------------------------------------------

    def stop_loss(self, buy_price):

        return round(

            buy_price *

            (1 - self.default_stop_loss / 100),

            2

        )

    # --------------------------------------------------

    def take_profit(self, buy_price):

        return round(

            buy_price *

            (1 + self.default_take_profit / 100),

            2

        )

    # --------------------------------------------------

    def max_risk(self):

        return round(

            self.capital *

            self.max_risk_percent / 100,

            2

        )

    # --------------------------------------------------

    def position_size(self,

                      buy_price,

                      stop_price):

        risk_per_share = buy_price - stop_price

        if risk_per_share <= 0:

            return 0

        volume = self.max_risk() / risk_per_share

        return int(volume)

    # --------------------------------------------------

    def portfolio_risk(self,

                       positions):

        total = 0

        for item in positions:

            total += item.get("risk", 0)

        return round(total, 2)

    # --------------------------------------------------

    def evaluate(self,

                 buy_price):

        stop = self.stop_loss(buy_price)

        target = self.take_profit(buy_price)

        volume = self.position_size(

            buy_price,

            stop

        )

        return {

            "BuyPrice": buy_price,

            "StopLoss": stop,

            "TakeProfit": target,

            "MaxRisk": self.max_risk(),

            "PositionSize": volume

        }

    # --------------------------------------------------

    def show(self,

             result):

        print()

        print("=" * 70)

        print("RISK MANAGER")

        print("=" * 70)

        print(

            "Buy Price      :",

            result["BuyPrice"]

        )

        print(

            "Stop Loss      :",

            result["StopLoss"]

        )

        print(

            "Take Profit    :",

            result["TakeProfit"]

        )

        print(

            "Max Risk       :",

            result["MaxRisk"]

        )

        print(

            "Position Size  :",

            result["PositionSize"]

        )

        print("=" * 70)

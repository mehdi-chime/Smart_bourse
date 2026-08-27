"""
Project : Smart_Bourse

File : position.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Position Object
"""


class Position:

    def __init__(

        self,

        symbol="",

        volume=0,

        buy_price=0

    ):

        self.symbol = symbol

        self.volume = volume

        self.buy_price = buy_price

        self.current_price = buy_price

    # --------------------------------------------------

    def update_price(self, price):

        self.current_price = price

    # --------------------------------------------------

    @property
    def value(self):

        return self.current_price * self.volume

    # --------------------------------------------------

    @property
    def cost(self):

        return self.buy_price * self.volume

    # --------------------------------------------------

    @property
    def profit(self):

        return self.value - self.cost

    # --------------------------------------------------

    @property
    def percent(self):

        if self.buy_price == 0:

            return 0

        return round(

            (

                (self.current_price - self.buy_price)

                / self.buy_price

            ) * 100,

            2

        )

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 60)

        print("POSITION")

        print("=" * 60)

        print("Symbol :", self.symbol)

        print("Volume :", self.volume)

        print("Buy    :", self.buy_price)

        print("Now    :", self.current_price)

        print("Profit :", self.profit)

        print("%      :", self.percent)

        print("=" * 60)

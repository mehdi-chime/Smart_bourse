"""
Project : Smart_Bourse

File : paper_trading.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Paper Trading Engine
"""


class PaperTrading:

    def __init__(self):

        self.cash = 100000000

        self.positions = []

        self.history = []

    # --------------------------------------------------

    def buy(self, symbol, price, volume):

        cost = price * volume

        if cost > self.cash:

            return False

        self.cash -= cost

        self.positions.append({

            "symbol": symbol,

            "price": price,

            "volume": volume

        })

        self.history.append({

            "type": "BUY",

            "symbol": symbol,

            "price": price,

            "volume": volume

        })

        return True

    # --------------------------------------------------

    def sell(self, symbol, price):

        for position in self.positions:

            if position["symbol"] == symbol:

                profit = (

                    price -

                    position["price"]

                ) * position["volume"]

                self.cash += (

                    price *

                    position["volume"]

                )

                self.history.append({

                    "type": "SELL",

                    "symbol": symbol,

                    "price": price,

                    "volume": position["volume"],

                    "profit": round(profit, 2)

                })

                self.positions.remove(position)

                return profit

        return None

    # --------------------------------------------------

    def total_profit(self):

        profit = 0

        for trade in self.history:

            if trade["type"] == "SELL":

                profit += trade["profit"]

        return round(profit, 2)

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)

        print("PAPER TRADING")

        print("=" * 70)

        print("Cash :", self.cash)

        print("Profit :", self.total_profit())

        print()

        for position in self.positions:

            print(position)

        print("=" * 70)

    # --------------------------------------------------

    def show_history(self):

        print()

        print("=" * 70)

        print("TRADE HISTORY")

        print("=" * 70)

        for trade in self.history:

            print(trade)

        print("=" * 70)

"""
Project : Smart_Bourse

File : portfolio.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Portfolio Manager
"""

import json
import os


class Portfolio:

    def __init__(self):

        self.assets = []

        self.file_path = "data/portfolio.json"

        os.makedirs("data", exist_ok=True)

    # --------------------------------------------------

    def buy(self, symbol, price, volume):

        for asset in self.assets:

            if asset["symbol"] == symbol:

                total_cost = asset["avg_price"] * asset["volume"]

                total_cost += price * volume

                asset["volume"] += volume

                asset["avg_price"] = round(
                    total_cost / asset["volume"], 2
                )

                return

        self.assets.append({

            "symbol": symbol,

            "avg_price": price,

            "volume": volume

        })

    # --------------------------------------------------

    def sell(self, symbol, volume):

        for asset in self.assets:

            if asset["symbol"] == symbol:

                asset["volume"] -= volume

                if asset["volume"] <= 0:

                    self.assets.remove(asset)

                return

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)

        print("PORTFOLIO")

        print("=" * 70)

        if len(self.assets) == 0:

            print("Portfolio Is Empty")

        else:

            for asset in self.assets:

                print(
                    f'{asset["symbol"]:10} | '
                    f'Volume : {asset["volume"]:8} | '
                    f'Average : {asset["avg_price"]}'
                )

        print("=" * 70)

    # --------------------------------------------------

    def profit_loss(self, prices):

        report = []

        for asset in self.assets:

            symbol = asset["symbol"]

            if symbol not in prices:

                continue

            current = prices[symbol]

            profit = (
                current - asset["avg_price"]
            ) * asset["volume"]

            percent = (
                (current - asset["avg_price"])
                / asset["avg_price"]
            ) * 100

            report.append({

                "symbol": symbol,

                "profit": round(profit, 2),

                "percent": round(percent, 2)

            })

        return report

    # --------------------------------------------------

    def save(self):

        with open(

            self.file_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                self.assets,

                file,

                indent=4,

                ensure_ascii=False

            )

    # --------------------------------------------------

    def load(self):

        if not os.path.exists(self.file_path):

            return

        with open(

            self.file_path,

            "r",

            encoding="utf-8"

        ) as file:

            self.assets = json.load(file)

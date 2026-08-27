"""
Project : Smart_Bourse

File : portfolio.py

Version : 0.1.0

Author :
Mehdi Jalali
ChatGPT

Description :
Portfolio Manager
"""


class Portfolio:

    def __init__(self):

        self.stocks = []

    # ----------------------------------

    def add(self, symbol):

        self.stocks.append(symbol)

    # ----------------------------------

    def show(self):

        print()

        print("=" * 40)

        print("Portfolio")

        print("=" * 40)

        for stock in self.stocks:

            print(stock)

        print("=" * 40)

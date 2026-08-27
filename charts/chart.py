"""
Project : Smart_Bourse

File : chart.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Chart Manager
"""

import matplotlib.pyplot as plt


class Chart:

    def __init__(self):

        pass

    # --------------------------------------------------

    def price_chart(self, stocks):

        dates = []
        prices = []

        for stock in stocks:

            dates.append(stock.trade_date)
            prices.append(stock.close_price)

        plt.figure(figsize=(12, 5))

        plt.plot(

            dates,

            prices,

            linewidth=2,

            label="Close Price"

        )

        plt.title("Price Chart")

        plt.xlabel("Date")

        plt.ylabel("Price")

        plt.grid(True)

        plt.legend()

        plt.tight_layout()

        plt.show()

    # --------------------------------------------------

    def ma_chart(self, prices, ma):

        plt.figure(figsize=(12, 5))

        plt.plot(prices, label="Price")

        plt.plot(ma, label="MA")

        plt.grid(True)

        plt.legend()

        plt.tight_layout()

        plt.show()

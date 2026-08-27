"""
Project : Smart_Bourse

File : stock.py

Version : 0.0.8

Author :
Mehdi Jalali
ChatGPT

Description :
Stock Model
"""


class Stock:

    def __init__(self):

        self.symbol = ""

        self.trade_date = ""

        self.open_price = 0

        self.high_price = 0

        self.low_price = 0

        self.close_price = 0

        self.volume = 0

    def __str__(self):

        return (
            f"{self.symbol} | "
            f"{self.trade_date} | "
            f"{self.close_price}"
        )

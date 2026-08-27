"""
Project : Smart_Bourse

File : performance_report.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Performance Report
"""


class PerformanceReport:

    def __init__(self):

        self.total_profit = 0

        self.total_trade = 0

        self.win = 0

        self.loss = 0

    # --------------------------------------------------

    def add_trade(self, profit):

        self.total_trade += 1

        self.total_profit += profit

        if profit > 0:

            self.win += 1

        else:

            self.loss += 1

    # --------------------------------------------------

    def win_rate(self):

        if self.total_trade == 0:

            return 0

        return round(

            self.win /

            self.total_trade * 100,

            2

        )

    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)

        print("PERFORMANCE REPORT")

        print("=" * 70)

        print("Trades :", self.total_trade)

        print("Win    :", self.win)

        print("Loss   :", self.loss)

        print("Profit :", round(self.total_profit, 2))

        print("WinRate:", self.win_rate(), "%")

        print("=" * 70)

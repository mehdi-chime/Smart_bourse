"""
Project : Smart_Bourse

File : backtest_engine.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
BackTest Engine
"""

from strategy.strategy_manager import StrategyManager

from indicators.indicator_manager import IndicatorManager

class BackTestEngine:

    def __init__(self):

        self.strategy = StrategyManager()

        self.indicators = IndicatorManager()

        self.initial_cash = 100000000

        self.cash = self.initial_cash

        self.position = 0

        self.buy_price = 0

        self.total_profit = 0

        self.total_trade = 0

        self.win_trade = 0

        self.loss_trade = 0

        self.history = []

    # --------------------------------------------------

    def reset(self):

        self.cash = self.initial_cash

        self.position = 0

        self.buy_price = 0

        self.total_profit = 0

        self.total_trade = 0

        self.win_trade = 0

        self.loss_trade = 0

        self.history.clear()

    # --------------------------------------------------

    def buy(self, price):

        if self.position != 0:

            return

        risk_percent = 0.20

        invest = self.cash * risk_percent

        volume = int(invest / price)        

        if volume <= 0:

            return

        self.position = volume

        self.buy_price = price

        self.cash -= volume * price

        self.history.append({

            "type": "BUY",

            "price": price,

            "volume": volume

        })

    # --------------------------------------------------

    def sell(self, price):

        if self.position == 0:

            return

        value = self.position * price

        profit = (price - self.buy_price) * self.position

        self.cash += value

        self.total_profit += profit

        self.total_trade += 1

        if profit >= 0:

            self.win_trade += 1

        else:

            self.loss_trade += 1

        self.history.append({

            "type": "SELL",

            "price": price,

            "profit": round(profit, 2)

        })

        self.position = 0


        self.buy_price = 0

            # --------------------------------------------------

    def equity(self, last_price):

        if self.position == 0:

            return self.cash

        return self.cash + self.position * last_price

    # --------------------------------------------------

    def run(self, stocks):

        self.reset()

        prices = []

        for stock in stocks:

            prices.append(stock.close_price)

        for i in range(60, len(stocks)):

            current = stocks[i]

            history = stocks[:i + 1]
            indicator_result = self.indicators.run(history)

            signal = self.strategy.generate(indicator_result)

            if signal["signal"] == "BUY":

                self.buy(current.close_price)

            elif signal["signal"] == "SELL":

                self.sell(current.close_price)
         

        if self.position != 0:

            self.sell(stocks[-1].close_price)

        self.report()

        self.show_history()

        return self.total_profit

    # --------------------------------------------------

    def win_rate(self):

        if self.total_trade == 0:

            return 0

        return round(

            self.win_trade /

            self.total_trade * 100,

            2

        )

    # --------------------------------------------------

    def loss_rate(self):

        if self.total_trade == 0:

            return 0

        return round(

            self.loss_trade /

            self.total_trade * 100,

            2

        )
        # --------------------------------------------------

    def max_drawdown(self):

        equity = self.initial_cash

        peak = equity

        drawdown = 0

        for trade in self.history:

            if trade["type"] == "SELL":

                equity += trade["profit"]

                if equity > peak:

                    peak = equity

                dd = peak - equity

                if dd > drawdown:

                    drawdown = dd

        return round(drawdown, 2)

    # --------------------------------------------------

    def profit_factor(self):

        profit = 0

        loss = 0

        for trade in self.history:

            if trade["type"] != "SELL":

                continue

            if trade["profit"] >= 0:

                profit += trade["profit"]

            else:

                loss += abs(trade["profit"])

        if loss == 0:

            return profit

        return round(profit / loss, 2)

    # --------------------------------------------------

    def final_cash(self):

        return round(self.cash, 2)

    # --------------------------------------------------

    def total_return(self):

        value = self.final_cash()

        return round(

            (

                value -

                self.initial_cash

            )

            /

            self.initial_cash

            * 100,

            2

        )
        # --------------------------------------------------

    def report(self):

        print()

        print("=" * 80)

        print("BACKTEST REPORT")

        print("=" * 80)

        print("Initial Cash   :", self.initial_cash)
        print("Final Cash     :", self.final_cash())
        print("Net Profit     :", round(self.total_profit, 2))
        print("Return %       :", self.total_return())

        print("-" * 80)

        print("Trades         :", self.total_trade)
        print("Win Trades     :", self.win_trade)
        print("Loss Trades    :", self.loss_trade)

        print("Win Rate       :", self.win_rate(), "%")
        print("Loss Rate      :", self.loss_rate(), "%")

        print("-" * 80)

        print("Profit Factor  :", self.profit_factor())
        print("Max Drawdown   :", self.max_drawdown())

        print("=" * 80)

    # --------------------------------------------------

    def show_history(self):

        print()

        print("=" * 80)

        print("TRADE HISTORY")

        print("=" * 80)

        for trade in self.history:

            print(trade)

        print("=" * 80)
    

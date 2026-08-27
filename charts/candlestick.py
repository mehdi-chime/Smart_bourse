"""
Project : Smart_Bourse

File : candlestick.py

Version : 1.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Candlestick Chart
"""

import mplfinance as mpf
import pandas as pd


class CandleStick:

    def __init__(self):

        pass

    # --------------------------------------------------

    def show(self, stocks):

        data = []

        for stock in stocks:

            data.append({

                "Date": stock.trade_date,

                "Open": stock.open_price,

                "High": stock.high_price,

                "Low": stock.low_price,

                "Close": stock.close_price,

                "Volume": stock.volume

            })

        df = pd.DataFrame(data)

        df["Date"] = pd.to_datetime(df["Date"])

        df.set_index("Date", inplace=True)

        mpf.plot(

            df,

            type="candle",

            volume=True,

            style="yahoo",

            figsize=(12, 7)

        )

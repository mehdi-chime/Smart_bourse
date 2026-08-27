"""
Project : Smart_Bourse

File : history_database.py

Version : 1.1.0

Author :
Mehdi Jalali
ChatGPT

Description :
History Database Manager
"""

import sqlite3
import os
from pathlib import Path

from project_config import PROJECT_PATH


class HistoryDatabase:

    def __init__(self):

        self.db_path = Path(PROJECT_PATH) / "data" / "smart_bourse.db"

        self.connection = None
        self.cursor = None

        os.makedirs(
            Path(PROJECT_PATH) / "data" / "history",
            exist_ok=True
        )

    # --------------------------------------------------
    # CONNECT
    # --------------------------------------------------

    def connect(self):

        self.connection = sqlite3.connect(self.db_path)

        self.cursor = self.connection.cursor()

        print("History Database Connected")

    # --------------------------------------------------
    # COMMIT
    # --------------------------------------------------

    def commit(self):

        if self.connection:

            self.connection.commit()

    # --------------------------------------------------
    # CLOSE
    # --------------------------------------------------

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None
            self.cursor = None

            print("History Database Closed")

    # --------------------------------------------------
    # CREATE TABLES
    # --------------------------------------------------

    def create_tables(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS stocks_history(

            symbol TEXT,

            trade_date TEXT,

            open_price REAL,

            high_price REAL,

            low_price REAL,

            close_price REAL,

            volume INTEGER,

            PRIMARY KEY(symbol, trade_date)

        )

        """)

        self.commit()

        print("History Table Ready")

    # --------------------------------------------------
    # INSERT ONE
    # --------------------------------------------------

    def insert_history(self, stock):

        self.cursor.execute("""

        INSERT INTO stocks_history(

            symbol,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume

        )

        VALUES(?,?,?,?,?,?,?)

        """, (

            stock.symbol,
            stock.trade_date,
            stock.open_price,
            stock.high_price,
            stock.low_price,
            stock.close_price,
            stock.volume

        ))

        self.commit()

    # --------------------------------------------------
    # INSERT MANY
    # --------------------------------------------------

    def insert_many(self, stocks):

        if not stocks:

            return

        data = []

        for stock in stocks:

            data.append((

                stock.symbol,
                stock.trade_date,
                stock.open_price,
                stock.high_price,
                stock.low_price,
                stock.close_price,
                stock.volume

            ))

        self.cursor.executemany("""

        INSERT INTO stocks_history(

            symbol,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume

        )

        VALUES(?,?,?,?,?,?,?)

        """, data)

        self.commit()

    # --------------------------------------------------
    # DELETE SYMBOL
    # --------------------------------------------------

    def delete_symbol(self, symbol):

        self.cursor.execute(

            "DELETE FROM stocks_history WHERE symbol=?",

            (symbol,)

        )

        self.commit()

    # --------------------------------------------------
    # DELETE DATE
    # --------------------------------------------------

    def delete_date(self, trade_date):

        self.cursor.execute(

            "DELETE FROM stocks_history WHERE trade_date=?",

            (trade_date,)

        )

        self.commit()

    # --------------------------------------------------
    # GET HISTORY
    # --------------------------------------------------

    def get_history(self, symbol, days=None):

        print("get_history:", symbol)

        # --------------------------------------------------
        # ALL HISTORY
        # --------------------------------------------------

        if days is None:

            self.cursor.execute("""

            SELECT *

            FROM stocks_history

            WHERE symbol=?

            ORDER BY trade_date ASC

            """, (symbol,))

        # --------------------------------------------------
        # LAST N DAYS
        # --------------------------------------------------

        else:

            self.cursor.execute("""

            SELECT *

            FROM (

                SELECT *

                FROM stocks_history

                WHERE symbol=?

                ORDER BY trade_date DESC

                LIMIT ?

            )

            ORDER BY trade_date ASC

            """, (symbol, days))

        rows = self.cursor.fetchall()

        print("rows:", len(rows))

        # --------------------------------------------------
        # CONVERT TO STOCK OBJECTS
        # --------------------------------------------------

        from models.stock import Stock

        stocks = []

        for row in rows:

            stock = Stock()

            stock.symbol = row[0]

            stock.trade_date = row[1]

            stock.open_price = row[2]

            stock.high_price = row[3]

            stock.low_price = row[4]

            stock.close_price = row[5]

            stock.volume = row[6]

            stocks.append(stock)

        return stocks

    # --------------------------------------------------
    # GET SYMBOLS
    # --------------------------------------------------

    def get_symbols(self):

        self.cursor.execute("""

        SELECT DISTINCT symbol

        FROM stocks_history

        ORDER BY symbol

        """)

        rows = self.cursor.fetchall()

        return [row[0] for row in rows]

    # --------------------------------------------------
    # GET LAST PRICE
    # --------------------------------------------------

    def get_last_price(self, symbol):

        self.cursor.execute("""

        SELECT close_price

        FROM stocks_history

        WHERE symbol=?

        ORDER BY trade_date DESC

        LIMIT 1

        """, (symbol,))

        row = self.cursor.fetchone()

        if row:

            return row[0]

        return None

    # --------------------------------------------------
    # GET LAST RECORD
    # --------------------------------------------------

    def get_last_record(self, symbol):

        self.cursor.execute("""

        SELECT *

        FROM stocks_history

        WHERE symbol=?

        ORDER BY trade_date DESC

        LIMIT 1

        """, (symbol,))

        row = self.cursor.fetchone()

        return row

    # --------------------------------------------------
    # GET CLOSE PRICES
    # --------------------------------------------------

    def get_close_prices(self, symbol, days=None):

        rows = self.get_history(symbol, days)

        prices = []

        for stock in rows:

            prices.append(stock.close_price)

        return prices

    # --------------------------------------------------
    # SHOW
    # --------------------------------------------------

    def show(self):

        print()

        print("=" * 70)
        print("HISTORY DATABASE")
        print("=" * 70)

        symbols = self.get_symbols()

        print("Symbols :", len(symbols))

        for symbol in symbols:

            count = len(
                self.get_history(symbol)
            )

            print(
                f"{symbol:10} -> {count} Records"
            )

        print("=" * 70)

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    def status(self):

        symbols = self.get_symbols()

        total = 0

        for symbol in symbols:

            total += len(
                self.get_history(symbol)
            )

        return {

            "symbols": len(symbols),

            "records": total

        }

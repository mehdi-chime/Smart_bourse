"""
Project : Smart_Bourse

File : database.py

Version : 0.0.9.2

Author :
Mehdi Jalali
ChatGPT

Description :
Database Manager
"""

from pathlib import Path
import sqlite3

from project_config import PROJECT_PATH


class Database:

    def __init__(self):

        self.data_folder = Path(PROJECT_PATH) / "data"

        self.data_folder.mkdir(exist_ok=True)

        self.database_file = self.data_folder / "smart_bourse.db"

        self.connection = None

        self.cursor = None

    # ----------------------------------

    def connect(self):

        self.connection = sqlite3.connect(self.database_file)

        self.cursor = self.connection.cursor()

        print("Database Connected")

    # ----------------------------------
    def create_symbol_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS symbols(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT UNIQUE,

            company TEXT,

            isin TEXT,

            company_isin TEXT,

            inscode TEXT,

            market TEXT,

            board TEXT,

            instrument_type TEXT,

            sector_code TEXT,

            sector_name TEXT,

            sub_sector TEXT

        )
        """)

        self.connection.commit()

        print("Table 'symbols' is ready.")

    # ----------------------------------
    def create_tables(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS stocks(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT NOT NULL,

            trade_date TEXT NOT NULL,

            open_price REAL,

            high_price REAL,

            low_price REAL,

            close_price REAL,

            volume INTEGER

        )

        """)

        self.connection.commit()

        print("Table 'stocks' is ready.")

        # ----------------------------

        self.create_symbol_table()
   

    # ----------------------------------

    def stock_exists(self, stock):

        sql = """

        SELECT COUNT(*)

        FROM stocks

        WHERE symbol = ?

        AND trade_date = ?

        """

        self.cursor.execute(

            sql,

            (stock.symbol, stock.trade_date)

        )

        count = self.cursor.fetchone()[0]

        return count > 0

    # ----------------------------------

    def insert_stock(self, stock):

        if self.stock_exists(stock):

            print(f"{stock.symbol} already exists.")

            return

        sql = """

        INSERT INTO stocks(

            symbol,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume

        )

        VALUES(?,?,?,?,?,?,?)

        """

        self.cursor.execute(

            sql,

            (

                stock.symbol,
                stock.trade_date,
                stock.open_price,
                stock.high_price,
                stock.low_price,
                stock.close_price,
                stock.volume

            )

        )

        self.connection.commit()

        print(f"{stock.symbol} saved.")

    # ----------------------------------

    def get_all_stocks(self):

        self.cursor.execute("""

        SELECT

            symbol,
            trade_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume

        FROM stocks

        ORDER BY trade_date

        """)

        return self.cursor.fetchall()

    # ----------------------------------
    def get_history(self, symbol, days=None):

        if days is None:

            self.cursor.execute(

                """

                SELECT

                    symbol,
                    trade_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume

                FROM stocks

                WHERE symbol=?

                ORDER BY trade_date

                """,

                (symbol,)

            )

        else:

            self.cursor.execute(

                """

                SELECT

                    symbol,
                    trade_date,
                    open_price,
                    high_price,
                    low_price,
                    close_price,
                    volume

                FROM stocks

                WHERE symbol=?

                ORDER BY trade_date DESC

                LIMIT ?

                """,

                (symbol, days)

            )

        rows = self.cursor.fetchall()

        stocks = []

        from models.stock import Stock

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
        # ----------------------------------

    def delete_stock(self, symbol, trade_date):

        self.cursor.execute(

            """

            DELETE FROM stocks

            WHERE symbol = ?

            AND trade_date = ?

            """,

            (symbol, trade_date)

        )

        self.connection.commit()

        print(f"{symbol} deleted.")

    # ----------------------------------

    def delete_by_date(self, trade_date):

        self.cursor.execute(

            """

            DELETE FROM stocks

            WHERE trade_date = ?

            """,

            (trade_date,)

        )

        self.connection.commit()

        print(f"All stocks of {trade_date} deleted.")

    # ----------------------------------

    def close(self):

        if self.connection:

            self.connection.close()

            print("Database Closed")

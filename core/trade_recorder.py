"""
core/trade_recorder.py
ذخیره‌سازی و تحلیل معاملات انجام‌شده در طول روز
"""

import sqlite3
from datetime import datetime

class TradeRecorder:
    def __init__(self, db_path="data/trades.db"):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                trade_type TEXT,
                price REAL,
                volume INTEGER,
                value REAL,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

    def record_trade(self, symbol, trade_type, price, volume):
        """ثبت یک معامله"""
        value = price * volume
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades (symbol, trade_type, price, volume, value, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (symbol, trade_type, price, volume, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"✅ معامله {symbol} - {trade_type} - {volume} سهم در {price:,.0f} ثبت شد.")

    def get_today_trades(self):
        """دریافت معاملات امروز"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM trades 
            WHERE timestamp > datetime('now', 'start of day')
            ORDER BY timestamp
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

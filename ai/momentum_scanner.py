"""
ai/momentum_scanner.py
تشخیص سهام با شتاب قیمتی در بازه‌های کوتاه‌مدت
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class MomentumScanner:
    def __init__(self, db_path="data/market_data.db"):
        self.db_path = db_path

    def get_latest_data(self, symbol, minutes=5):
        """دریافت داده‌های چند دقیقه اخیر یک سهم"""
        conn = sqlite3.connect(self.db_path)
        query = f"""
            SELECT price, timestamp FROM live_data 
            WHERE symbol = '{symbol}'
            AND timestamp > datetime('now', '-{minutes} minutes')
            ORDER BY timestamp
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def calculate_momentum(self, symbol, windows=[1, 3, 5]):
        """محاسبه شتاب قیمت در بازه‌های مختلف"""
        results = {}
        for w in windows:
            df = self.get_latest_data(symbol, w)
            if len(df) < 2:
                results[w] = None
                continue
            start_price = df.iloc[0]['price']
            end_price = df.iloc[-1]['price']
            change_percent = ((end_price - start_price) / start_price) * 100
            results[w] = {
                'change_percent': change_percent,
                'start_price': start_price,
                'end_price': end_price,
                'records': len(df)
            }
        return results

    def scan_all(self, symbols, min_momentum=0.5):
        """اسکن همه سهام و پیدا کردن سهام با شتاب بالا"""
        candidates = []
        for symbol in symbols:
            momentum = self.calculate_momentum(symbol)
            if momentum.get(3) and abs(momentum[3]['change_percent']) >= min_momentum:
                candidates.append({
                    'symbol': symbol,
                    'momentum_1m': momentum.get(1),
                    'momentum_3m': momentum.get(3),
                    'momentum_5m': momentum.get(5)
                })
        candidates.sort(key=lambda x: abs(x['momentum_3m']['change_percent']), reverse=True)
        return candidates[:10]

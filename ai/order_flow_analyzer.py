"""
ai/order_flow_analyzer.py
تحلیل جریان سفارشات و تشخیص فشار خرید و فروش
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

class OrderFlowAnalyzer:
    def __init__(self, db_path="data/market_data.db"):
        self.db_path = db_path
    
    def get_recent_data(self, symbol="خگستر", minutes=5):
        """دریافت داده‌های چند دقیقه اخیر"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = f"""
                SELECT * FROM live_data 
                WHERE symbol = '{symbol}'
                AND timestamp > datetime('now', '-{minutes} minutes')
                ORDER BY timestamp
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except:
            return pd.DataFrame()
    
    def get_last_price(self, symbol="خگستر"):
        """دریافت آخرین قیمت ثبت‌شده"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = f"""
                SELECT price, timestamp FROM live_data 
                WHERE symbol = '{symbol}'
                ORDER BY timestamp DESC
                LIMIT 1
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            if not df.empty:
                return df.iloc[0]['price'], df.iloc[0]['timestamp']
        except:
            pass
        return 0, None
    
    def analyze_pressure(self, symbol="خگستر", minutes=5):
        """تحلیل فشار خرید و فروش"""
        df = self.get_recent_data(symbol, minutes)
        
        if df.empty:
            last_price, last_time = self.get_last_price(symbol)
            return {
                "signal": "NEUTRAL",
                "pressure": 0.5,
                "avg_buy": 0,
                "avg_sell": 0,
                "records": 0,
                "last_price": last_price,
                "last_time": last_time
            }
        
        avg_buy = df['buy_volume'].mean() if 'buy_volume' in df else 0
        avg_sell = df['sell_volume'].mean() if 'sell_volume' in df else 0
        
        if avg_sell == 0:
            pressure = 0.5
        else:
            pressure = avg_buy / avg_sell
        
        if pressure > 1.2:
            signal = "BUY"
        elif pressure < 0.8:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        last_price = df.iloc[-1]['price'] if 'price' in df else 0
        last_time = df.iloc[-1]['timestamp'] if 'timestamp' in df else None
        
        return {
            "signal": signal,
            "pressure": round(pressure, 2),
            "avg_buy": int(avg_buy),
            "avg_sell": int(avg_sell),
            "records": len(df),
            "last_price": last_price,
            "last_time": last_time
        }

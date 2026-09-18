"""
core/logger.py
مدیریت لاگ‌های پروژه - نسخه نهایی
"""

import os
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        self.console_lines = []

    def log(self, message, to_console=False):
        """ذخیره پیام در فایل لاگ و در صورت نیاز نمایش در کنسول"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
        
        if to_console:
            print(message)

    def log_symbol(self, symbol, data):
        """ذخیره‌ی اطلاعات یک نماد در فایل لاگ (به‌صورت خلاصه)"""
        self.log(f"SYMBOL: {symbol} | INSCODE: {data.get('inscode', 'N/A')} | ISIN: {data.get('isin', 'N/A')}")

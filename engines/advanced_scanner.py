"""
engines/advanced_scanner.py
موتور جستجوی پیشرفته - بررسی همه سهام با داده‌های ۳۶۵ روزه
نسخه ۱.۰ - تحلیل جامع بازار و معرفی ۱۰ سهم برتر
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from history.history_database import HistoryDatabase
from database.database import Database
from indicators.indicator_manager import IndicatorManager
from analysis.support_resistance import SupportResistanceAnalyzer
from analysis.trend import TrendAnalyzer

class AdvancedScanner:
    def __init__(self, config=None):
        self.config = config or self.default_config()
        self.results = []
        self.indicators = IndicatorManager()
        self.sr_analyzer = SupportResistanceAnalyzer()
        self.trend_analyzer = TrendAnalyzer()

    def default_config(self):
        return {
            "min_days": 200,  # حداقل روزهای داده
            "min_volume": 10_000_000_000,  # حداقل حجم معاملات (۱۰ میلیارد تومان)
            "max_pe": 15,  # حداکثر P/E
            "weights": {
                "trend": 0.20,
                "rsi": 0.15,
                "macd": 0.15,
                "volume": 0.10,
                "support_resistance": 0.20,
                "smart_money": 0.20
            }
        }

    def get_all_symbols(self):
        """دریافت لیست همه نمادها از دیتابیس"""
        db = Database()
        db.connect()
        symbols = db.get_all_symbols()
        db.close()
        return symbols

    def get_history(self, symbol, days=365):
        """دریافت تاریخچه قیمت یک سهم"""
        history_db = HistoryDatabase()
        history_db.connect()
        stocks = history_db.get_history(symbol, days)
        history_db.close()
        return stocks

    def calculate_indicators(self, data):
        """محاسبه اندیکاتورها برای یک سهم"""
        return self.indicators.run(data)

    def calculate_score(self, stock, indicators):
        """محاسبه امتیاز نهایی برای یک سهم"""
        score = 0
        reasons = []

        # ۱. روند
        trend = indicators.get('Trend', '')
        if 'UP' in trend:
            score += 10
            reasons.append("روند صعودی")
        elif 'DOWN' in trend:
            score += 2
            reasons.append("روند نزولی")

        # ۲. RSI
        rsi = indicators.get('RSI', 50)
        if 30 < rsi < 70:
            score += 8
            reasons.append(f"RSI در محدوده نرمال ({rsi:.1f})")
        elif rsi <= 30:
            score += 5
            reasons.append(f"RSI اشباع فروش ({rsi:.1f})")
        elif rsi >= 70:
            score += 2
            reasons.append(f"RSI اشباع خرید ({rsi:.1f})")

        # ۳. MACD
        macd = indicators.get('MACD', {})
        if macd.get('Trend') == 'Bullish':
            score += 10
            reasons.append("MACD صعودی")
        elif macd.get('Trend') == 'Bearish':
            score += 2
            reasons.append("MACD نزولی")

        # ۴. حجم
        close_price = indicators.get('close', 0)
        volume = indicators.get('volume', 0)
        if volume > self.config["min_volume"]:
            score += 8
            reasons.append("حجم بالا")
        else:
            score += 3

        # ۵. حمایت و مقاومت
        sr = self.sr_analyzer.calculate(indicators.get('close_prices', []))
        if sr.get('near_support', False):
            score += 10
            reasons.append(f"نزدیک به حمایت ({sr.get('support_level', 0):,.0f})")
        if sr.get('near_resistance', False):
            score += 5
            reasons.append(f"نزدیک به مقاومت ({sr.get('resistance_level', 0):,.0f})")

        # ۶. پول هوشمند (اگر داده باشد)
        smart_money = stock.get('smart_money_ratio', 0.5)
        if smart_money > 0.6:
            score += 8
            reasons.append("پول هوشمند در حال ورود")

        return {
            "score": min(100, score * 2),
            "reasons": reasons[:5]  # فقط ۵ دلیل اول
        }

    def scan_all(self):
        """اسکن همه سهام و محاسبه امتیاز"""
        symbols = self.get_all_symbols()
        print(f"🔍 شروع اسکن {len(symbols)} سهم...")
        
        results = []
        total = len(symbols)
        for idx, symbol_row in enumerate(symbols):
            symbol_name = symbol_row[1]
            if idx % 50 == 0:
                print(f"   پردازش {idx}/{total} ...")
            
            # دریافت داده‌ها
            stocks = self.get_history(symbol_name, 365)
            if len(stocks) < self.config["min_days"]:
                continue
            
            # محاسبه اندیکاتورها
            indicators = self.calculate_indicators(stocks)
            if not indicators:
                continue
            
            # محاسبه امتیاز
            stock_data = {
                'symbol': symbol_name,
                'close_price': stocks[-1].close_price,
                'volume': stocks[-1].volume,
                'smart_money_ratio': 0.5  # مقدار پیش‌فرض
            }
            score_result = self.calculate_score(stock_data, indicators)
            
            results.append({
                'symbol': symbol_name,
                'price': stocks[-1].close_price,
                'score': score_result['score'],
                'reasons': score_result['reasons'],
                'volume': stocks[-1].volume,
                'change': ((stocks[-1].close_price - stocks[0].close_price) / stocks[0].close_price) * 100
            })
        
        # مرتب‌سازی بر اساس امتیاز
        results.sort(key=lambda x: x['score'], reverse=True)
        self.results = results
        return results

    def get_top_swings(self, n=10):
        """۱۰ سهم برتر برای نوسان‌گیری"""
        # برای نوسان‌گیری، سهام با حجم بالا و نوسان زیاد
        swing_candidates = [r for r in self.results if r['volume'] > self.config["min_volume"]]
        swing_candidates.sort(key=lambda x: abs(x['change']), reverse=True)
        return swing_candidates[:n]

    def get_top_long_term(self, n=10):
        """۱۰ سهم برتر برای سرمایه‌گذاری بلندمدت"""
        # برای بلندمدت، سهام با امتیاز بالا و روند صعودی
        long_candidates = [r for r in self.results if r['score'] > 50]
        long_candidates.sort(key=lambda x: x['score'], reverse=True)
        return long_candidates[:n]

    def report(self):
        """گزارش نهایی"""
        if not self.results:
            return "❌ هیچ داده‌ای برای تحلیل پیدا نشد."

        lines = [
            "=" * 70,
            "📊 گزارش اسکنر پیشرفته بازار",
            "=" * 70,
            f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"📈 تعداد سهام بررسی‌شده: {len(self.results)}",
            "=" * 70
        ]

        # ۱۰ سهم برای نوسان‌گیری
        lines.append("\n🎯 ۱۰ سهم برتر برای نوسان‌گیری روزانه:")
        lines.append("-" * 60)
        for i, r in enumerate(self.get_top_swings(10), 1):
            lines.append(f"{i}. {r['symbol']} | قیمت: {r['price']:,.0f} | تغییر: {r['change']:+.2f}% | حجم: {r['volume']:,}")
            lines.append(f"   امتیاز: {r['score']:.1f} | دلایل: {', '.join(r['reasons'])}")
            lines.append("")

        # ۱۰ سهم برای سرمایه‌گذاری
        lines.append("\n🏦 ۱۰ سهم برتر برای سرمایه‌گذاری بلندمدت:")
        lines.append("-" * 60)
        for i, r in enumerate(self.get_top_long_term(10), 1):
            lines.append(f"{i}. {r['symbol']} | قیمت: {r['price']:,.0f} | تغییر: {r['change']:+.2f}%")
            lines.append(f"   امتیاز: {r['score']:.1f} | دلایل: {', '.join(r['reasons'])}")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)


# ========== بخش تست ==========
if __name__ == "__main__":
    scanner = AdvancedScanner()
    scanner.scan_all()
    print(scanner.report())

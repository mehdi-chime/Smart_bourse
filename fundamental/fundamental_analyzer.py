"""
fundamental/fundamental_analyzer.py
تحلیل بنیادی با استفاده از داده‌های کدال (از فایل CSV)
"""

import pandas as pd
import os
from datetime import datetime

class FundamentalAnalyzer:
    def __init__(self, csv_path=None):
        # تنظیم مسیر مطلق برای فایل CSV
        if csv_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.csv_path = os.path.join(base_dir, "data", "fundamental_data.csv")
        else:
            self.csv_path = csv_path
        self.data = {}
        self.df = pd.DataFrame()
        self.load_data()

    def load_data(self):
        """بارگذاری داده‌های بنیادی از فایل CSV"""
        if os.path.exists(self.csv_path):
            try:
                self.df = pd.read_csv(self.csv_path)
                print(f"✅ داده‌های بنیادی از {self.csv_path} بارگذاری شد.")
                print(f"📊 تعداد رکوردها: {len(self.df)}")
            except Exception as e:
                print(f"❌ خطا در بارگذاری داده‌های بنیادی: {e}")
                self.df = pd.DataFrame()
        else:
            print(f"⚠️ فایل {self.csv_path} پیدا نشد. از داده‌های پیش‌فرض استفاده می‌شود.")
            self.df = pd.DataFrame()

    def get_company_info(self, symbol):
        """
        دریافت اطلاعات بنیادی یک سهم از فایل CSV
        """
        if self.df.empty:
            return self._get_default_info(symbol)

        # جستجو با نام فارسی (ستون symbol)
        row = self.df[self.df['symbol'] == symbol]
        if not row.empty:
            return {
                "symbol": symbol,
                "pe_ratio": float(row.iloc[0]['pe_ratio']),
                "roe": float(row.iloc[0]['roe']),
                "profit_growth": float(row.iloc[0]['profit_growth']),
                "debt_to_equity": float(row.iloc[0]['debt_to_equity']),
                "sales_growth": float(row.iloc[0]['sales_growth'])
            }
        else:
            print(f"⚠️ اطلاعات بنیادی برای {symbol} در CSV پیدا نشد.")
            return self._get_default_info(symbol)

    def _get_default_info(self, symbol):
        """داده‌های پیش‌فرض برای زمانی که اطلاعات بنیادی موجود نیست"""
        return {
            "symbol": symbol,
            "pe_ratio": 10.0,
            "roe": 0.15,
            "profit_growth": 0.10,
            "debt_to_equity": 0.50,
            "sales_growth": 0.05
        }

    def calculate_fundamental_score(self, symbol):
        """محاسبه امتیاز بنیادی بر اساس معیارهای کلیدی"""
        info = self.get_company_info(symbol)
        score = 0
        reasons = []

        # ۱. نسبت P/E (هرچه کمتر، بهتر)
        pe = info.get("pe_ratio", 20)
        if pe < 5:
            score += 15
            reasons.append("P/E بسیار پایین")
        elif pe < 10:
            score += 10
            reasons.append("P/E پایین")
        elif pe < 15:
            score += 5
            reasons.append("P/E متوسط")

        # ۲. بازده حقوق صاحبان سهام (ROE)
        roe = info.get("roe", 0)
        if roe > 0.25:
            score += 15
            reasons.append("ROE عالی")
        elif roe > 0.15:
            score += 10
            reasons.append("ROE خوب")

        # ۳. رشد سودآوری
        growth = info.get("profit_growth", 0)
        if growth > 0.20:
            score += 15
            reasons.append("رشد سود بالا")
        elif growth > 0.10:
            score += 10
            reasons.append("رشد سود متوسط")

        # ۴. نسبت بدهی (هرچه کمتر، بهتر)
        debt = info.get("debt_to_equity", 1)
        if debt < 0.3:
            score += 10
            reasons.append("بدهی پایین")
        elif debt < 0.6:
            score += 5
            reasons.append("بدهی متوسط")

        # ۵. رشد فروش
        sales_growth = info.get("sales_growth", 0)
        if sales_growth > 0.15:
            score += 10
            reasons.append("رشد فروش بالا")
        elif sales_growth > 0.05:
            score += 5
            reasons.append("رشد فروش متوسط")

        # امتیاز نهایی (مقیاس ۰ تا ۱۰۰)
        final_score = min(100, int(score * 1.5))

        return {
            "symbol": symbol,
            "score": final_score,
            "reasons": reasons[:5],
            "details": info
        }

    def get_top_fundamental_stocks(self, symbols, top_n=10):
        """دریافت بهترین سهام بر اساس امتیاز بنیادی"""
        results = []
        for symbol in symbols:
            result = self.calculate_fundamental_score(symbol)
            results.append(result)
        
        # مرتب‌سازی بر اساس امتیاز (نزولی)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_n]

    def report(self, symbol):
        """گزارش تحلیل بنیادی برای یک سهم"""
        result = self.calculate_fundamental_score(symbol)
        lines = [
            "=" * 50,
            f"📊 تحلیل بنیادی {symbol}",
            "=" * 50,
            f"امتیاز بنیادی: {result['score']:.1f} از ۱۰۰",
            f"دلایل: {', '.join(result['reasons']) if result['reasons'] else 'هیچ‌کدام'}",
            "",
            "📋 جزئیات:",
            f"   نسبت P/E: {result['details'].get('pe_ratio', 'N/A')}",
            f"   ROE: {result['details'].get('roe', 0) * 100:.1f}%",
            f"   رشد سود: {result['details'].get('profit_growth', 0) * 100:.1f}%",
            f"   نسبت بدهی: {result['details'].get('debt_to_equity', 0) * 100:.1f}%",
            f"   رشد فروش: {result['details'].get('sales_growth', 0) * 100:.1f}%",
            "=" * 50
        ]
        return "\n".join(lines)

    def report_multiple(self, symbols):
        """گزارش تحلیل بنیادی برای چند سهم"""
        top_stocks = self.get_top_fundamental_stocks(symbols, top_n=10)
        
        lines = [
            "=" * 60,
            "🏦 تحلیل بنیادی - ۱۰ سهم برتر",
            "=" * 60,
            f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ""
        ]
        
        for i, stock in enumerate(top_stocks, 1):
            lines.append(f"{i}. {stock['symbol']} | امتیاز: {stock['score']:.1f}")
            lines.append(f"   دلایل: {', '.join(stock['reasons'][:3])}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


# ========== بخش تست ==========
if __name__ == "__main__":
    analyzer = FundamentalAnalyzer()
    
    # لیست سهام برای تحلیل
    symbols = ["فولاد", "فملی", "خودرو", "خگستر", "شپنا", "وبملت", "فارس", "شستا", "کگل", "حکشتی"]
    
    print("\n" + "=" * 60)
    print("📊 تحلیل بنیادی گروهی")
    print("=" * 60)
    
    for symbol in symbols:
        print(analyzer.report(symbol))
    
    print(analyzer.report_multiple(symbols))

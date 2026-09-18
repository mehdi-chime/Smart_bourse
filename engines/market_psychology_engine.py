"""
engines/market_psychology_engine.py
موتور تشخیص ریزش موقتی از ساختاری
"""

class MarketPsychologyEngine:
    def __init__(self, stocks, gold_price=0, dollar_price=0, legal_buy_ratio=0.5):
        self.stocks = stocks
        self.gold_price = gold_price      # قیمت طلا (اگر داری)
        self.dollar_price = dollar_price  # قیمت دلار (اگر داری)
        self.legal_buy_ratio = legal_buy_ratio  # نسبت خرید حقوقی به کل

    def analyze_drop_type(self):
        """
        تشخیص نوع ریزش بر اساس چند شاخص
        بازگشت: 'موقتی' یا 'ساختاری' یا 'نامشخص'
        """
        # ۱. درصد سهام منفی
        negative_stocks = sum(1 for s in self.stocks if s.get('change_percent', 0) < 0)
        total = len(self.stocks)
        negative_ratio = negative_stocks / total if total > 0 else 0

        # ۲. شدت افت شاخص (اگر داده‌اش را داشته باشی)
        # اینجا می‌توانی از تغییرات شاخص کل استفاده کنی

        # ۳. رفتار حقوقی‌ها
        if self.legal_buy_ratio > 0.6:
            legal_signal = "خرید حقوقی بالا"
        elif self.legal_buy_ratio > 0.4:
            legal_signal = "متوسط"
        else:
            legal_signal = "فروش حقوقی بالا"

        # ۴. واکنش بازارهای موازی (طلا و دلار)
        if self.gold_price > 0 and self.dollar_price > 0:
            # اگر طلا و دلار همزمان بالا رفته باشند
            if self.gold_price > self.gold_price * 1.01 or self.dollar_price > self.dollar_price * 1.01:
                parallel_market = "افزایش"
            else:
                parallel_market = "ثبات"
        else:
            parallel_market = "نامشخص"

        # ۵. جمع‌بندی
        if negative_ratio > 0.7 and self.legal_buy_ratio < 0.3 and parallel_market == "افزایش":
            return {
                "type": "ساختاری 🔴",
                "description": "ریزش شدید و هماهنگ با خروج نقدینگی به بازارهای موازی",
                "action": "خرید نکن، منتظر بمان تا بازار آرام شود.",
                "duration": "چند هفته تا چند ماه",
                "crisis_swing_allowed": False
            }
        elif negative_ratio > 0.5 and self.legal_buy_ratio > 0.5:
            return {
                "type": "موقتی 🟡",
                "description": "ریزش ناشی از هیجان منفی، اما حقوقی‌ها در حال خرید هستند.",
                "action": "می‌توانی با احتیاط و حجم کم در منفی ۳ خرید کنی.",
                "duration": "۱ تا ۳ روز",
                "crisis_swing_allowed": True
            }
        else:
            return {
                "type": "نامشخص 🟠",
                "description": "شرایط نامشخص است. بازار در حال تعادل‌یابی است.",
                "action": "صبر کن و منتظر سیگنال واضح‌تر باش.",
                "duration": "نامشخص",
                "crisis_swing_allowed": False
            }

    def report(self):
        result = self.analyze_drop_type()
        lines = [
            "🧠 تحلیل روانشناسی بازار:",
            "=" * 60,
            f"📌 نوع ریزش: {result['type']}",
            f"📝 توضیح: {result['description']}",
            f"⏳ مدت پیش‌بینی‌شده: {result['duration']}",
            f"💡 اقدام پیشنهادی: {result['action']}",
        ]
        if result['crisis_swing_allowed']:
            lines.append("✅ نوسان‌گیری بحرانی (منفی ۳ به صفر) مجاز است.")
        else:
            lines.append("⛔ نوسان‌گیری بحرانی توصیه نمی‌شود.")
        return "\n".join(lines)

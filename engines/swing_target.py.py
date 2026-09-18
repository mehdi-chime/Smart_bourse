"""
engines/swing_engine.py
موتور نوسان‌گیری روزانه - مخصوص سهام خاص (خگستر، خبهمن و ...)
با تحلیل حجم، تغییرات قیمت، و رفتار سفارشات
"""

class SwingEngine:
    def __init__(self, stocks, config=None, target_symbols=None):
        """
        stocks: لیست سهام
        target_symbols: لیست سهام مورد نظر (مثلاً ['خگستر', 'خبهمن'])
        """
        self.all_stocks = stocks
        self.config = config or self.default_config()
        self.target_symbols = target_symbols or ['خگستر', 'خبهمن']
        self.candidates = []

    def default_config(self):
        return {
            "min_volume": 30_000_000_000,      # حداقل حجم (۳۰ میلیارد تومان)
            "buy_threshold": -2.5,             # خرید در منفی ۲.۵٪
            "sell_threshold": 1.5,             # فروش در مثبت ۱.۵٪
            "max_candidates": 5,
            "stop_loss": -4.0,                 # حد ضرر ۴٪
        }

    def filter_stocks(self):
        """فیلتر کردن سهام بر اساس حجم و تغییرات"""
        filtered = []
        for stock in self.all_stocks:
            symbol = stock.get('symbol', '')
            # فقط سهام مورد نظر را بررسی کن
            if symbol not in self.target_symbols:
                continue

            volume = stock.get('volume', 0)
            change = stock.get('change_percent', 0)

            # اگر حجم مناسب نبود، رد کن
            if volume < self.config["min_volume"]:
                continue

            # اگر تغییرات در محدوده خرید یا فروش نبود، رد کن
            if change < self.config["buy_threshold"] or change > self.config["sell_threshold"]:
                continue

            filtered.append(stock)

        return filtered

    def analyze_stock(self, stock):
        """تحلیل دقیق یک سهم برای نوسان‌گیری"""
        symbol = stock.get('symbol', 'نامشخص')
        price = stock.get('close_price', 0)
        change = stock.get('change_percent', 0)
        volume = stock.get('volume', 0)
        open_price = stock.get('open_price', 0)

        # تشخیص سیگنال
        if change <= self.config["buy_threshold"]:
            signal = "🟢 خرید"
            target = price * (1 + (self.config["sell_threshold"] - change) / 100)
            stop_loss = price * (1 + self.config["stop_loss"] / 100)
            reason = f"ریزش به {change:.1f}٪ - پتانسیل بازگشت"
        elif change >= self.config["sell_threshold"]:
            signal = "🔴 فروش"
            target = price * (1 - (change - self.config["sell_threshold"]) / 100)
            stop_loss = None
            reason = f"رشد به {change:.1f}٪ - برداشت سود"
        else:
            return None

        return {
            "symbol": symbol,
            "price": price,
            "change": change,
            "volume": volume,
            "signal": signal,
            "target": target,
            "stop_loss": stop_loss,
            "reason": reason,
            "score": round(abs(change) * 2 + (volume / 10_000_000_000), 2)
        }

    def get_candidates(self):
        """انتخاب سهام برتر برای نوسان‌گیری"""
        filtered = self.filter_stocks()
        analyzed = []

        for stock in filtered:
            result = self.analyze_stock(stock)
            if result:
                analyzed.append(result)

        # مرتب‌سازی بر اساس امتیاز
        analyzed.sort(key=lambda x: x.get('score', 0), reverse=True)
        self.candidates = analyzed[:self.config["max_candidates"]]
        return self.candidates

    def report(self):
        """گزارش خروجی"""
        if not self.candidates:
            return "❌ امروز سیگنال نوسان‌گیری برای سهام مورد نظر پیدا نشد."

        lines = ["📈 پیشنهادات نوسان‌گیری روزانه (خگستر، خبهمن و ...):"]
        lines.append("=" * 60)

        for s in self.candidates:
            lines.append(f"""
📌 {s['symbol']}
   قیمت: {s['price']:,.0f} ریال
   تغییرات: {s['change']:+.1f}%
   حجم: {s['volume']:,}
   سیگنال: {s['signal']}
   🎯 هدف: {s['target']:,.0f} ریال
   🛑 حد ضرر: {s['stop_loss']:,.0f} ریال
   💡 {s['reason']}
""")

        lines.append("=" * 60)
        return "\n".join(lines)

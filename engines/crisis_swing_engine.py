"""
engines/crisis_swing_engine.py
موتور نوسان‌گیری در روزهای بحرانی - خرید در منفی ۳ و فروش در صفر
"""

class CrisisSwingEngine:
    def __init__(self, stocks, config=None):
        self.stocks = stocks
        self.config = config or self.default_config()
        self.signals = []

    def default_config(self):
        return {
            "buy_threshold": -3.0,    # درصد منفی برای خرید
            "sell_threshold": 0.0,    # درصد صفر برای فروش
            "max_investment": 0.20,   # حداکثر ۲۰٪ سرمایه در این استراتژی
            "stop_loss": -6.0,        # حد ضرر ۶٪ (اگر بازار بیشتر ریخت)
            "min_volume": 30_000_000_000,  # سهام با نقدشوندگی بالا
        }

    def analyze_stock(self, stock):
        change = stock.get('change_percent', 0)
        volume = stock.get('volume', 0)
        symbol = stock.get('symbol', 'نامشخص')
        price = stock.get('close_price', 0)

        # فقط سهام با نقدشوندگی بالا
        if volume < self.config["min_volume"]:
            return None

        # سیگنال خرید در منفی ۳
        if change <= self.config["buy_threshold"]:
            return {
                "symbol": symbol,
                "price": price,
                "change": change,
                "signal": "🟢 خرید بحرانی",
                "target": price * (1 + (self.config["sell_threshold"] - change) / 100),
                "stop_loss": price * (1 + self.config["stop_loss"] / 100),
                "volume": volume,
                "reason": f"ریزش به {change:.1f}٪ - پتانسیل بازگشت به صفر"
            }

        return None

    def get_candidates(self):
        self.signals = []
        for stock in self.stocks:
            signal = self.analyze_stock(stock)
            if signal:
                self.signals.append(signal)

        # مرتب‌سازی بر اساس نزدیک‌ترین به منفی ۳
        self.signals.sort(key=lambda x: x['change'])
        return self.signals

    def report(self):
        if not self.signals:
            return "❌ هیچ سیگنال خرید بحرانی پیدا نشد."

        lines = ["🚨 سیگنال‌های خرید بحرانی (منفی ۳ به صفر):"]
        lines.append("=" * 60)

        for s in self.signals:
            lines.append(f"""
📌 {s['symbol']}
   قیمت فعلی: {s['price']:,.0f} ریال
   تغییرات: {s['change']:.1f}%
   🎯 هدف: {s['target']:,.0f} ریال (صفر)
   🛑 حد ضرر: {s['stop_loss']:,.0f} ریال (۶٪-)
   💡 {s['reason']}
""")

        lines.append("=" * 60)
        lines.append("⚠️ توصیه: فقط ۲۰٪ سرمایه را وارد کن و در صورت برگشت به صفر، بفروش.")
        return "\n".join(lines)

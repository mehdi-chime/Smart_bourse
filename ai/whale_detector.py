import json
import os

class WhaleDetector:
    def __init__(self):
        # مسیر پوشه‌ای که فایل‌های JSON در آن هستند
        self.data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
        self.data_folder = os.path.abspath(self.data_folder)  # مسیر کامل
        print(f"🔍 مسیر پوشه داده: {self.data_folder}")  # برای اطمینان

        # آستانه تشخیص نهنگ (۱ میلیون سهم)
        self.whale_threshold = 1_000_000

    def load_json(self, filename):
        path = os.path.join(self.data_folder, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            print(f"❌ فایل {path} پیدا نشد.")
            return None

    def detect_from_order_book(self, filename="order_book_khegostar.json"):
        data = self.load_json(filename)
        if not data:
            return {"signal": f"⚠️ فایل {filename} پیدا نشد"}

        whales = []
        best_limits = data.get("bestLimits", [])
        for item in best_limits:
            buy_vol = item.get("qTitMeDem", 0)
            sell_vol = item.get("qTitMeOf", 0)
            if buy_vol > self.whale_threshold:
                whales.append({"type": "BUY", "volume": buy_vol})
            if sell_vol > self.whale_threshold:
                whales.append({"type": "SELL", "volume": sell_vol})

        if not whales:
            return {"signal": "⚪ هیچ نهنگی در صفوف شناسایی نشد"}

        buy_count = sum(1 for w in whales if w['type'] == "BUY")
        sell_count = sum(1 for w in whales if w['type'] == "SELL")
        signal = "🟢 خرید" if buy_count > sell_count else "🔴 فروش" if sell_count > buy_count else "⚪ متعادل"

        return {"signal": signal, "buy_count": buy_count, "sell_count": sell_count}

    def report(self, filename="order_book_khegostar.json"):
        result = self.detect_from_order_book(filename)
        lines = [
            "=" * 50,
            f"🐋 تشخیص نهنگ‌ها - {filename}",
            "=" * 50,
            f"سیگنال: {result.get('signal', 'نامشخص')}",
            f"تعداد نهنگ‌های خریدار: {result.get('buy_count', 0)}",
            f"تعداد نهنگ‌های فروشنده: {result.get('sell_count', 0)}",
            "=" * 50
        ]
        return "\n".join(lines)

if __name__ == "__main__":
    detector = WhaleDetector()
    print(detector.report())

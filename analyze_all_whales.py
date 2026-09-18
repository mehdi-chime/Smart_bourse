import json
import os
from datetime import datetime

class WhaleDetector:
    def __init__(self):
        self.data_folder = "data"
        self.whale_threshold = 1_000_000
        self.funds = [
            "ماهور", "ارکیده", "اركيده", "تابان", "آفاق", "ثمر",
            "شگستر", "وتجارت", "وبملت", "وبانک", "ونیرو", "تداوم"
        ]

    def is_fund(self, symbol):
        return any(fund in symbol for fund in self.funds)

    def load_json(self, filename):
        path = os.path.join(self.data_folder, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def detect_real_whales(self, filename="tsetmc_all_20260902_040150.json"):
        data = self.load_json(filename)
        if not data:
            return {"error": "فایل پیدا نشد"}

        real_whales = []
        for stock in data:
            try:
                symbol = stock.get("symbol", "")
                if self.is_fund(symbol):
                    continue

                # قیمت ممکن است None باشد، بنابراین با {} جایگزین می‌کنیم
                price_info = stock.get("price", {}) or {}
                price_info = price_info.get("closingPriceInfo", {}) or {}

                trade_volume = price_info.get("qTotTran5J", 0) or 0
                trade_count = price_info.get("zTotTran", 0) or 0
                price = price_info.get("pClosing", 0) or 0

                if trade_volume > self.whale_threshold and trade_count < 100:
                    real_whales.append({
                        "symbol": symbol,
                        "volume": int(trade_volume),
                        "trade_count": trade_count,
                        "price": price
                    })
            except Exception as e:
                # اگر خطایی در پردازش یک سهم رخ داد، آن را نادیده بگیر
                continue

        real_whales.sort(key=lambda x: x['volume'], reverse=True)

        return {
            "whales": real_whales[:10],
            "total_whales": len(real_whales)
        }

    def report(self, filename="tsetmc_all_20260902_040150.json"):
        result = self.detect_real_whales(filename)
        if "error" in result:
            return f"❌ {result['error']}"

        lines = [
            "=" * 60,
            "🐋 تشخیص نهنگ‌های واقعی (بر اساس حجم و تعداد معاملات)",
            "=" * 60,
            f"📅 تاریخ تحلیل: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "🔴 نهنگ‌های احتمالی (حجم بالا، تعداد معاملات کم):"
        ]
        if result['whales']:
            for w in result['whales']:
                lines.append(f"   📊 {w['symbol']}: {w['volume']:,} سهم | تعداد معاملات: {w['trade_count']} | قیمت: {w['price']:,.0f}")
        else:
            lines.append("   ✅ هیچ نهنگی بر اساس معیارهای واقعی شناسایی نشد.")

        lines.append("\n📊 خلاصه:")
        lines.append(f"   تعداد نهنگ‌ها: {result['total_whales']}")
        lines.append("=" * 60)

        return "\n".join(lines)

if __name__ == "__main__":
    detector = WhaleDetector()
    files = [f for f in os.listdir("data") if f.startswith("tsetmc_all_")]
    if files:
        latest_file = sorted(files)[-1]
        print(f"📂 استفاده از فایل: {latest_file}")
        print(detector.report(latest_file))
    else:
        print("❌ هیچ فایل tsetmc_all_*.json در پوشه data پیدا نشد.")

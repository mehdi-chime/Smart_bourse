# check_stock.py
# بررسی یه سهم با برنامه Smart_Bourse
# اجرا: python check_stock.py آسیاتک
# یا: python check_stock.py ذواکس

import sys
import json
from pathlib import Path
from datetime import datetime

# مسیر پروژه
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
sys.path.insert(0, str(PROJECT_ROOT / "ai"))

print("=" * 60)
print("🔍 بررسی سهم با Smart_Bourse")
print("=" * 60)
print()


def get_stock_data(symbol):
    """دریافت داده‌ی سهم از algotik_tse"""
    try:
        import algotik_tse

        print(f"📡 دریافت داده برای: {symbol}")
        market = algotik_tse.get_live_market()
        print(f"   ✅ {len(market)} سهم دریافت شد")
        print()

        # پیدا کردن سهم
        stock = None
        for _, row in market.iterrows():
            name = str(row.get("name", "")) or str(row.get("symbol", ""))
            if symbol in name:
                stock = row
                break

        if stock is None:
            print(f"   ❌ سهم '{symbol}' پیدا نشد!")
            return None

        return stock

    except Exception as e:
        print(f"   ❌ خطا: {e}")
        return None


def analyze_stock(symbol):
    """تحلیل کامل سهم"""
    print(f"🎯 تحلیل: {symbol}")
    print("─" * 60)

    # ۱. دریافت داده
    stock = get_stock_data(symbol)
    if stock is None:
        return

    # ۲. استخراج اطلاعات
    name = stock.get("name", symbol)
    last = float(stock.get("last", 0))
    close = float(stock.get("close", 0))
    pe = float(stock.get("pe", 0))
    rsi = float(stock.get("rsi", 50))
    volume = float(stock.get("volume", 0))
    atr = float(stock.get("atr", 0))

    # محاسبه تغییر
    if close > 0:
        change_pct = ((last - close) / close) * 100
    else:
        change_pct = 0

    # ۳. نمایش
    print(f"📊 نماد: {name}")
    print(f"💰 قیمت: {last:,.0f}")
    print(f"📈 تغییر: {change_pct:+.2f}%")
    print(f"📉 RSI: {rsi:.1f}")
    print(f"📊 P/E: {pe:.2f}")
    print(f"📦 حجم: {volume:,.0f}")
    print(f"📏 ATR: {atr:.2f}%")
    print()

    # ۴. چک شرایط
    print("🔍 چک شرایط استراتژی:")
    print("─" * 60)

    checks = []

    # RSI
    if rsi < 30:
        checks.append(("RSI", f"{rsi:.1f}", "✅ عالی (زیر ۳۰)"))
    elif rsi < 50:
        checks.append(("RSI", f"{rsi:.1f}", "✅ خوب (زیر ۵۰)"))
    elif rsi < 70:
        checks.append(("RSI", f"{rsi:.1f}", "⚠️ متوسط (بالای ۵۰)"))
    else:
        checks.append(("RSI", f"{rsi:.1f}", "🔴 اشباع خرید!"))

    # تغییر قیمت
    if change_pct <= -3:
        checks.append(("تغییر", f"{change_pct:.2f}%", "✅ منفی ۳٪ (فرصت خرید!)"))
    elif change_pct < 0:
        checks.append(("تغییر", f"{change_pct:.2f}%", "🟡 منفی (ولی کم)"))
    elif change_pct < 3:
        checks.append(("تغییر", f"{change_pct:.2f}%", "🟡 مثبت کم"))
    else:
        checks.append(("تغییر", f"{change_pct:.2f}%", "🔴 مثبت ۳٪ (فروش!)"))

    # P/E
    if pe > 0 and pe < 15:
        checks.append(("P/E", f"{pe:.2f}", "✅ زیر ۱۵"))
    elif pe > 0:
        checks.append(("P/E", f"{pe:.2f}", "⚠️ بالای ۱۵"))
    else:
        checks.append(("P/E", f"{pe:.2f}", "❓ نامشخص"))

    # حجم
    if volume > 500000:
        checks.append(("حجم", f"{volume:,.0f}", "✅ بالای ۵۰۰K"))
    else:
        checks.append(("حجم", f"{volume:,.0f}", "⚠️ زیر ۵۰۰K"))

    # ATR
    if atr > 2.5:
        checks.append(("ATR", f"{atr:.2f}%", "✅ بالای ۲.۵٪"))
    else:
        checks.append(("ATR", f"{atr:.2f}%", "⚠️ زیر ۲.۵٪"))

    for name_c, val, result in checks:
        print(f"   {name_c}: {val} → {result}")

    print()

    # ۵. تصمیم نهایی
    print("🎯 تصمیم نهایی:")
    print("─" * 60)

    # محاسبه امتیاز
    score = 0
    reasons = []

    if rsi < 30:
        score += 40
        reasons.append("RSI عالی")
    elif rsi < 50:
        score += 25
        reasons.append("RSI خوب")

    if change_pct <= -3:
        score += 40
        reasons.append("منفی ۳٪")
    elif change_pct < 0:
        score += 20

    if pe > 0 and pe < 15:
        score += 20
        reasons.append("P/E خوب")

    print(f"   امتیاز: {score}/100")

    if score >= 70:
        print(f"   ✅ بخر! ({', '.join(reasons)})")
    elif score >= 50:
        print(f"   🟡 شاید ({', '.join(reasons)})")
    else:
        print(f"   🔴 نخر! شرایط مناسب نیست")

    print()


# ===== اجرا =====
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ نام سهم رو بده!")
        print()
        print("مثال:")
        print("   python check_stock.py آسیاتک")
        print("   python check_stock.py ذواکس")
        sys.exit(1)

    symbol = sys.argv[1]
    analyze_stock(symbol)

    print("=" * 60)

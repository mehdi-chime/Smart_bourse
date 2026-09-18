"""
daily_runner.py
اسکریپت اجرای روزانه - دانلود خودکار داده + وضعیت بازار + موتورها + هوش مصنوعی + اسکنر پیشرفته + اسکن لحظه‌ای
نسخه ۸.۰ - با پشتیبانی از نوسان‌گیری لحظه‌ای و ثبت معاملات
"""

import json
import os
from datetime import datetime

# ========== دانلودر خودکار ==========
from market_downloader import MarketDownloader

# ========== ماژول‌های اصلی ==========
from core.market_health import calculate_market_health
from core.event_analyzer import EventAnalyzer
from core.trade_recorder import TradeRecorder

from engines.swing_engine import SwingEngine
from engines.long_term_engine import LongTermEngine
from engines.advanced_scanner import AdvancedScanner

from ai.order_flow_analyzer import OrderFlowAnalyzer
from ai.whale_detector import WhaleDetector
from ai.momentum_scanner import MomentumScanner

from decision.ai_decision_engine import AIDecisionEngine

# ========== تنظیمات ==========
DATA_FILE = "data/market_today.json"
REPORT_FILE = "reports/daily_signal.txt"
LOG_FILE = "logs/daily_run.log"

# ========== لیست سهام هدف ==========
TARGET_SYMBOLS = [
    "خگستر", "فولاد", "فملی", "خودرو", "خبهمن",
    "شپنا", "شستا", "کگل", "وبملت", "فارس", "حکشتی"
]

# ========== توابع کمکی ==========
def download_today_data():
    print("\n📡 دانلود داده‌های امروز از بازار...")
    downloader = MarketDownloader()
    if downloader.download():
        downloader.save_json()
        print("✅ داده‌های امروز با موفقیت دانلود و ذخیره شد.")
        return True
    else:
        print("❌ خطا در دانلود داده‌های امروز.")
        return False

def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_report(content):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def get_news_risk():
    print("\n📰 ریسک خبری امروز را وارد کنید (۱ تا ۱۰):")
    print("   - ۱ تا ۳: آرامش نسبی")
    print("   - ۴ تا ۶: اخبار متوسط")
    print("   - ۷ تا ۱۰: اخبار پرریسک")
    while True:
        try:
            risk = int(input("عدد را وارد کنید (۱-۱۰): "))
            if 1 <= risk <= 10:
                return risk
        except:
            print("❌ عدد معتبر وارد کن.")

# ========== تابع اصلی ==========
def main():
    print("\n" + "=" * 60)
    print("🔍 گزارش روزانه Smart Bourse")
    print("=" * 60)

    log_message("شروع گزارش روزانه")

    # ========== دانلود داده‌های امروز ==========
    download_today_data()

    # ========== بارگذاری داده ==========
    data = load_data()
    if not data:
        print("❌ فایل داده پیدا نشد!")
        return

    if isinstance(data, list):
        stocks = data
        health = calculate_market_health({"stocks": data})
    else:
        stocks = data.get('stocks', [])
        health = calculate_market_health(data)

    if not stocks:
        print("❌ لیست سهام خالی است.")
        return

    # ========== دریافت ریسک خبری ==========
    news_risk = get_news_risk()
    log_message(f"ریسک خبری: {news_risk}")

    # ========== تحلیل رویدادها ==========
    event_analyzer = EventAnalyzer()
    event_impact = event_analyzer.calculate_market_impact()

    # ========== نمره نهایی سلامت بازار ==========
    final_score = health['health_score']
    if event_impact['impact_score'] > 70:
        final_score -= 20
    elif event_impact['impact_score'] > 40:
        final_score -= 10

    if news_risk >= 7:
        final_score -= 15
    elif news_risk >= 4:
        final_score -= 5

    final_score = max(0, min(100, final_score))

    if final_score < 35:
        final_status = "قرمز 🔴"
        final_advice = "خطر ریزش! امروز خرید نکن."
    elif final_score < 65:
        final_status = "زرد 🟡"
        final_advice = "صبر کن، بازار مطمئن نیست."
    else:
        final_status = "سبز 🟢"
        final_advice = "وضعیت خوب است. می‌توانی از موتورها استفاده کنی."

    # ========== گزارش پایه ==========
    report = f"""
========================================
📆 تاریخ: {datetime.now().strftime("%Y-%m-%d %H:%M")}

📊 وضعیت بازار (اصلاح‌شده):
   نمره سلامت: {final_score} از ۱۰۰
   وضعیت نهایی: {final_status}
   💡 توصیه: {final_advice}
   📰 ریسک خبری: {news_risk}/10

📅 رویدادهای پیش‌رو:
   {event_impact['impact_level']}
"""

    # ========== موتور نوسان‌گیری ==========
    swing = SwingEngine(stocks)
    swing.get_candidates()
    report += f"\n\n📈 {swing.report()}"

    # ========== موتور بلندمدت ==========
    long = LongTermEngine(stocks)
    long.get_candidates()
    report += f"\n\n📊 {long.report()}"

    # ========== هوش مصنوعی ==========
    print("\n🧠 در حال تحلیل هوش مصنوعی...")
    
    for symbol in TARGET_SYMBOLS:
        try:
            engine = AIDecisionEngine(symbol)
            
            order_flow = OrderFlowAnalyzer()
            flow_result = order_flow.analyze_pressure(symbol)
            if flow_result and flow_result.get('records', 0) > 0:
                engine.add_signal("order_flow", "BUY" if flow_result['pressure'] > 1.2 else "SELL" if flow_result['pressure'] < 0.8 else "HOLD", flow_result['pressure'])
            
            whale = WhaleDetector()
            whale_result = whale.detect_real_whales()
            if whale_result and whale_result.get('whales'):
                buy_count = sum(1 for w in whale_result['whales'] if w['type'] == "BUY")
                sell_count = sum(1 for w in whale_result['whales'] if w['type'] == "SELL")
                if buy_count > sell_count:
                    engine.add_signal("whale", "BUY", 0.7)
                elif sell_count > buy_count:
                    engine.add_signal("whale", "SELL", 0.7)
                else:
                    engine.add_signal("whale", "HOLD", 0.5)
            
            decision = engine.calculate_final_decision()
            report += f"\n\n🧠 {engine.report()}"
            
        except Exception as e:
            log_message(f"خطا در تحلیل هوش مصنوعی برای {symbol}: {e}")
            report += f"\n\n⚠️ خطا در تحلیل هوش مصنوعی برای {symbol}"

    # ========== Advanced Scanner ==========
    print("\n🔍 در حال اجرای اسکنر پیشرفته...")
    try:
        scanner = AdvancedScanner()
        scanner.scan_all()
        report += f"\n\n{scanner.report()}"
    except Exception as e:
        log_message(f"خطا در اسکنر پیشرفته: {e}")
        report += f"\n\n⚠️ خطا در اجرای اسکنر پیشرفته"

    # ========== اسکن لحظه‌ای (Momentum Scanner) ==========
    print("\n⚡ اسکن لحظه‌ای سهام با شتاب بالا...")
    try:
        momentum = MomentumScanner()
        momentum_symbols = momentum.scan_all(TARGET_SYMBOLS, min_momentum=0.5)
        
        if momentum_symbols:
            report += "\n\n⚡ سهام با شتاب لحظه‌ای (نوسان‌گیری سریع):"
            for s in momentum_symbols:
                report += f"\n   🔥 {s['symbol']}: {s['momentum_3m']['change_percent']:+.2f}% در ۳ دقیقه"
        else:
            report += "\n\n⚡ هیچ سهمی با شتاب بالا در لحظه شناسایی نشد."
    except Exception as e:
        log_message(f"خطا در اسکن لحظه‌ای: {e}")
        report += f"\n\n⚠️ خطا در اسکن لحظه‌ای"

    # ========== ثبت معاملات روزانه ==========
    print("\n📝 ثبت معاملات روزانه...")
    try:
        recorder = TradeRecorder()
        today_trades = recorder.get_today_trades()
        if not today_trades.empty:
            report += f"\n\n📝 خلاصه معاملات امروز ({len(today_trades)} معامله):"
            for _, row in today_trades.iterrows():
                report += f"\n   {row['symbol']} | {row['trade_type']} | {row['volume']} سهم در {row['price']:,.0f}"
        else:
            report += "\n\n📝 امروز هیچ معامله‌ای ثبت نشده است."
    except Exception as e:
        log_message(f"خطا در ثبت معاملات: {e}")
        report += f"\n\n⚠️ خطا در ثبت معاملات"

    report += "\n========================================"

    # ========== ذخیره و نمایش ==========
    save_report(report)
    print("\n" + report)
    print(f"\n📁 گزارش در '{REPORT_FILE}' ذخیره شد.")
    log_message("گزارش روزانه تکمیل شد.")

if __name__ == "__main__":
    main()

"""
auto_trader.py
معامله‌گر خودکار - فقط در روزهای منفی خرید می‌کند و حد ضرر را مدیریت می‌کند
نسخه ۱.۰ - ۱۴۰۵/۰۶/۱۰
"""

import json
import os
from datetime import datetime

from core.market_health import calculate_market_health
from engines.crisis_swing_engine import CrisisSwingEngine
from engines.market_psychology_engine import MarketPsychologyEngine

# ========== تنظیمات ==========
DATA_FILE = "data/market_today.json"
REPORT_FILE = "reports/auto_trader_signal.txt"
LOG_FILE = "logs/auto_trader.log"

# ========== تنظیمات سرمایه ==========
MAX_INVESTMENT_PER_TRADE = 0.20   # حداکثر ۲۰٪ سرمایه در هر معامله
MAX_DAILY_LOSS = 0.02             # حداکثر ضرر روزانه ۲٪ سرمایه
STOP_LOSS = -0.04                 # حد ضرر ۴٪


def log_message(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")


def load_data():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_report(content):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


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
            print("❌ عدد بین ۱ تا ۱۰ وارد کن.")
        except:
            print("❌ فقط عدد وارد کن.")


def main():
    print("\n" + "=" * 60)
    print("🤖 معامله‌گر خودکار Smart Bourse")
    print("=" * 60)

    log_message("شروع معامله‌گر خودکار")

    # ========== بارگذاری داده ==========
    data = load_data()
    if not data:
        print("❌ فایل داده پیدا نشد!")
        log_message("خطا: فایل داده پیدا نشد")
        return

    if isinstance(data, list):
        stocks = data
        health = calculate_market_health({"stocks": data})
    else:
        stocks = data.get('stocks', [])
        health = calculate_market_health(data)

    if not stocks:
        print("❌ لیست سهام خالی است.")
        log_message("خطا: لیست سهام خالی")
        return

    # ========== دریافت ریسک خبری ==========
    news_risk = get_news_risk()
    log_message(f"ریسک خبری: {news_risk}")

    # ========== تحلیل روانشناسی بازار ==========
    print("\n🧠 تحلیل روانشناسی بازار...")
    psychology = MarketPsychologyEngine(stocks, legal_buy_ratio=0.5)
    psych_result = psychology.analyze_drop_type()
    print(psychology.report())
    log_message(f"نوع ریزش: {psych_result['type']}")

    # ========== سلامت بازار ==========
    final_score = health['health_score']
    if final_score < 35:
        market_status = "قرمز 🔴"
        advice = "خطر ریزش! امروز خرید نکن."
    elif final_score < 65:
        market_status = "زرد 🟡"
        advice = "صبر کن، بازار مطمئن نیست."
    else:
        market_status = "سبز 🟢"
        advice = "وضعیت خوب است. اما این موتور فقط در روزهای منفی خرید می‌کند."

    print(f"\n📊 وضعیت بازار: {market_status} (نمره: {final_score})")

    # ========== تصمیم‌گیری ==========
    # فقط در صورتی خرید کن که:
    # 1. بازار قرمز باشد (نمره < 35) یا زرد با ریزش موقتی
    # 2. ریزش موقتی تشخیص داده شده باشد
    # 3. ریسک خبری کمتر از ۷ باشد (تا حدی)

    can_trade = False
    reason = ""

    if final_score < 35:
        can_trade = True
        reason = "بازار قرمز است (ریزش شدید)."
    elif final_score < 65 and psych_result.get('crisis_swing_allowed', False):
        can_trade = True
        reason = "بازار زرد است اما ریزش موقتی تشخیص داده شد."
    else:
        reason = "شرایط بازار برای خرید مناسب نیست."

    # ========== گزارش نهایی ==========
    report = f"""
========================================
🤖 گزارش معامله‌گر خودکار
📆 تاریخ: {datetime.now().strftime("%Y-%m-%d %H:%M")}

📊 وضعیت بازار: {market_status}
📊 نمره سلامت: {final_score} از ۱۰۰
📰 ریسک خبری: {news_risk}/10

🧠 تحلیل روانشناسی:
{psych_result['type']} - {psych_result['description']}

✅ تصمیم نهایی:
"""

    if can_trade and news_risk < 7:
        # ========== اجرای موتور بحرانی ==========
        print("\n🟢 شرایط خرید فراهم است. اجرای موتور بحرانی...")
        crisis = CrisisSwingEngine(stocks)
        crisis.get_candidates()
        crisis_report = crisis.report()

        report += f"""
✅ خرید مجاز است.
دلیل: {reason}
حداکثر سرمایه در این معامله: {MAX_INVESTMENT_PER_TRADE * 100:.0f}٪

{crisis_report}

⚠️ حد ضرر: {STOP_LOSS * 100:.0f}٪
⚠️ حداکثر ضرر روزانه: {MAX_DAILY_LOSS * 100:.0f}٪
"""
        log_message("خرید مجاز شد")
    else:
        report += f"""
⛔ خرید مجاز نیست.
دلیل: {reason}

توصیه: صبر کن و منتظر روزهای منفی‌تر باش.
"""
        log_message("خرید مجاز نشد")

    report += "========================================"

    save_report(report)
    print("\n" + report)
    print(f"\n📁 گزارش در '{REPORT_FILE}' ذخیره شد.")
    log_message("گزارش نهایی ذخیره شد")


if __name__ == "__main__":
    main()

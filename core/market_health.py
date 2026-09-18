import json
import os

def calculate_market_health(data):
    """
    محاسبه وضعیت سلامت بازار (عدد بین ۰ تا ۱۰۰)
    ورودی: دیکشنری داده‌های بازار (مثل market_today.json)
    خروجی: دیکشنری شامل وضعیت، نمره و توصیه
    """
    stocks = data.get('stocks', [])
    
    if not stocks:
        return {
            "health_score": 50,
            "status": "ناشناخته",
            "advice": "داده‌ای برای تحلیل وجود ندارد."
        }
    
    # شاخص ۱: نسبت صعودی به نزولی
    positive = sum(1 for s in stocks if s.get('change_percent', 0) > 0)
    negative = sum(1 for s in stocks if s.get('change_percent', 0) < 0)
    total = len(stocks)
    ad_ratio = positive / total if total > 0 else 0.5
    
    # شاخص ۲: نسبت پول حقیقی (اگر داده دارید)
    real_money = data.get('real_money_ratio', 0.5)  # پیش‌فرض ۵۰٪
    
    # شاخص ۳: مقایسه شاخص با میانگین متحرک (اگر داده دارید)
    index_status = data.get('index_vs_ma', 1.0)  # پیش‌فرض ۱.۰
    
    # محاسبه نمره نهایی
    score = (ad_ratio * 0.4) + (real_money * 0.35) + (index_status * 0.25)
    health_score = min(100, max(0, int(score * 100)))
    
    if health_score < 35:
        status = "قرمز 🔴"
        advice = "خطر ریزش! دست نگه دار، امروز روز خرید نیست."
    elif health_score < 65:
        status = "زرد 🟡"
        advice = "صبر کن. سیگنال مطمئن نیست."
    else:
        status = "سبز 🟢"
        advice = "وضعیت خوب است. می‌توانی از موتور نوسان‌گیری استفاده کنی."
    
    return {
        "health_score": health_score,
        "status": status,
        "advice": advice,
        "details": {
            "ad_ratio": round(ad_ratio, 2),
            "real_money": round(real_money, 2),
            "index_status": round(index_status, 2),
            "positive": positive,
            "negative": negative,
            "total": total
        }
    }

# اگر مستقیم اجرا شد، یک تست با داده‌های نمونه انجام بده
if __name__ == "__main__":
    # ساخت داده‌های نمونه
    sample_data = {
        "stocks": [
            {"symbol": "فولاد", "change_percent": 2.5},
            {"symbol": "فملی", "change_percent": -1.2},
            {"symbol": "خودرو", "change_percent": 0.8},
            {"symbol": "شپنا", "change_percent": -0.5},
            {"symbol": "کگل", "change_percent": 3.1}
        ],
        "real_money_ratio": 0.6,
        "index_vs_ma": 1.02
    }
    
    result = calculate_market_health(sample_data)
    print("📊 وضعیت سلامت بازار:")
    print(f"   نمره: {result['health_score']} از ۱۰۰")
    print(f"   وضعیت: {result['status']}")
    print(f"   توصیه: {result['advice']}")
    print("   جزئیات:", result['details'])

سلام. من مهدی هستم.
پروژه‌ی Smart_Bourse.
چت قبلی: Smart_Bourse2.

## 🎯 درخواست: ساخت `check_2_stocks.py`

می‌خوام یه فایل پایتون بسازی که **۲ سهم** رو بررسی کنه:
1. **دواتکس**
2. **آسیاتک**

## 📌 اسم‌های دقیق (از TSETMC)

- **دواتکس:** `دواتكس` (با `ك` عربی)
- **آسیاتک:** `اسياتك` (با `ي` و `ك` عربی)
- **INS Code آسیاتک:** `14079693677610396`

## 📋 اطلاعات پروژه

- **مسیر:** F:\python\har roz ba python\smart_bours
- **AI:** `ai/ai_engine.py` (v3.0 با ML)
- **ادغام:** `ai_integration.py` (تابع `get_ai_advice`)
- **اسکنر:** `smart_scanner_v8.py`
- **ایتا:** `scanner/alert_config.py`
- **دیتابیس:** `data/smart_bourse_v2.db`

## 📊 اطلاعاتی که باید نشون بده

| مورد | توضیح |
|:---|:---|
| **قیمت** | Last, Close, Yesterday, ChangePct |
| **دامنه** | MinAllowed, MaxAllowed |
| **P/E** | محاسبه (Last / EPS) |
| **RSI** | 14 روزه (از تاریخچه) |
| **ATR** | نوسان (از تاریخچه) |
| **سفارشات** | Vol_buy/sell_retail, Vol_buy/sell_institutional |
| **نسبت** | خرید/فروش |
| **صف** | خرید/فروش (BidVolume1, AskVolume1) |
| **AI** | از `get_ai_advice` — score, advice, confidence, mode |
| **تصمیم** | خرید/فروش/نگه دار |
| **استراتژی** | قیمت خرید/فروش/حدضرر/سود |

## 🔧 توابع مورد نیاز

### ۱. `normalize(s)`
نرمال‌سازی اسم (تبدیل `ي` به `ی`، `ك` به `ک`)

### ۲. `calc_rsi(prices, period=14)`
محاسبه RSI

### ۳. `calc_atr(highs, lows, closes, period=14)`
محاسبه ATR

### ۴. `get_history_safe(symbol)`
دریافت تاریخچه با `algotik_tse.get_history` (با چند alias)

### ۵. `send_eitaa(text)`
ارسال به ایتا (از `alert_config`)

### ۶. `get_ai_advice(...)`
از `ai_integration`

### ۷. `analyze_stock(stock_info, df_live)`
تحلیل کامل یه سهم

### ۸. `print_stock(r)`
چاپ خروجی

### ۹. `build_eitaa_message(results)`
ساخت پیام ایتا

### ۱۰. `main()`
اجرای برنامه

## 📌 الگوی کد

```python
STOCKS = [
    {"name": "دواتکس", "aliases": ["دواتكس", "دواتکس", "داتکس"]},
    {"name": "آسیاتک", "aliases": ["اسياتك", "آسیاتک", "هسياتك", "هاتف"]},
]

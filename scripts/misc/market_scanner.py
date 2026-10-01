import os
import pandas as pd
import numpy as np

from history.history_database import HistoryDatabase
from database.database import Database

# ==========================================
# تنظیمات مسیر (ذخیره در پوشه reports)
# ==========================================
script_dir = os.path.dirname(os.path.abspath(__file__))
reports_dir = os.path.join(script_dir, "reports")
os.makedirs(reports_dir, exist_ok=True)
report_file_path = os.path.join(reports_dir, "market_scanner_report.txt")

# ==========================================
# 1. دریافت داده‌ها
# ==========================================
def get_stock_data(symbol):
    try:
        history_db = HistoryDatabase()
        history_db.connect()
        stocks_list = history_db.get_history(symbol, 365)
        history_db.close()

        if stocks_list is None or len(stocks_list) < 10:
            return None

        stocks_list = stocks_list[::-1] 

        data = {
            'Date': [s.trade_date for s in stocks_list],
            'Open': [s.open_price for s in stocks_list],
            'High': [s.high_price for s in stocks_list],
            'Low': [s.low_price for s in stocks_list],
            'Close': [s.close_price for s in stocks_list],
            'Volume': [s.volume for s in stocks_list]
        }
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)

        return df

    except Exception as e:
        print(f"خطا در خواندن داده از دیتابیس: {e}")
        return None

# ==========================================
# 2. توابع تحلیل تکنیکال
# ==========================================
def calculate_rsi(data, period=14):
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        
        # اگر مقدار rs یک عدد معتبر نبود، 50 برگردان
        if pd.isna(rs.iloc[-1]) or rs.iloc[-1] == 0:
            return 50.0
            
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])
    except:
        return 50.0

def calculate_macd(data, fast=12, slow=26, signal=9):
    try:
        exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
        exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return float(macd.iloc[-1]), float(signal_line.iloc[-1])
    except:
        return 0.0, 0.0

def calculate_moving_averages(data):
    try:
        ma_20 = float(data['Close'].rolling(window=20).mean().iloc[-1])
        ma_50 = float(data['Close'].rolling(window=50).mean().iloc[-1]) if len(data) >= 50 else None
        return ma_20, ma_50
    except:
        return 0.0, None

def check_support_resistance(data):
    try:
        recent_data = data.tail(30)
        support = float(recent_data['Low'].min())
        resistance = float(recent_data['High'].max())
        return support, resistance
    except:
        return 0.0, 0.0

# ==========================================
# 3. موتور تحلیل و تولید گزارش
# ==========================================
def analyze_symbol(symbol, data):
    if data is None or len(data) < 10:
        return f"{symbol}: داده کافی برای تحلیل وجود ندارد."

    rsi = calculate_rsi(data)
    macd_line, signal_line = calculate_macd(data)
    ma_20, ma_50 = calculate_moving_averages(data)
    support, resistance = check_support_resistance(data)
    last_close = float(data['Close'].iloc[-1])

    report = f"\n{'='*40}\nتحلیل تکنیکال سهم: {symbol}\n{'='*40}\n"
    report += f"آخرین قیمت بسته‌شدن: {last_close:.2f}\n"
    
    if ma_50 is not None:
        report += f"میانگین ۲۰ روزه: {ma_20:.2f} | میانگین ۵۰ روزه: {ma_50:.2f}\n"
    else:
        report += f"میانگین ۲۰ روزه: {ma_20:.2f} | میانگین ۵۰ روزه: نامشخص (کمتر از 50 روز داده)\n"

    report += f"RSI (14): {rsi:.2f}\n"
    report += f"MACD: {macd_line:.2f} | خط سیگنال: {signal_line:.2f}\n"
    report += f"مقاومت: {resistance:.2f} | حمایت: {support:.2f}\n\n"

    trend = "نامشخص"
    if ma_50 is not None:
        if ma_20 > ma_50:
            trend = "صعودی (میانگین کوتاه‌مدت بالای بلندمدت)"
        else:
            trend = "نزولی (میانگین کوتاه‌مدت پایین بلندمدت)"
    report += f"روند کلی: {trend}\n"

    if rsi < 30:
        rsi_signal = "اشباع فروش (منطقه خرید)"
    elif rsi > 70:
        rsi_signal = "اشباع خرید (منطقه ریسک/فروش)"
    else:
        rsi_signal = "خنثی (بدون فشار خاص)"
    report += f"سیگنال RSI: {rsi_signal}\n"

    if macd_line > signal_line:
        macd_signal = "مثبت (سیگنال خرید تکنیکال)"
    else:
        macd_signal = "منفی (سیگنال فروش تکنیکال)"
    report += f"سیگنال MACD: {macd_signal}\n"

    volatility = (resistance - support) / last_close * 100
    report += f"\n--- بخش نوسان‌گیری ---\n"
    report += f"بازه نوسان: {support:.0f} تا {resistance:.0f} (حدود {volatility:.2f} درصد)\n"
    if volatility > 10:
        report += "پتانسیل نوسان‌گیری: بالا (دامنه نوسان مناسب برای ورود و خروج سریع)\n"
    else:
        report += "پتانسیل نوسان‌گیری: پایین (بهتر است استراتژی بلندمدت یا خرید در کف اعمال شود)\n"

    report += "توصیه: برای تصمیم‌گیری نهایی، حتماً به حجم معاملات و شرایط بازار نیز توجه کنید.\n"
    return report

# ==========================================
# 4. اجرای اصلی
# ==========================================
def main():
    print("شروع تحلیل...")
    
    db = Database()
    db.connect()
    symbols = db.get_all_symbols()
    db.close()
    
    all_reports = []
    total = len(symbols)
    
    for idx, symbol_row in enumerate(symbols):
        symbol_name = symbol_row[1]
        
        if symbol_name.startswith('ح.'):
            continue
            
        if idx % 50 == 0:
            print(f"   تحلیل {idx}/{total} ...")
            
        try:
            data = get_stock_data(symbol_name)
            result = analyze_symbol(symbol_name, data)
            print(result)
            all_reports.append(result)
        except Exception as e:
            error_msg = f"\nخطا در پردازش {symbol_name}: {e}"
            print(error_msg)
            all_reports.append(error_msg)

    print(f"\nدر حال ذخیره گزارش در: {report_file_path}")
    with open(report_file_path, "w", encoding="utf-8") as f:
        f.write("گزارش کامل تحلیل تکنیکال سهام‌های انتخابی\n")
        f.write("تاریخ: " + str(pd.Timestamp.now()) + "\n")
        for rep in all_reports:
            f.write(rep)
            
    print("گزارش با موفقیت ذخیره شد!")

if __name__ == "__main__":
    main()

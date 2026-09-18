import pandas as pd
import json
import os

# خواندن فایل Excel (همون فایلی که از TSETMC گرفتی)
df = pd.read_excel("Iran Kh. Inv. (1).xlsx")

# ستون‌های مورد نیاز
df = df[['<DTYYYYMMDD>', '<OPEN>', '<HIGH>', '<LOW>', '<CLOSE>', '<VOL>']]

# تغییر نام ستون‌ها
df.columns = ['trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']

# تبدیل تاریخ
df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d').dt.strftime('%Y-%m-%d')

# تبدیل به لیست دیکشنری
data = df.to_dict(orient='records')

# ذخیره در پوشه data
os.makedirs("data", exist_ok=True)
with open("data/market_today.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ {len(data)} رکورد در data/market_today.json ذخیره شد.")

"""
create_fundamental_csv.py
ساخت فایل fundamental_data.csv با داده‌های نمونه
"""

import os
import pandas as pd

# ========== داده‌های نمونه ==========
data = {
    "symbol": ["فولاد", "فملی", "خودرو", "خگستر", "شپنا", "وبملت", "فارس", "شستا", "کگل", "حکشتی"],
    "pe_ratio": [4.2, 5.1, 8.5, 6.0, 3.8, 7.2, 5.5, 6.8, 4.5, 9.0],
    "roe": [0.32, 0.25, 0.18, 0.30, 0.35, 0.15, 0.28, 0.22, 0.30, 0.12],
    "profit_growth": [0.28, 0.18, 0.12, 0.22, 0.30, 0.10, 0.20, 0.15, 0.25, 0.08],
    "debt_to_equity": [0.25, 0.35, 0.55, 0.30, 0.20, 0.60, 0.28, 0.45, 0.22, 0.70],
    "sales_growth": [0.22, 0.15, 0.08, 0.20, 0.25, 0.05, 0.18, 0.12, 0.20, 0.04]
}

# ========== ساخت دیتافریم ==========
df = pd.DataFrame(data)

# ========== ذخیره در پوشه data ==========
os.makedirs("data", exist_ok=True)
csv_path = "data/fundamental_data.csv"
df.to_csv(csv_path, index=False, encoding='utf-8-sig')

print(f"✅ فایل {csv_path} با {len(df)} رکورد ساخته شد.")
print("\n📊 پیش‌نمایش داده‌ها:")
print(df.head())

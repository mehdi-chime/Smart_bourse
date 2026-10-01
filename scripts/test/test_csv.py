import pandas as pd
import os

csv_path = "data/fundamental_data.csv"

if os.path.exists(csv_path):
    print(f"✅ فایل {csv_path} پیدا شد.")
    df = pd.read_csv(csv_path)
    print(f"📊 تعداد رکوردها: {len(df)}")
    print(df.head())
else:
    print(f"❌ فایل {csv_path} پیدا نشد.")

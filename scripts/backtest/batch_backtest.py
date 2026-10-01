"""
batch_backtest.py
اجرای بک‌تست روی چند سهم به‌صورت همزمان
"""

import sys
from pathlib import Path

# تنظیم مسیر ریشه
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from ai.backtest_optimizer import BacktestOptimizer

symbols = ["خگستر", "خبهمن", "فولاد", "فملی"]

print("=" * 60)
print("🚀 اجرای بک‌تست گروهی")
print("=" * 60)

for s in symbols:
    print(f"\n📊 بک‌تست {s}")
    opt = BacktestOptimizer(s, 100_000_000)
    if opt.load_data():
        r = opt.run_strategy(-3, 3, 0.2)
        if r:
            print(f"   ✅ بازده {s}: {r['return_percent']:.2f}%")
            print(f"   📈 تعداد معاملات: {r['total_trades']}")
            print(f"   🏆 درصد برد: {r['win_rate']:.1f}%")
        else:
            print(f"   ❌ بک‌تست {s} نتیجه‌ای نداشت.")
    else:
        print(f"   ❌ داده‌ای برای {s} پیدا نشد.")

print("\n" + "=" * 60)
print("✅ بک‌تست گروهی کامل شد.")
print("=" * 60)

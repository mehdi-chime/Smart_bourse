# install_ai_backtest.py
# نصب خودکار بک‌تست کامل AI
# اجرا: python install_ai_backtest.py

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
AI_DIR = PROJECT_ROOT / "ai"

print("=" * 70)
print("  📊 نصب بک‌تست کامل AI")
print("=" * 70)
print()

# ===== قدم ۱: چک دیتابیس =====
print("📁 قدم ۱: چک دیتابیس...")
DB = PROJECT_ROOT / "data" / "smart_bourse_v2.db"
if not DB.exists():
    print(f"   ❌ پیدا نشد: {DB}")
    sys.exit(1)
print(f"   ✅ وجود دارد ({DB.stat().st_size / 1024 / 1024:.1f} MB)")
print()

# ===== قدم ۲: چک مدل ML =====
print("📁 قدم ۲: چک مدل ML...")
ML = PROJECT_ROOT / "data" / "ai" / "ml_model.pkl"
if ML.exists():
    print(f"   ✅ وجود دارد ({ML.stat().st_size:,} bytes)")
else:
    print(f"   ⚠️  پیدا نشد (بدون ML کار می‌کنه)")
print()

# ===== قدم ۳: ساخت فایل بک‌تست =====
print("📝 قدم ۳: ساخت ai/ai_backtest.py...")

backtest_content = '''# ai/ai_backtest.py
# بک‌تست کامل AI
# دقت واقعی رو از دیتابیس حساب می‌کنه

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(r"F:\\python\\har roz ba python\\smart_bours")
DB_PATH = PROJECT_ROOT / "data" / "smart_bourse_v2.db"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)


class AIBacktest:
    """بک‌تست AI از دیتابیس"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row

    def load_signals(self):
        """لود سیگنال‌ها"""
        cursor = self.conn.execute("SELECT * FROM signals ORDER BY trade_date")
        return [dict(row) for row in cursor.fetchall()]

    def load_outcomes(self):
        """لود نتایج"""
        cursor = self.conn.execute("SELECT * FROM outcomes")
        return [dict(row) for row in cursor.fetchall()]

    def match_signals_outcomes(self):
        """تطبیق سیگنال با نتیجه"""
        signals = self.load_signals()
        outcomes = self.load_outcomes()

        # کلید: (symbol, trade_date)
        outcome_map = {}
        for o in outcomes:
            key = (o.get("symbol"), o.get("trade_date"))
            outcome_map[key] = o

        matched = []
        for s in signals:
            key = (s.get("symbol"), s.get("trade_date"))
            if key in outcome_map:
                matched.append({
                    "signal": s,
                    "outcome": outcome_map[key]
                })

        return matched

    def compute_stats(self, matched):
        """محاسبه آمار"""
        if not matched:
            return None

        total = len(matched)
        wins = 0
        losses = 0
        total_return = 0

        by_symbol = defaultdict(lambda: {"wins": 0, "losses": 0, "return": 0})
        by_category = defaultdict(lambda: {"wins": 0, "losses": 0, "return": 0})

        for m in matched:
            s = m["signal"]
            o = m["outcome"]

            success = o.get("success", 0)
            ret = o.get("return_pct", 0) or 0

            if success:
                wins += 1
            else:
                losses += 1

            total_return += ret

            sym = s.get("symbol", "?")
            by_symbol[sym]["wins" if success else "losses"] += 1
            by_symbol[sym]["return"] += ret

            cat = s.get("category", "?")
            by_category[cat]["wins" if success else "losses"] += 1
            by_category[cat]["return"] += ret

        win_rate = wins / total * 100 if total > 0 else 0
        avg_return = total_return / total if total > 0 else 0

        return {
            "total": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "avg_return": round(avg_return, 2),
            "total_return": round(total_return, 2),
            "by_symbol": dict(by_symbol),
            "by_category": dict(by_category),
        }

    def run(self):
        """اجرای بک‌تست"""
        logger.info("=" * 60)
        logger.info("  📊 بک‌تست AI")
        logger.info("=" * 60)

        matched = self.match_signals_outcomes()
        logger.info(f"  ✅ {len(matched)} سیگنال با نتیجه تطبیق داده شد")

        if not matched:
            logger.warning("  ⚠️  هیچ سیگنالی تطبیق داده نشد!")
            return None

        stats = self.compute_stats(matched)

        logger.info("")
        logger.info("  📊 نتیجه:")
        logger.info(f"     کل: {stats['total']}")
        logger.info(f"     ✅ برد: {stats['wins']}")
        logger.info(f"     ❌ باخت: {stats['losses']}")
        logger.info(f"     🎯 Win Rate: {stats['win_rate']}%")
        logger.info(f"     💰 میانگین سود: {stats['avg_return']}%")
        logger.info(f"     💰 جمع سود: {stats['total_return']}%")

        # ذخیره
        report = {
            "date": datetime.now().isoformat(),
            "stats": stats,
        }
        report_file = REPORT_DIR / f"ai_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"")
        logger.info(f"  💾 ذخیره: {report_file}")

        return stats


def main():
    bt = AIBacktest()
    bt.run()


if __name__ == "__main__":
    main()
'''

backtest_file = AI_DIR / "ai_backtest.py"
backtest_file.write_text(backtest_content, encoding="utf-8")
print(f"   ✅ ساخته شد: {backtest_file}")
print()

# ===== قدم ۴: تست =====
print("=" * 70)
print("  🎯 قدم ۴: اجرای بک‌تست")
print("=" * 70)
print()

os.chdir(AI_DIR)
os.system(f"{sys.executable} ai_backtest.py")

print()
print("=" * 70)
print("  🎉 نصب کامل شد!")
print("=" * 70)
print()
print("📋 قدم بعدی: نتیجه رو بفرست تا بریم سراغ بهینه‌سازی.")
print()

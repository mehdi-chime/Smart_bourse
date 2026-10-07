# install_ai_backtest_fix.py
# اصلاح و اجرای بک‌تست AI
# اجرا: python install_ai_backtest_fix.py

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
AI_DIR = PROJECT_ROOT / "ai"

print("=" * 70)
print("  🔧 اصلاح و اجرای بک‌تست AI")
print("=" * 70)
print()

# ===== ساخت فایل اصلاح‌شده =====
print("📝 ساخت ai/ai_backtest.py (نسخه اصلاح‌شده)...")

backtest_content = '''# ai/ai_backtest.py
# بک‌تست کامل AI (نسخه اصلاح‌شده)

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
        cursor = self.conn.execute("SELECT * FROM signals ORDER BY date")
        return [dict(row) for row in cursor.fetchall()]

    def load_outcomes(self):
        cursor = self.conn.execute("SELECT * FROM outcomes")
        return [dict(row) for row in cursor.fetchall()]

    def match_signals_outcomes(self):
        signals = self.load_signals()
        outcomes = self.load_outcomes()

        # کلید: (symbol, date)
        outcome_map = {}
        for o in outcomes:
            key = (o.get("symbol"), o.get("date"))
            outcome_map[key] = o

        matched = []
        for s in signals:
            key = (s.get("symbol"), s.get("date"))
            if key in outcome_map:
                matched.append({
                    "signal": s,
                    "outcome": outcome_map[key]
                })

        return matched

    def compute_stats(self, matched):
        if not matched:
            return None

        total = len(matched)
        wins = 0
        losses = 0
        total_return = 0
        returns_list = []

        by_symbol = defaultdict(lambda: {"wins": 0, "losses": 0, "return": 0.0})
        by_category = defaultdict(lambda: {"wins": 0, "losses": 0, "return": 0.0})

        for m in matched:
            s = m["signal"]
            o = m["outcome"]

            success = o.get("success", 0)

            # محاسبه return از price_at_signal و price_after_7d
            p_signal = o.get("price_at_signal") or 0
            p_after = o.get("price_after_7d") or 0

            ret = 0.0
            if p_signal and p_after:
                ret = (p_after - p_signal) / p_signal * 100

            if success:
                wins += 1
            else:
                losses += 1

            total_return += ret
            returns_list.append(ret)

            sym = s.get("symbol", "?")
            by_symbol[sym]["wins" if success else "losses"] += 1
            by_symbol[sym]["return"] += ret

            cat = s.get("category", "?")
            by_category[cat]["wins" if success else "losses"] += 1
            by_category[cat]["return"] += ret

        win_rate = wins / total * 100 if total > 0 else 0
        avg_return = total_return / total if total > 0 else 0

        best = max(returns_list) if returns_list else 0
        worst = min(returns_list) if returns_list else 0

        return {
            "total": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 2),
            "avg_return": round(avg_return, 2),
            "total_return": round(total_return, 2),
            "best_return": round(best, 2),
            "worst_return": round(worst, 2),
            "by_symbol": dict(by_symbol),
            "by_category": dict(by_category),
        }

    def run(self):
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
        logger.info(f"     🏆 بهترین: {stats['best_return']}%")
        logger.info(f"     📉 بدترین: {stats['worst_return']}%")

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

        # Top symbols
        logger.info("")
        logger.info("  📊 بهترین سهم‌ها:")
        sorted_syms = sorted(
            stats["by_symbol"].items(),
            key=lambda x: -(x[1]["wins"] - x[1]["losses"])
        )[:5]
        for sym, data in sorted_syms:
            total_sym = data["wins"] + data["losses"]
            wr = data["wins"] / total_sym * 100 if total_sym > 0 else 0
            logger.info(f"     {sym}: {data['wins']}/{total_sym} ({wr:.0f}%)")

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

# ===== اجرا =====
print("=" * 70)
print("  🎯 اجرای بک‌تست")
print("=" * 70)
print()

os.chdir(AI_DIR)
os.system(f"{sys.executable} ai_backtest.py")

print()
print("=" * 70)
print("  🎉 تمام!")
print("=" * 70)
print()
print("📋 نتیجه رو بفرست تا بریم سراغ بهینه‌سازی.")
print()

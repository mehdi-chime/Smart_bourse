# install_ai_optimize.py
# نصب خودکار بهینه‌سازی AI
# اجرا: python install_ai_optimize.py

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
AI_DIR = PROJECT_ROOT / "ai"

print("=" * 70)
print("  🧠 نصب بهینه‌سازی AI")
print("=" * 70)
print()

# ===== قدم ۱: چک فایل‌ها =====
print("📁 قدم ۱: چک فایل‌ها...")
files_needed = [
    AI_DIR / "ai_engine.py",
    AI_DIR / "ml_model.py",
    AI_DIR / "trainer.py",
    PROJECT_ROOT / "data" / "smart_bourse_v2.db",
]
for f in files_needed:
    if f.exists():
        print(f"   ✅ {f.name}")
    else:
        print(f"   ❌ {f.name} پیدا نشد!")
print()

# ===== قدم ۲: ساخت ai/ai_optimizer.py =====
print("📝 قدم ۲: ساخت ai/ai_optimizer.py...")

optimizer_content = '''# ai/ai_optimizer.py
# بهینه‌ساز AI — از بک‌تست یاد می‌گیره
# هدف: Win Rate 34% → 50%+

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
WEIGHTS_FILE = PROJECT_ROOT / "data" / "ai" / "weights.json"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)


class AIOptimizer:
    """بهینه‌ساز AI — از داده‌های واقعی"""

    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row

    def load_matched(self):
        """لود سیگنال‌های تطبیق‌داده‌شده"""
        cursor = self.conn.execute("SELECT * FROM signals ORDER BY date")
        signals = [dict(row) for row in cursor.fetchall()]

        cursor = self.conn.execute("SELECT * FROM outcomes")
        outcomes = [dict(row) for row in cursor.fetchall()]

        outcome_map = {}
        for o in outcomes:
            key = (o.get("symbol"), o.get("date"))
            outcome_map[key] = o

        matched = []
        for s in signals:
            key = (s.get("symbol"), s.get("date"))
            if key in outcome_map:
                matched.append({"signal": s, "outcome": outcome_map[key]})
        return matched

    def analyze_patterns(self, matched):
        """تحلیل الگوهای موفق/ناموفق"""
        logger.info("  🔍 تحلیل الگوها...")

        success_data = {
            "rsi": [],
            "ratio": [],
            "technical_score": [],
            "final_score": [],
            "last_price": [],
        }
        fail_data = {
            "rsi": [],
            "ratio": [],
            "technical_score": [],
            "final_score": [],
            "last_price": [],
        }

        for m in matched:
            s = m["signal"]
            o = m["outcome"]
            success = o.get("success", 0)

            target = success_data if success else fail_data

            if s.get("rsi"): target["rsi"].append(s["rsi"])
            if s.get("ratio"): target["ratio"].append(s["ratio"])
            if s.get("technical_score"): target["technical_score"].append(s["technical_score"])
            if s.get("final_score"): target["final_score"].append(s["final_score"])
            if s.get("last_price"): target["last_price"].append(s["last_price"])

        def avg(lst):
            return sum(lst) / len(lst) if lst else 0

        logger.info("")
        logger.info("  📊 مقایسه موفق vs ناموفق:")
        logger.info(f"     {'ویژگی':<20} | {'موفق':>10} | {'ناموفق':>10}")
        logger.info("     " + "-" * 45)

        for key in ["rsi", "ratio", "technical_score", "final_score"]:
            s_avg = avg(success_data[key])
            f_avg = avg(fail_data[key])
            logger.info(f"     {key:<20} | {s_avg:>10.2f} | {f_avg:>10.2f}")

        return {"success": success_data, "fail": fail_data}

    def optimize_weights(self, patterns):
        """بهینه‌سازی وزن‌ها بر اساس الگوها"""
        logger.info("")
        logger.info("  ⚖️ بهینه‌سازی وزن‌ها...")

        # وزن‌های فعلی
        if WEIGHTS_FILE.exists():
            try:
                with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
                    weights = json.load(f)
            except:
                weights = {"money_flow": 0.4, "technical": 0.35, "context": 0.25}
        else:
            weights = {"money_flow": 0.4, "technical": 0.35, "context": 0.25}

        logger.info(f"     وزن‌های فعلی:")
        for k, v in weights.items():
            logger.info(f"        {k}: {v:.3f}")

        # ذخیره وزن‌های قبلی
        prev_weights = weights.copy()

        # بهینه‌سازی: اگه میانگین technical_score موفق بالاتر بود، وزن technical رو زیاد کن
        s_tech = patterns["success"]["technical_score"]
        f_tech = patterns["fail"]["technical_score"]

        if s_tech and f_tech:
            s_avg = sum(s_tech) / len(s_tech)
            f_avg = sum(f_tech) / len(f_tech)

            if s_avg > f_avg * 1.1:  # موفق‌ها ۱۰٪ بهتر
                weights["technical"] = min(0.5, weights["technical"] + 0.05)
                weights["money_flow"] = 1 - weights["technical"] - weights["context"]
                logger.info(f"     ⬆️ technical افزایش یافت به {weights['technical']:.3f}")

        # نرمال‌سازی
        total = sum(weights.values())
        for k in weights:
            weights[k] = round(weights[k] / total, 3)

        logger.info("")
        logger.info(f"     وزن‌های جدید:")
        for k, v in weights.items():
            diff = v - prev_weights.get(k, 0)
            arrow = "⬆️" if diff > 0.001 else "⬇️" if diff < -0.001 else "➡️"
            logger.info(f"        {arrow} {k}: {prev_weights.get(k, 0):.3f} → {v:.3f}")

        # ذخیره
        WEIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(WEIGHTS_FILE, "w", encoding="utf-8") as f:
            json.dump(weights, f, ensure_ascii=False, indent=2)
        logger.info(f"     💾 ذخیره: {WEIGHTS_FILE}")

        return weights

    def find_best_symbols(self, matched):
        """پیدا کردن بهترین سهم‌ها"""
        logger.info("")
        logger.info("  🏆 بهترین سهم‌ها (برای فیلتر):")

        by_symbol = defaultdict(lambda: {"wins": 0, "losses": 0, "returns": []})
        for m in matched:
            s = m["signal"]
            o = m["outcome"]
            sym = s.get("symbol", "?")

            p_signal = o.get("price_at_signal") or 0
            p_after = o.get("price_after_7d") or 0
            ret = (p_after - p_signal) / p_signal * 100 if p_signal and p_after else 0

            if o.get("success", 0):
                by_symbol[sym]["wins"] += 1
            else:
                by_symbol[sym]["losses"] += 1
            by_symbol[sym]["returns"].append(ret)

        # فیلتر: حداقل ۳ سیگنال
        good_symbols = []
        bad_symbols = []
        for sym, data in by_symbol.items():
            total = data["wins"] + data["losses"]
            if total < 3:
                continue
            wr = data["wins"] / total * 100
            avg_ret = sum(data["returns"]) / len(data["returns"])
            if wr >= 75 and avg_ret > 0:
                good_symbols.append({
                    "symbol": sym, "total": total, "win_rate": round(wr, 1),
                    "avg_return": round(avg_ret, 2)
                })
            elif wr <= 25:
                bad_symbols.append({"symbol": sym, "total": total, "win_rate": round(wr, 1)})

        good_symbols.sort(key=lambda x: -x["avg_return"])
        bad_symbols.sort(key=lambda x: x["win_rate"])

        logger.info("")
        logger.info("     ✅ سهم‌های خوب (اولویت):")
        for s in good_symbols[:10]:
            logger.info(f"        {s['symbol']}: {s['win_rate']}% ({s['total']} سیگنال, {s['avg_return']}%)")

        logger.info("")
        logger.info("     ⛔ سهم‌های بد (اجتناب):")
        for s in bad_symbols[:10]:
            logger.info(f"        {s['symbol']}: {s['win_rate']}% ({s['total']} سیگنال)")

        # ذخیره
        good_file = PROJECT_ROOT / "data" / "ai" / "good_symbols.json"
        bad_file = PROJECT_ROOT / "data" / "ai" / "bad_symbols.json"
        good_file.parent.mkdir(parents=True, exist_ok=True)
        with open(good_file, "w", encoding="utf-8") as f:
            json.dump(good_symbols, f, ensure_ascii=False, indent=2)
        with open(bad_file, "w", encoding="utf-8") as f:
            json.dump(bad_symbols, f, ensure_ascii=False, indent=2)
        logger.info("")
        logger.info(f"     💾 ذخیره: {good_file.name} + {bad_file.name}")

        return {"good": good_symbols, "bad": bad_symbols}

    def run(self):
        logger.info("=" * 60)
        logger.info("  🧠 بهینه‌ساز AI")
        logger.info("=" * 60)

        matched = self.load_matched()
        logger.info(f"  ✅ {len(matched)} سیگنال تطبیق داده شد")

        if not matched:
            return

        # ۱. تحلیل الگوها
        patterns = self.analyze_patterns(matched)

        # ۲. بهینه‌سازی وزن‌ها
        weights = self.optimize_weights(patterns)

        # ۳. بهترین/بدترین سهم‌ها
        symbols = self.find_best_symbols(matched)

        # ۴. ذخیره گزارش
        report = {
            "date": datetime.now().isoformat(),
            "total_signals": len(matched),
            "weights": weights,
            "good_symbols": symbols["good"],
            "bad_symbols": symbols["bad"],
        }
        report_file = REPORT_DIR / f"ai_optimize_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info("")
        logger.info("=" * 60)
        logger.info(f"  ✅ بهینه‌سازی تمام!")
        logger.info(f"  💾 گزارش: {report_file}")
        logger.info("=" * 60)


def main():
    optimizer = AIOptimizer()
    optimizer.run()


if __name__ == "__main__":
    main()
'''

optimizer_file = AI_DIR / "ai_optimizer.py"
optimizer_file.write_text(optimizer_content, encoding="utf-8")
print(f"   ✅ ساخته شد: {optimizer_file}")
print()

# ===== قدم ۳: اجرا =====
print("=" * 70)
print("  🎯 قدم ۳: اجرای بهینه‌ساز")
print("=" * 70)
print()

os.chdir(AI_DIR)
os.system(f"{sys.executable} ai_optimizer.py")

print()
print("=" * 70)
print("  🎉 نصب کامل شد!")
print("=" * 70)
print()
print("📋 نتیجه رو بفرست تا بریم سراغ مرحله ۳: XGBoost")
print()

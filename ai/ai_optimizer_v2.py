# ai/ai_optimizer_v2.py
# بهینه‌ساز AI نسخه ۲ — با success درست
# اجرا: python ai_optimizer_v2.py

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

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
DB_PATH = PROJECT_ROOT / "data" / "smart_bourse_v2.db"
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)


class AIOptimizerV2:
    """بهینه‌ساز AI با success درست"""

    def __init__(self, success_threshold=3.0):
        self.conn = sqlite3.connect(str(DB_PATH))
        self.conn.row_factory = sqlite3.Row
        self.success_threshold = success_threshold

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

    def recompute_success(self, matched):
        """محاسبه مجدد success با استاندارد +۳٪"""
        for m in matched:
            o = m["outcome"]
            p_signal = o.get("price_at_signal") or 0
            p_after = o.get("price_after_7d") or 0

            if p_signal and p_after:
                ret = (p_after - p_signal) / p_signal * 100
            else:
                ret = 0

            # ✅ success جدید: +۳٪ یا بیشتر
            m["new_success"] = 1 if ret >= self.success_threshold else 0
            m["return_pct"] = ret

    def analyze(self, matched):
        """تحلیل کامل"""
        total = len(matched)
        wins = sum(1 for m in matched if m["new_success"])
        losses = total - wins

        returns = [m["return_pct"] for m in matched]
        avg_ret = sum(returns) / total if total else 0

        # بر اساس ratio
        by_ratio_low = [m for m in matched if (m["signal"].get("ratio") or 0) < 2]
        by_ratio_high = [m for m in matched if (m["signal"].get("ratio") or 0) >= 2]

        low_wins = sum(1 for m in by_ratio_low if m["new_success"])
        high_wins = sum(1 for m in by_ratio_high if m["new_success"])

        return {
            "total": total,
            "wins": wins,
            "losses": losses,
            "win_rate": round(wins / total * 100, 2) if total else 0,
            "avg_return": round(avg_ret, 2),
            "ratio_low": {
                "total": len(by_ratio_low),
                "wins": low_wins,
                "win_rate": round(low_wins / len(by_ratio_low) * 100, 2) if by_ratio_low else 0,
            },
            "ratio_high": {
                "total": len(by_ratio_high),
                "wins": high_wins,
                "win_rate": round(high_wins / len(by_ratio_high) * 100, 2) if by_ratio_high else 0,
            },
        }

    def find_symbols(self, matched):
        """بهترین و بدترین سهم‌ها"""
        by_sym = defaultdict(lambda: {"wins": 0, "losses": 0, "returns": []})

        for m in matched:
            sym = m["signal"].get("symbol", "?")
            if m["new_success"]:
                by_sym[sym]["wins"] += 1
            else:
                by_sym[sym]["losses"] += 1
            by_sym[sym]["returns"].append(m["return_pct"])

        good = []
        bad = []
        for sym, d in by_sym.items():
            tot = d["wins"] + d["losses"]
            if tot < 3:
                continue
            wr = d["wins"] / tot * 100
            avg = sum(d["returns"]) / len(d["returns"])
            if wr >= 75 and avg > 0:
                good.append({"symbol": sym, "total": tot, "win_rate": round(wr, 1), "avg_return": round(avg, 2)})
            elif wr == 0:
                bad.append({"symbol": sym, "total": tot, "win_rate": 0})

        good.sort(key=lambda x: -x["avg_return"])
        return {"good": good, "bad": bad}

    def run(self):
        logger.info("=" * 60)
        logger.info("  🧠 بهینه‌ساز AI v2")
        logger.info(f"  🎯 success >= +{self.success_threshold}%")
        logger.info("=" * 60)

        matched = self.load_matched()
        logger.info(f"  ✅ {len(matched)} سیگنال تطبیق داده شد")
        logger.info("")

        # محاسبه مجدد success
        self.recompute_success(matched)
        logger.info("  🔄 success بازمحاسبه شد (استاندارد +۳٪)")
        logger.info("")

        # تحلیل
        stats = self.analyze(matched)
        logger.info("  📊 نتیجه:")
        logger.info(f"     کل: {stats['total']}")
        logger.info(f"     ✅ برد: {stats['wins']}")
        logger.info(f"     ❌ باخت: {stats['losses']}")
        logger.info(f"     🎯 Win Rate: {stats['win_rate']}%")
        logger.info(f"     💰 میانگین سود: {stats['avg_return']}%")
        logger.info("")
        logger.info("  📊 بر اساس ratio:")
        logger.info(f"     ratio < 2: {stats['ratio_low']['wins']}/{stats['ratio_low']['total']} ({stats['ratio_low']['win_rate']}%)")
        logger.info(f"     ratio >= 2: {stats['ratio_high']['wins']}/{stats['ratio_high']['total']} ({stats['ratio_high']['win_rate']}%)")

        # سهم‌ها
        symbols = self.find_symbols(matched)
        logger.info("")
        logger.info(f"  🏆 بهترین سهم‌ها ({len(symbols['good'])}):")
        for s in symbols["good"][:10]:
            logger.info(f"     {s['symbol']}: {s['win_rate']}% ({s['total']}، {s['avg_return']}%)")

        logger.info("")
        logger.info(f"  ⛔ بدترین سهم‌ها ({len(symbols['bad'])}):")
        for s in symbols["bad"][:10]:
            logger.info(f"     {s['symbol']}: {s['win_rate']}% ({s['total']})")

        # ذخیره
        report = {
            "date": datetime.now().isoformat(),
            "success_threshold": self.success_threshold,
            "stats": stats,
            "good_symbols": symbols["good"],
            "bad_symbols": symbols["bad"],
        }
        f = REPORT_DIR / f"ai_optimize_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(report, fp, ensure_ascii=False, indent=2)
        logger.info("")
        logger.info(f"  💾 گزارش: {f}")

        # ذخیره لیست‌ها
        good_f = PROJECT_ROOT / "data" / "ai" / "good_symbols_v2.json"
        bad_f = PROJECT_ROOT / "data" / "ai" / "bad_symbols_v2.json"
        good_f.parent.mkdir(parents=True, exist_ok=True)
        with open(good_f, "w", encoding="utf-8") as fp:
            json.dump(symbols["good"], fp, ensure_ascii=False, indent=2)
        with open(bad_f, "w", encoding="utf-8") as fp:
            json.dump(symbols["bad"], fp, ensure_ascii=False, indent=2)
        logger.info(f"  💾 سهم‌های خوب: {good_f.name}")
        logger.info(f"  💾 سهم‌های بد: {bad_f.name}")
        logger.info("=" * 60)


def main():
    opt = AIOptimizerV2(success_threshold=3.0)
    opt.run()


if __name__ == "__main__":
    main()

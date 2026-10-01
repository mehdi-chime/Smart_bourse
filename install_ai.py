# install_ai.py
# نصب و بازسازی AI — نسخه ۲.۰
# اجرا: python install_ai.py

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

AI_DIR = PROJECT_ROOT / "ai"
BACKUP_DIR = PROJECT_ROOT / "backup" / "ai"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def backup_ai():
    """بکاپ از کل پوشه ai/"""
    if not AI_DIR.exists():
        return None
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"ai_backup_{timestamp}"
    
    shutil.copytree(AI_DIR, backup_path)
    return backup_path


# ═══════════════════════════════════════════════════════════
# memory.py — نسخه ۲.۰
# ═══════════════════════════════════════════════════════════

MEMORY_V2 = '''"""
Project : Smart_Bourse
File    : ai/memory.py
Version : 2.0.0

Description :
    حافظه‌ی AI — ذخیره‌ی همه‌ی سیگنال‌ها و نتایج
    
Changes v2.0:
    - days_ago درست شد
    - فیلتر تاریخ واقعی
"""

import json
from datetime import datetime, timedelta
from pathlib import Path


class AIMemory:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.signals_file = self.base_dir / "memory.jsonl"
        self.outcomes_file = self.base_dir / "outcomes.jsonl"
        self.context_file = self.base_dir / "market_context.jsonl"

    def save_signal(self, trade_date, symbol, category, ratio,
                    rsi=None, technical_score=None, final_score=None,
                    last_price=None, context=None):
        entry = {
            "date": trade_date,
            "saved_at": datetime.now().isoformat(),
            "symbol": symbol,
            "category": category,
            "ratio": ratio,
            "rsi": rsi,
            "technical_score": technical_score,
            "final_score": final_score,
            "last_price": last_price,
            "context": context or {},
        }
        with open(self.signals_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\\n")

    def save_outcome(self, trade_date, symbol, category, price_at_signal,
                     price_after_1d=None, price_after_3d=None,
                     price_after_7d=None, success=None):
        entry = {
            "date": trade_date,
            "checked_at": datetime.now().isoformat(),
            "symbol": symbol,
            "category": category,
            "price_at_signal": price_at_signal,
            "price_after_1d": price_after_1d,
            "price_after_3d": price_after_3d,
            "price_after_7d": price_after_7d,
            "success": success,
        }
        with open(self.outcomes_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\\n")

    def save_context(self, trade_date, context):
        entry = {
            "date": trade_date,
            "saved_at": datetime.now().isoformat(),
            **context,
        }
        with open(self.context_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\\n")

    def load_signals(self):
        if not self.signals_file.exists():
            return []
        entries = []
        with open(self.signals_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
        return entries

    def load_outcomes(self):
        if not self.outcomes_file.exists():
            return []
        entries = []
        with open(self.outcomes_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
        return entries

    def get_pending_signals(self, days_ago=30):
        """
        سیگنال‌های چک‌نشده
        
        نسخه ۲.۰: days_ago درست کار می‌کند
        """
        signals = self.load_signals()
        outcomes = self.load_outcomes()
        checked = {(o["date"], o["symbol"]) for o in outcomes}
        
        # فیلتر تاریخ
        cutoff = datetime.now() - timedelta(days=days_ago)
        
        pending = []
        for s in signals:
            key = (s["date"], s["symbol"])
            if key in checked:
                continue
            
            # چک تاریخ
            try:
                signal_date = datetime.strptime(str(s["date"]), "%Y-%m-%d")
                if signal_date < cutoff:
                    continue
            except Exception:
                pass
            
            pending.append(s)
        
        return pending

    def stats(self):
        signals = self.load_signals()
        outcomes = self.load_outcomes()
        return {
            "total_signals": len(signals),
            "total_outcomes": len(outcomes),
            "pending": len(self.get_pending_signals()),
            "success_count": sum(1 for o in outcomes if o.get("success")),
            "failure_count": sum(1 for o in outcomes if o.get("success") is False),
        }
'''


# ═══════════════════════════════════════════════════════════
# learner.py — نسخه ۲.۰
# ═══════════════════════════════════════════════════════════

LEARNER_V2 = '''"""
Project : Smart_Bourse
File    : ai/learner.py
Version : 2.0.0
"""

import json
from datetime import datetime
from pathlib import Path


class AILearner:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.weights_file = self.base_dir / "weights.json"
        self.history_file = self.base_dir / "learning_history.json"
        
        self.default_weights = {
            "money_flow": 0.40,
            "technical": 0.35,
            "context": 0.25,
        }
        
        self.weight_limits = {
            "money_flow": (0.20, 0.60),
            "technical": (0.20, 0.60),
            "context": (0.10, 0.40),
        }
        
        self.min_outcomes = 10
        self.min_confidence = 3
        self.weight_step = 0.05
        
        self.weights = self.load_weights()

    def load_weights(self):
        if self.weights_file.exists():
            try:
                with open(self.weights_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "money_flow" in data:
                        return data
            except Exception:
                pass
        return dict(self.default_weights)

    def save_weights(self):
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, ensure_ascii=False, indent=2)

    def save_learning_history(self, entry):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        history.append(entry)
        history = history[-100:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

    def learn_from_outcomes(self, outcomes):
        if not outcomes:
            return {}
        
        stats = {}
        for o in outcomes:
            cat = o.get("category", "UNKNOWN")
            if cat not in stats:
                stats[cat] = {"total": 0, "success": 0, "fail": 0}
            
            stats[cat]["total"] += 1
            if o.get("success") is True:
                stats[cat]["success"] += 1
            elif o.get("success") is False:
                stats[cat]["fail"] += 1
        
        for cat, s in stats.items():
            if s["total"] > 0:
                s["success_rate"] = round(s["success"] / s["total"], 3)
            else:
                s["success_rate"] = 0.0
        
        return stats

    def adjust_weights(self, outcomes):
        if len(outcomes) < self.min_outcomes:
            return self.weights
        
        category_stats = self.learn_from_outcomes(outcomes)
        total_adjustments = 0
        
        for cat in ["SAFE_BUY", "SAFE_SELL", "QUEUE_BUY"]:
            if cat not in category_stats:
                continue
            
            rate = category_stats[cat]["success_rate"]
            total = category_stats[cat]["total"]
            
            if total < self.min_confidence:
                continue
            
            adjustments = self._adjust_for_category(cat, rate)
            total_adjustments += adjustments
        
        self._normalize_weights()
        self.save_weights()
        
        self.save_learning_history({
            "date": datetime.now().isoformat(),
            "total_outcomes": len(outcomes),
            "category_stats": category_stats,
            "weights_after": dict(self.weights),
            "adjustments": total_adjustments,
        })
        
        return self.weights

    def _adjust_for_category(self, category, rate):
        adjustments = 0
        
        if rate > 0.60:
            self._increase_weight("money_flow", self.weight_step)
            self._increase_weight("technical", self.weight_step * 0.5)
            adjustments += 2
        elif rate < 0.40:
            self._decrease_weight("money_flow", self.weight_step)
            self._decrease_weight("technical", self.weight_step * 0.5)
            adjustments += 2
        else:
            self._decrease_weight("context", self.weight_step * 0.3)
            adjustments += 1
        
        return adjustments

    def _increase_weight(self, key, amount):
        if key not in self.weights:
            return
        min_val, max_val = self.weight_limits.get(key, (0.0, 1.0))
        new_val = min(max_val, self.weights[key] + amount)
        self.weights[key] = round(new_val, 3)

    def _decrease_weight(self, key, amount):
        if key not in self.weights:
            return
        min_val, max_val = self.weight_limits.get(key, (0.0, 1.0))
        new_val = max(min_val, self.weights[key] - amount)
        self.weights[key] = round(new_val, 3)

    def _normalize_weights(self):
        total = sum(self.weights.values())
        if total > 0:
            for k in self.weights:
                self.weights[k] = round(self.weights[k] / total, 3)

    def get_confidence(self, category, outcomes):
        cat_outcomes = [o for o in outcomes if o.get("category") == category]
        
        if len(cat_outcomes) < self.min_confidence:
            return 0.5
        
        total_weight = 0
        success_weight = 0
        
        recent = cat_outcomes[-20:]
        
        for i, o in enumerate(recent):
            weight = 1 + (i * 0.05)
            total_weight += weight
            if o.get("success"):
                success_weight += weight
        
        if total_weight == 0:
            return 0.5
        
        raw_confidence = success_weight / total_weight
        count_bonus = min(0.1, len(cat_outcomes) * 0.005)
        confidence = min(1.0, raw_confidence + count_bonus)
        
        return round(confidence, 3)

    def report(self):
        print()
        print("=" * 70)
        print("  AILearner - Report (v2.0)")
        print("=" * 70)
        print()
        
        print("Weights:")
        for k, v in self.weights.items():
            print(f"   {k:<15} : {v}")
        print()
        
        print(f"Min outcomes    : {self.min_outcomes}")
        print(f"Min confidence  : {self.min_confidence}")
        print(f"Weight step     : {self.weight_step}")
        print()
        print("=" * 70)
        print()


if __name__ == "__main__":
    learner = AILearner()
    learner.report()
'''


# ═══════════════════════════════════════════════════════════
# ai_engine.py — نسخه ۲.۰
# ═══════════════════════════════════════════════════════════

AI_ENGINE_V2 = '''"""
Project : Smart_Bourse
File    : ai/ai_engine.py
Version : 2.0.0
"""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.memory import AIMemory
from ai.learner import AILearner


class AIEngine:

    def __init__(self):
        self.memory = AIMemory()
        self.learner = AILearner()

    def record_signal(self, trade_date, symbol, category, ratio,
                      rsi=None, technical_score=None, final_score=None,
                      last_price=None, market_change_pct=None):
        self.memory.save_signal(
            trade_date=trade_date,
            symbol=symbol,
            category=category,
            ratio=ratio,
            rsi=rsi,
            technical_score=technical_score,
            final_score=final_score,
            last_price=last_price,
            context={"market_change_pct": market_change_pct},
        )

    def check_outcomes(self, price_lookup_func, market_lookup_func=None):
        pending = self.memory.get_pending_signals()
        checked = 0
        skipped = 0
        today = datetime.now().date()

        for p in pending:
            symbol = p["symbol"]
            price_signal = p.get("last_price")
            signal_date_str = p.get("date")

            if not price_signal or not signal_date_str:
                skipped += 1
                continue

            try:
                signal_date = datetime.strptime(str(signal_date_str), "%Y-%m-%d").date()
                days_passed = (today - signal_date).days
            except Exception:
                skipped += 1
                continue

            if days_passed < 1:
                skipped += 1
                continue

            price_1d = price_lookup_func(symbol, 1) if days_passed >= 1 else None
            price_3d = price_lookup_func(symbol, 3) if days_passed >= 3 else None
            price_7d = price_lookup_func(symbol, 7) if days_passed >= 7 else None

            best_price = None
            for pc in [price_7d, price_3d, price_1d]:
                if pc:
                    best_price = pc
                    break

            if best_price:
                change_pct = (best_price - price_signal) / price_signal * 100
                cat = p["category"]
                success = None
                if cat == "SAFE_BUY":
                    success = change_pct > 1.0
                elif cat == "SAFE_SELL":
                    success = change_pct < -1.0
            else:
                success = None

            if success is None:
                skipped += 1
                continue

            self.memory.save_outcome(
                trade_date=p["date"],
                symbol=symbol,
                category=cat,
                price_at_signal=price_signal,
                price_after_1d=price_1d,
                price_after_3d=price_3d,
                price_after_7d=price_7d,
                success=success,
            )
            checked += 1

        if skipped > 0:
            print("   (" + str(skipped) + " skipped)")
        return checked

    def get_insight(self):
        stats = self.memory.stats()
        outcomes = self.memory.load_outcomes()
        category_stats = self.learner.learn_from_outcomes(outcomes)
        return {
            "memory": stats,
            "category_stats": category_stats,
            "weights": self.learner.weights,
        }

    def advise(self, symbol, category, ratio, rsi=None, technical_score=None,
               market_change_pct=None):
        outcomes = self.memory.load_outcomes()
        confidence = self.learner.get_confidence(category, outcomes)
        mf_score = self._score_money_flow(ratio)
        tech_score = technical_score or 50
        rsi_score = self._score_rsi(rsi)
        context_score = self._score_context(market_change_pct)
        w = self.learner.weights
        final = (
            w["money_flow"] * mf_score
            + w["technical"] * tech_score
            + w["context"] * context_score
        )
        advice = self._make_advice(category, final, confidence, rsi)
        return {
            "symbol": symbol,
            "category": category,
            "ratio": ratio,
            "rsi": rsi,
            "mf_score": mf_score,
            "tech_score": tech_score,
            "rsi_score": rsi_score,
            "context_score": context_score,
            "final_score": round(final, 1),
            "confidence": round(confidence, 2),
            "weights": w,
            "advice": advice,
        }

    @staticmethod
    def _score_money_flow(ratio):
        if ratio >= 10: return 100
        elif ratio >= 5: return 85
        elif ratio >= 2: return 65
        elif ratio >= 1: return 50
        elif ratio >= 0.5: return 35
        elif ratio >= 0.2: return 20
        return 10

    @staticmethod
    def _score_rsi(rsi):
        if rsi is None: return 50
        if rsi < 20: return 100
        elif rsi < 30: return 85
        elif rsi < 40: return 70
        elif rsi < 50: return 55
        elif rsi < 60: return 40
        elif rsi < 70: return 25
        else: return 10

    @staticmethod
    def _score_context(market_change_pct):
        if market_change_pct is None: return 50
        if market_change_pct > 2: return 80
        elif market_change_pct > 1: return 70
        elif market_change_pct > 0: return 60
        elif market_change_pct > -1: return 50
        elif market_change_pct > -2: return 40
        else: return 30

    @staticmethod
    def _make_advice(category, final_score, confidence, rsi):
        if rsi and rsi > 80:
            return "منتظر اصلاح بمان"
        if rsi and rsi < 30 and category == "SAFE_BUY":
            return "فرصت خوب"
        if category == "SAFE_BUY":
            if final_score > 75 and confidence > 0.6:
                return "کاندید قوی"
            elif final_score > 60:
                return "کاندید متوسط"
            else:
                return "ضعیف"
        if category == "SAFE_SELL":
            return "فشار فروش"
        if category == "QUEUE_BUY":
            return "صف خرید"
        return "معمولی"

    def report(self):
        insight = self.get_insight()
        print()
        print("=" * 70)
        print("  Smart_Bourse AI - Report (v2.0)")
        print("=" * 70)
        m = insight["memory"]
        print()
        print("Memory:")
        print("   Total signals    : " + str(m["total_signals"]))
        print("   Checked outcomes : " + str(m["total_outcomes"]))
        print("   Pending          : " + str(m["pending"]))
        print("   Success          : " + str(m["success_count"]))
        print("   Failed           : " + str(m["failure_count"]))
        print()
        print("Weights:")
        for k, v in insight["weights"].items():
            print("   " + k.ljust(15) + " : " + str(round(v, 3)))
        print("=" * 70)


if __name__ == "__main__":
    engine = AIEngine()
    engine.report()
'''


# ═══════════════════════════════════════════════════════════
# نصب
# ═══════════════════════════════════════════════════════════

def install_memory():
    path = AI_DIR / "memory.py"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "Version : 2.0.0" in content:
            safe_print("     ℹ️ memory.py از قبل نسخه ۲.۰ هست")
            return True
    path.write_text(MEMORY_V2, encoding="utf-8")
    safe_print("     ✅ memory.py v2.0 نصب شد")
    return True


def install_learner():
    path = AI_DIR / "learner.py"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "Version : 2.0.0" in content:
            safe_print("     ℹ️ learner.py از قبل نسخه ۲.۰ هست")
            return True
    path.write_text(LEARNER_V2, encoding="utf-8")
    safe_print("     ✅ learner.py v2.0 نصب شد")
    return True


def install_ai_engine():
    path = AI_DIR / "ai_engine.py"
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "Version : 2.0.0" in content:
            safe_print("     ℹ️ ai_engine.py از قبل نسخه ۲.۰ هست")
            return True
    path.write_text(AI_ENGINE_V2, encoding="utf-8")
    safe_print("     ✅ ai_engine.py v2.0 نصب شد")
    return True


def test_all():
    safe_print("")
    safe_print("  🧪 تست همه‌ی ماژول‌ها...")
    
    try:
        import importlib
        
        # پاک کردن کش
        for mod in ["ai.memory", "ai.learner", "ai.ai_engine"]:
            if mod in sys.modules:
                importlib.reload(sys.modules[mod])
        
        from ai.memory import AIMemory
        from ai.learner import AILearner
        from ai.ai_engine import AIEngine
        
        safe_print("     ✅ memory import موفق")
        safe_print("     ✅ learner import موفق")
        safe_print("     ✅ ai_engine import موفق")
        safe_print("")
        
        # تست learner
        learner = AILearner()
        safe_print("     وزن‌ها:")
        for k, v in learner.weights.items():
            safe_print(f"        {k:<15} : {v}")
        safe_print("")
        
        # تست ai_engine
        engine = AIEngine()
        result = engine.advise(
            symbol="خگستر",
            category="SAFE_BUY",
            ratio=5.0,
            rsi=25,
            technical_score=70,
            market_change_pct=1.5,
        )
        
        safe_print("     تست advise:")
        safe_print(f"        final_score: {result['final_score']}")
        safe_print(f"        confidence: {result['confidence']}")
        safe_print(f"        advice: {result['advice']}")
        safe_print("")
        safe_print(f"     mf_score: {result['mf_score']}")
        safe_print(f"     tech_score: {result['tech_score']}")
        safe_print(f"     rsi_score: {result['rsi_score']}")
        safe_print(f"     context_score: {result['context_score']}")
        
        return True
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        return False


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 نصب و بازسازی AI — نسخه ۲.۰")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بکاپ
    safe_print("  📦 بکاپ از ai/...")
    backup = backup_ai()
    if backup:
        safe_print(f"     ✅ {backup.name}")
    safe_print("")

    # ۲. نصب memory.py
    safe_print("  📝 نصب memory.py v2.0...")
    install_memory()
    safe_print("")

    # ۳. نصب learner.py
    safe_print("  📝 نصب learner.py v2.0...")
    install_learner()
    safe_print("")

    # ۴. نصب ai_engine.py
    safe_print("  📝 نصب ai_engine.py v2.0...")
    install_ai_engine()
    safe_print("")

    # ۵. تست
    test_all()
    safe_print("")

    # ۶. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ memory.py v2.0")
    safe_print("  ✅ learner.py v2.0")
    safe_print("  ✅ ai_engine.py v2.0")
    safe_print("")
    if backup:
        safe_print(f"  📦 بکاپ: {backup.name}")
    safe_print("")
    safe_print("  🎯 قدم بعدی:")
    safe_print("     - ML واقعی (فاز ۲)")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()

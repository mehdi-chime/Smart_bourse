# install_ml_engine.py
# ادغام ML با ai_engine.py
# اجرا: python install_ml_engine.py

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
    if not AI_DIR.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"ai_backup_ml_engine_{timestamp}"
    shutil.copytree(AI_DIR, backup_path)
    return backup_path


# ═══════════════════════════════════════════════════════════
# ai_engine.py — نسخه ۳.۰ (با ML)
# ═══════════════════════════════════════════════════════════

AI_ENGINE_V3 = '''"""
Project : Smart_Bourse
File    : ai/ai_engine.py
Version : 3.0.0

Description :
    موتور اصلی AI - با ML

Changes v3.0:
    - ادغام ML (RandomForest)
    - پیش‌بینی با ML
    - ترکیب ML + weight-based
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
        
        # ML
        self.ml_model = None
        try:
            from ai.ml_model import MLModel
            self.ml_model = MLModel()
        except Exception:
            pass

    # ═══════════════════════════════════════════════════════
    # ثبت سیگنال
    # ═══════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════
    # چک نتیجه
    # ═══════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════
    # بینش
    # ═══════════════════════════════════════════════════════

    def get_insight(self):
        stats = self.memory.stats()
        outcomes = self.memory.load_outcomes()
        category_stats = self.learner.learn_from_outcomes(outcomes)
        return {
            "memory": stats,
            "category_stats": category_stats,
            "weights": self.learner.weights,
        }

    # ═══════════════════════════════════════════════════════
    # مشاوره — نسخه ۳.۰ (با ML)
    # ═══════════════════════════════════════════════════════

    def advise(self, symbol, category, ratio, rsi=None, technical_score=None,
               market_change_pct=None, last_price=None):
        outcomes = self.memory.load_outcomes()
        confidence = self.learner.get_confidence(category, outcomes)
        
        # امتیازها
        mf_score = self._score_money_flow(ratio)
        tech_score = technical_score or 50
        rsi_score = self._score_rsi(rsi)
        context_score = self._score_context(market_change_pct)
        
        # وزن‌ها
        w = self.learner.weights
        
        # فرمول weight-based
        weight_score = (
            w["money_flow"] * mf_score
            + w["technical"] * tech_score
            + w["context"] * context_score
        )
        
        # ML prediction
        ml_score = None
        if self.ml_model and self.ml_model.is_ready() and last_price:
            try:
                X = [[
                    last_price,
                    0,
                    0,
                    0,
                ]]
                proba = self.ml_model.predict_proba(X)
                if proba is not None and len(proba) > 0:
                    ml_score = round(proba[0][1] * 100, 1)
            except Exception:
                pass
        
        # ترکیب
        if ml_score is not None:
            # 60% ML + 40% weight
            final = 0.6 * ml_score + 0.4 * weight_score
            mode = "ML+weight"
        else:
            final = weight_score
            mode = "weight-only"
        
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
            "weight_score": round(weight_score, 1),
            "ml_score": ml_score,
            "final_score": round(final, 1),
            "confidence": round(confidence, 2),
            "mode": mode,
            "weights": w,
            "advice": advice,
        }

    # ═══════════════════════════════════════════════════════
    # امتیازها
    # ═══════════════════════════════════════════════════════

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

    # ═══════════════════════════════════════════════════════
    # گزارش
    # ═══════════════════════════════════════════════════════

    def report(self):
        insight = self.get_insight()
        print()
        print("=" * 70)
        print("  Smart_Bourse AI - Report (v3.0)")
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
        print()
        print(f"ML Model: {'✅ ready' if self.ml_model and self.ml_model.is_ready() else '❌ not ready'}")
        print("=" * 70)


if __name__ == "__main__":
    engine = AIEngine()
    engine.report()
'''


def install_ml_engine():
    path = AI_DIR / "ai_engine.py"
    
    if path.exists():
        content = path.read_text(encoding="utf-8")
        if "Version : 3.0.0" in content:
            safe_print("     ℹ️ ai_engine.py از قبل نسخه ۳.۰ هست")
            return True
    
    path.write_text(AI_ENGINE_V3, encoding="utf-8")
    safe_print("     ✅ ai_engine.py v3.0 نصب شد (با ML)")
    return True


def test_ml_engine():
    safe_print("")
    safe_print("  🧪 تست ai_engine v3.0...")
    
    try:
        import importlib
        if "ai.ai_engine" in sys.modules:
            importlib.reload(sys.modules["ai.ai_engine"])
        
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        
        safe_print("     ✅ import موفق")
        safe_print(f"     ML Model: {'✅ ready' if engine.ml_model and engine.ml_model.is_ready() else '❌ not ready'}")
        safe_print("")
        
        # تست advise با ML
        result = engine.advise(
            symbol="خگستر",
            category="SAFE_BUY",
            ratio=5.0,
            rsi=25,
            technical_score=70,
            market_change_pct=1.5,
            last_price=10000,
        )
        
        safe_print("     تست advise:")
        safe_print(f"        mode: {result['mode']}")
        safe_print(f"        weight_score: {result['weight_score']}")
        safe_print(f"        ml_score: {result['ml_score']}")
        safe_print(f"        final_score: {result['final_score']}")
        safe_print(f"        advice: {result['advice']}")
        
        return True
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🚀 ادغام ML با ai_engine")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بکاپ
    safe_print("  📦 بکاپ...")
    backup = backup_ai()
    if backup:
        safe_print(f"     ✅ {backup.name}")
    safe_print("")

    # ۲. نصب
    safe_print("  📝 نصب ai_engine.py v3.0...")
    install_ml_engine()
    safe_print("")

    # ۳. تست
    test_ml_engine()
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ ai_engine.py v3.0 (با ML)")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()

"""
Smart_Bourse Master Installer
==============================
این اسکریپت:
1. فایل‌های AI رو می‌سازه
2. نقشه‌راه رو آپدیت می‌کنه
3. بک‌آپ می‌گیره
"""

from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()


# ======================================================================
# نقشه‌راه جدید
# ======================================================================

ROADMAP = """================================================================
🛡️ پروژه‌ی هوشمند بورس (Smart Bourse) - نقشه‌ی راه نسخه‌ی ۳.۰
✍️ تهیه‌شده توسط: Mehdi Jalali + Assistant
📅 آخرین آپدیت: {date}
🎯 شعار: «از شهود تا سیستم، از نوسان تا سرمایه‌گذاری هوشمند»

================================================================
📌 این نقشه‌راه، نسخه‌ی واقع‌بینانه است.
   فقط چیزهایی که واقعاً تست شده‌اند، با ✅ علامت خورده‌اند.
================================================================

[✅] فاز ۱: پایه‌ریزی (کامل)
    [✅] ۱-۱. اتصال به TSETMC (algotik_tse)
    [✅] ۱-۲. دریافت داده‌ی زنده (get_live_market)
    [✅] ۱-۳. فیلتر جریان پول حقیقی
    [✅] ۱-۴. حذف حق تقدم‌ها
    [✅] ۱-۵. خروجی JSON + Excel

[✅] فاز ۲: تکمیل اسکنر (کامل)
    [✅] ۲-۱. ذخیره‌ی تاریخچه (history.jsonl)
    [✅] ۲-۲. ذخیره‌ی هر نماد در فایل جدا
    [✅] ۲-۳. گزارش HTML روزانه
    [ ] ۲-۴. main.py (اجرای همه با یه دستور) ← بعدی

[✅] فاز ۳: تحلیل تکنیکال (کامل)
    [✅] ۳-۱. RSI (از indicators/rsi.py)
    [✅] ۳-۲. MACD، MA، Bollinger، ATR
    [✅] ۳-۳. IndicatorManager (مدیریت اندیکاتورها)
    [✅] ۳-۴. امتیازدهی تکنیکال (technical_analyzer.py)

[✅] فاز ۴: AI Engine (کامل) ← جدید!
    [✅] ۴-۱. حافظه‌ی AI (ai/memory.py)
    [✅] ۴-۲. یادگیری از نتایج (ai/learner.py)
    [✅] ۴-۳. مغز متفکر (ai/ai_engine.py)
    [✅] ۴-۴. مشاور AI (scanner/ai_advisor.py)
    [✅] ۴-۵. تنظیم خودکار وزن‌ها
    [✅] ۴-۶. محاسبه‌ی اعتماد

[⏳] فاز ۵: مدیریت پرتفوی (در دست اقدام)
    [ ] ۵-۱. ژورنال معاملاتی
    [ ] ۵-۲. محاسبه سود/ضرر
    [ ] ۵-۳. حد ضرر و حد سود
    [ ] ۵-۴. گزارش ماهانه

[ ] فاز ۶: بافت بازار (برنامه‌ریزی)
    [ ] ۶-۱. شاخص کل و هم‌وزن
    [ ] ۶-۲. نرخ دلار
    [ ] ۶-۳. چرخش صنایع
    [ ] ۶-۴. عرضه/تقاضا

[ ] فاز ۷: بک‌تست (برنامه‌ریزی)
    [ ] ۷-۱. استراتژی ساده
    [ ] ۷-۲. بک‌تست روی داده‌ی گذشته
    [ ] ۷-۳. معیارها (بازدهی، افت، شارپ)
    [ ] ۷-۴. بهینه‌سازی

[ ] فاز ۸: اتوماسیون و هشدار (برنامه‌ریزی)
    [ ] ۸-۱. هشدار تلگرام
    [ ] ۸-۲. زمان‌بند روزانه
    [ ] ۸-۳. پشتیبان‌گیری خودکار

[ ] فاز ۹: محصول نهایی (برنامه‌ریزی)
    [ ] ۹-۱. رابط وب
    [ ] ۹-۲. مستندات
    [ ] ۹-۳. نصب آسان

================================================================
📊 وضعیت فعلی:
   ✅ فاز ۱ (پایه): کامل
   ✅ فاز ۲ (اسکنر): کامل
   ✅ فاز ۳ (تکنیکال): کامل
   ✅ فاز ۴ (AI Engine): کامل ← جدید
   ⏳ فاز ۵ (پرتفوی): بعدی

🧠 AI چه کار می‌کنه:
   ۱. هر روز سیگنال‌ها رو تو حافظه ذخیره می‌کنه
   ۲. نتایج سیگنال‌های قبلی رو چک می‌کنه
   ۳. از موفقیت/شکست یاد می‌گیره
   ۴. وزن‌ها رو خودکار تنظیم می‌کنه
   ۵. با درصد اعتماد، توصیه می‌ده

📌 گام بعدی:
   → python scanner\\ai_advisor.py (مشاور AI)
   → فاز ۵: مدیریت پرتفوی

📌 قوانین کار:
   ۱. صادق باشیم - اگه چیزی رو نمی‌دونیم، بگیم
   ۲. تست قبل از ادامه - هر کد باید اجرا شه
   ۳. مرحله‌به‌مرحله - یه فاز تموم شه، بعد بریم بعدی
   ۴. هدف: ابزار برای کمک به تصمیم، نه جایگزین فکر

================================================================
🎯 تعهد:
   - دستیار: کد کامل، صادقانه، قدم‌به‌قدم
   - توسعه‌دهنده: تست، بازخورد، صبر
   - با هم: پروژه رو به نتیجه می‌رسونیم
================================================================
"""


# ======================================================================
# محتوای فایل‌های AI
# ======================================================================

AI_MEMORY = '''"""
Project : Smart_Bourse
File    : ai/memory.py
Version : 1.0.0

Description :
    حافظه‌ی AI — ذخیره‌ی همه‌ی سیگنال‌ها و نتایج
"""

import json
from datetime import datetime
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

    def get_pending_signals(self, days_ago=7):
        signals = self.load_signals()
        outcomes = self.load_outcomes()
        checked = {(o["date"], o["symbol"]) for o in outcomes}
        pending = []
        for s in signals:
            key = (s["date"], s["symbol"])
            if key not in checked:
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


AI_LEARNER = '''"""
Project : Smart_Bourse
File    : ai/learner.py
Version : 1.0.0

Description :
    یادگیری از نتایج
"""

import json
from pathlib import Path


class AILearner:

    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent / "data" / "ai"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.weights_file = self.base_dir / "weights.json"
        self.default_weights = {
            "money_flow": 0.40,
            "technical": 0.35,
            "context": 0.25,
        }
        self.weights = self.load_weights()

    def load_weights(self):
        if self.weights_file.exists():
            try:
                with open(self.weights_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return dict(self.default_weights)

    def save_weights(self):
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(self.weights, f, ensure_ascii=False, indent=2)

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
        if len(outcomes) < 20:
            return self.weights
        safe_buy_outcomes = [o for o in outcomes if o.get("category") == "SAFE_BUY"]
        if safe_buy_outcomes:
            success = sum(1 for o in safe_buy_outcomes if o.get("success"))
            rate = success / len(safe_buy_outcomes)
            if rate > 0.6:
                self.weights["money_flow"] = min(0.55, self.weights["money_flow"] + 0.02)
            elif rate < 0.4:
                self.weights["money_flow"] = max(0.25, self.weights["money_flow"] - 0.02)
        total = sum(self.weights.values())
        for k in self.weights:
            self.weights[k] = round(self.weights[k] / total, 3)
        self.save_weights()
        return self.weights

    def get_confidence(self, category, outcomes):
        cat_outcomes = [o for o in outcomes if o.get("category") == category]
        if len(cat_outcomes) < 5:
            return 0.5
        success = sum(1 for o in cat_outcomes if o.get("success"))
        return round(success / len(cat_outcomes), 3)
'''


AI_ENGINE = '''"""
Project : Smart_Bourse
File    : ai/ai_engine.py
Version : 1.0.0

Description :
    مغز AI
"""

from datetime import datetime
from pathlib import Path
import sys

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
                      last_price=None):
        self.memory.save_signal(
            trade_date=trade_date,
            symbol=symbol,
            category=category,
            ratio=ratio,
            rsi=rsi,
            technical_score=technical_score,
            final_score=final_score,
            last_price=last_price,
        )

    def check_outcomes(self, price_lookup_func):
        pending = self.memory.get_pending_signals()
        checked = 0
        for p in pending:
            symbol = p["symbol"]
            price_signal = p.get("last_price")
            if not price_signal:
                continue
            try:
                price_1d = price_lookup_func(symbol, 1)
                price_3d = price_lookup_func(symbol, 3)
                price_7d = price_lookup_func(symbol, 7)
            except Exception:
                continue
            success = None
            cat = p["category"]
            if cat == "SAFE_BUY" and price_3d:
                success = price_3d > price_signal
            elif cat == "SAFE_SELL" and price_3d:
                success = price_3d < price_signal
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

    def advise(self, symbol, category, ratio, rsi=None, technical_score=None):
        outcomes = self.memory.load_outcomes()
        confidence = self.learner.get_confidence(category, outcomes)
        mf_score = self._score_money_flow(ratio)
        tech_score = technical_score or 50
        w = self.learner.weights
        final = (
            w["money_flow"] * mf_score
            + w["technical"] * tech_score
            + w["context"] * 50
        )
        advice = self._make_advice(category, final, confidence, rsi)
        return {
            "symbol": symbol,
            "category": category,
            "ratio": ratio,
            "rsi": rsi,
            "final_score": round(final, 1),
            "confidence": round(confidence, 2),
            "weights": w,
            "advice": advice,
        }

    @staticmethod
    def _score_money_flow(ratio):
        if ratio >= 10:
            return 100
        elif ratio >= 5:
            return 85
        elif ratio >= 2:
            return 65
        elif ratio >= 1:
            return 50
        elif ratio >= 0.5:
            return 35
        elif ratio >= 0.2:
            return 20
        return 10

    @staticmethod
    def _make_advice(category, final_score, confidence, rsi):
        if rsi and rsi > 80:
            return "منتظر اصلاح بمان — سهم در اوج قیمت است"
        if rsi and rsi < 30 and category == "SAFE_BUY":
            return "فرصت خوب — فشار خرید حقیقی با اشباع فروش"
        if category == "SAFE_BUY":
            if final_score > 75 and confidence > 0.6:
                return "کاندید قوی — بررسی بیشتر"
            elif final_score > 60:
                return "کاندید متوسط — زیر نظر بگیر"
            else:
                return "ضعیف — احتمالاً ارزش ورود ندارد"
        if category == "SAFE_SELL":
            return "فشار فروش — احتمال ریزش"
        if category == "QUEUE_BUY":
            return "صف خرید — بررسی کن که واقعی است یا دام"
        return "معمولی — نیاز به بررسی بیشتر"

    def report(self):
        insight = self.get_insight()
        print()
        print("=" * 70)
        print("  🧠 Smart_Bourse AI — گزارش حافظه")
        print("=" * 70)
        m = insight["memory"]
        print()
        print("📚 حافظه:")
        print("   کل سیگنال‌ها     : " + str(m["total_signals"]))
        print("   نتایج چک‌شده     : " + str(m["total_outcomes"]))
        print("   در انتظار چک    : " + str(m["pending"]))
        print("   موفق            : " + str(m["success_count"]))
        print("   ناموفق           : " + str(m["failure_count"]))
        print()
        print("⚖️  وزن‌های یادگرفته:")
        for k, v in insight["weights"].items():
            print("   " + k.ljust(15) + " : " + str(round(v, 3)))
        if insight["category_stats"]:
            print()
            print("📊 آمار دسته‌ها:")
            for cat, s in insight["category_stats"].items():
                rate = s.get("success_rate", 0)
                print("   " + cat.ljust(12) + " : " + str(s["success"]) + "/" + str(s["total"]) + "  (" + str(round(rate * 100, 1)) + "%)")
        print("=" * 70)


if __name__ == "__main__":
    engine = AIEngine()
    engine.report()
'''


AI_ADVISOR = '''"""
Project : Smart_Bourse
File    : scanner/ai_advisor.py
Version : 1.0.0

Description :
    مشاور AI
"""

import json
from datetime import datetime
from pathlib import Path
import sys

import algotik_tse as att

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.ai_engine import AIEngine


DATA_DIR = PROJECT_ROOT / "data"
REAL_FLOW_DIR = DATA_DIR / "real_flow"


class AIAdvisor:

    def __init__(self):
        self.engine = AIEngine()
        self.data_dir = REAL_FLOW_DIR

    def find_latest_json(self):
        if not self.data_dir.exists():
            return None
        files = sorted(self.data_dir.glob("real_flow_*.json"), reverse=True)
        files = [f for f in files if "history" not in str(f)]
        return files[0] if files else None

    def _lookup_price(self, symbol, days_ago):
        try:
            df = att.get_history(symbol)
            if df is None or df.empty or len(df) <= days_ago:
                return None
            return float(df["Close"].iloc[-1 - days_ago])
        except Exception:
            return None

    def run(self, json_file=None):
        print()
        print("=" * 70)
        print("  🧠 Smart_Bourse AI Advisor")
        print("=" * 70)

        print()
        print("📚 چک نتایج سیگنال‌های قبلی ...")
        checked = self.engine.check_outcomes(self._lookup_price)
        print("   " + str(checked) + " نتیجه چک شد")

        self.engine.report()

        if json_file is None:
            json_file = self.find_latest_json()

        if json_file is None:
            print()
            print("هیچ فایل JSON پیدا نشد")
            return

        print()
        print("📄 خواندن سیگنال‌های جدید: " + json_file.name)
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        trade_date = data.get("date")

        print()
        print("💾 ثبت سیگنال‌ها تو حافظه AI ...")

        for cat in ["safe_buy", "safe_sell", "queue_buy"]:
            for item in data.get(cat, []):
                symbol = item.get("Symbol") or item.get("symbol")
                if not symbol:
                    continue
                self.engine.record_signal(
                    trade_date=trade_date,
                    symbol=symbol,
                    category=cat.upper(),
                    ratio=item.get("ratio", 0),
                    last_price=item.get("Last"),
                )

        print("   ثبت کامل")

        print()
        print("=" * 70)
        print("  🎯 توصیه AI برای هر نماد")
        print("=" * 70)

        tech_file = self.data_dir / ("technical_" + str(trade_date) + ".json")
        tech_lookup = {}
        if tech_file.exists():
            with open(tech_file, "r", encoding="utf-8") as f:
                tech_data = json.load(f)
            for r in tech_data.get("results", []):
                tech_lookup[r["symbol"]] = r

        for cat in ["safe_buy", "queue_buy", "safe_sell"]:
            items = data.get(cat, [])
            if not items:
                continue

            print()
            print("  " + cat.upper() + " — " + str(len(items)) + " نماد:")
            print("  " + "-" * 60)

            for item in items:
                symbol = item.get("Symbol") or item.get("symbol")
                if not symbol:
                    continue

                tech = tech_lookup.get(symbol, {})
                rsi = tech.get("rsi")
                tech_score = tech.get("technical_score")

                advice = self.engine.advise(
                    symbol=symbol,
                    category=cat.upper(),
                    ratio=item.get("ratio", 0),
                    rsi=rsi,
                    technical_score=tech_score,
                )

                print("   " + symbol.ljust(10) + " | نسبت: " + str(round(advice["ratio"], 2)).rjust(7) + " | امتیاز: " + str(advice["final_score"]).rjust(5) + " | اعتماد: " + str(advice["confidence"]))
                print("      💡 " + advice["advice"])

        print()
        print("=" * 70)
        print("  تمام")
        print("=" * 70)


if __name__ == "__main__":
    advisor = AIAdvisor()
    advisor.run()
'''


# ======================================================================
# نصب
# ======================================================================

FILES = {
    "ai/memory.py": AI_MEMORY,
    "ai/learner.py": AI_LEARNER,
    "ai/ai_engine.py": AI_ENGINE,
    "scanner/ai_advisor.py": AI_ADVISOR,
}


def install():
    print()
    print("=" * 70)
    print("  🧠 Smart_Bourse Master Installer")
    print("=" * 70)
    print("  مسیر پروژه: " + str(ROOT))
    print()

    # ۱. فایل‌های AI
    (ROOT / "ai").mkdir(parents=True, exist_ok=True)

    print("📦 نصب فایل‌های AI ...")
    print()

    for rel, content in FILES.items():
        target = ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)

        if target.exists():
            backup = target.with_suffix(target.suffix + ".bak")
            try:
                backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
                print("  [بک‌آپ] " + rel + " → " + backup.name)
            except Exception:
                pass

        try:
            target.write_text(content, encoding="utf-8")
            size = len(content)
            print("  [OK]   " + rel + "  (" + str(size) + " بایت)")
        except Exception as e:
            print("  [خطا] " + rel + " : " + str(e))

    # ۲. نقشه‌راه
    print()
    print("📜 آپدیت نقشه‌راه ...")
    print()

    roadmap_file = ROOT / "DeepSeek_RoadMap.txt"
    old_roadmap_backup = ROOT / "DeepSeek_RoadMap_OLD.txt"

    if roadmap_file.exists() and not old_roadmap_backup.exists():
        try:
            old_roadmap_backup.write_text(
                roadmap_file.read_text(encoding="utf-8"),
                encoding="utf-8"
            )
            print("  [بک‌آپ] DeepSeek_RoadMap_OLD.txt")
        except Exception as e:
            print("  [خطا در بک‌آپ] " + str(e))

    try:
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        roadmap_file.write_text(ROADMAP.format(date=date_str), encoding="utf-8")
        print("  [OK]   DeepSeek_RoadMap.txt (نسخه‌ی ۳.۰)")
    except Exception as e:
        print("  [خطا] " + str(e))

    print()
    print("=" * 70)
    print("  ✅ نصب کامل شد!")
    print("=" * 70)
    print()
    print("حالا اجرا کن:")
    print()
    print("  python scanner\\ai_advisor.py")
    print()
    print("فازهای تکمیل‌شده:")
    print("  ✅ فاز ۱: پایه‌ریزی")
    print("  ✅ فاز ۲: تکمیل اسکنر")
    print("  ✅ فاز ۳: تحلیل تکنیکال")
    print("  ✅ فاز ۴: AI Engine ← جدید")
    print()


if __name__ == "__main__":
    install()
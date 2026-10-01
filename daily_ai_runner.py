"""
Project : Smart_Bourse
File    : daily_ai_runner.py
Version : 1.0.0

Description :
    رانر روزانه AI — ادغام با برنامه اصلی
"""

import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.ai_engine import AIEngine


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def load_signals():
    """بارگذاری سیگنال‌های امروز از hunter"""
    hunter_dir = PROJECT_ROOT / "data" / "hunter"
    today = datetime.now().strftime("%Y-%m-%d")
    
    signals = []
    
    # پیدا کردن فایل امروز
    for f in hunter_dir.glob(f"*{today}*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if "top" in data:
                for s in data["top"]:
                    signals.append({
                        "symbol": s.get("symbol"),
                        "category": "SAFE_BUY",
                        "ratio": s.get("ratio", 1),
                        "rsi": s.get("rsi"),
                        "technical_score": s.get("score", 50),
                        "last_price": s.get("last"),
                    })
        except Exception:
            pass
    
    return signals


def record_signals_to_ai():
    """ثبت سیگنال‌ها در AI"""
    safe_print("  📝 ثبت سیگنال‌ها در AI...")
    
    signals = load_signals()
    
    if not signals:
        safe_print("     ⚠️ سیگنالی پیدا نشد")
        return 0
    
    engine = AIEngine()
    today = datetime.now().strftime("%Y-%m-%d")
    
    count = 0
    for s in signals:
        engine.record_signal(
            trade_date=today,
            symbol=s["symbol"],
            category=s["category"],
            ratio=s["ratio"],
            rsi=s["rsi"],
            technical_score=s["technical_score"],
            last_price=s["last_price"],
        )
        count += 1
    
    safe_print(f"     ✅ {count} سیگنال ثبت شد")
    return count


def check_outcomes_from_ai():
    """چک نتایج قبلی"""
    safe_print("  🔍 چک نتایج قبلی...")
    
    engine = AIEngine()
    
    # تابع ساده برای چک قیمت
    def price_lookup(symbol, days):
        """چک قیمت N روز قبل"""
        try:
            from history.history_database import HistoryDatabase
            db = HistoryDatabase()
            
            # فعلاً ساده
            return None
        except Exception:
            return None
    
    checked = engine.check_outcomes(price_lookup)
    safe_print(f"     ✅ {checked} نتیجه چک شد")
    return checked


def report_ai():
    """گزارش AI"""
    safe_print("")
    safe_print("  📊 گزارش AI...")
    
    engine = AIEngine()
    engine.report()


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🤖 رانر روزانه AI")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    # ۱. ثبت سیگنال‌ها
    record_signals_to_ai()
    safe_print("")

    # ۲. چک نتایج
    check_outcomes_from_ai()
    safe_print("")

    # ۳. گزارش
    report_ai()
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()

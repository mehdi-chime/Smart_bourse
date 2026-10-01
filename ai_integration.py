"""
Project : Smart_Bourse
File    : ai_integration.py
Version : 1.0.0

Description :
    ادغام AI با برنامه اصلی
    استفاده در smart_bourse_v10 و اسکنرها
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_ai_advice(symbol, category, ratio, rsi=None, technical_score=None,
                  market_change_pct=None, last_price=None):
    """
    دریافت مشاوره AI برای یه سهم
    
    Returns:
        dict با کلیدهای: final_score, advice, confidence, mode
    """
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        
        return engine.advise(
            symbol=symbol,
            category=category,
            ratio=ratio,
            rsi=rsi,
            technical_score=technical_score,
            market_change_pct=market_change_pct,
            last_price=last_price,
        )
    except Exception as e:
        return {
            "symbol": symbol,
            "final_score": 50,
            "advice": f"AI error: {e}",
            "confidence": 0.5,
            "mode": "error",
        }


def record_ai_signal(symbol, category, ratio, rsi=None,
                     technical_score=None, last_price=None):
    """ثبت سیگنال در AI"""
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        
        today = datetime.now().strftime("%Y-%m-%d")
        engine.record_signal(
            trade_date=today,
            symbol=symbol,
            category=category,
            ratio=ratio,
            rsi=rsi,
            technical_score=technical_score,
            last_price=last_price,
        )
        return True
    except Exception:
        return False


def enhance_scanner_results(results):
    """
    غنی‌سازی نتایج اسکنر با AI
    
    Args:
        results: لیست نتایج اسکنر
    
    Returns:
        لیست غنی‌شده با AI
    """
    enhanced = []
    
    for r in results:
        try:
            symbol = r.get("symbol", "")
            ratio = r.get("ratio", 1)
            rsi = r.get("rsi")
            tech = r.get("score", 50)
            price = r.get("last")
            
            # مشاوره AI
            advice = get_ai_advice(
                symbol=symbol,
                category="SAFE_BUY",
                ratio=ratio,
                rsi=rsi,
                technical_score=tech,
                last_price=price,
            )
            
            # ترکیب
            r["ai_score"] = advice.get("final_score", 50)
            r["ai_advice"] = advice.get("advice", "")
            r["ai_confidence"] = advice.get("confidence", 0.5)
            r["ai_mode"] = advice.get("mode", "")
            
            # ثبت
            record_ai_signal(
                symbol=symbol,
                category="SAFE_BUY",
                ratio=ratio,
                rsi=rsi,
                technical_score=tech,
                last_price=price,
            )
            
            enhanced.append(r)
        except Exception:
            enhanced.append(r)
    
    return enhanced


def print_ai_summary():
    """خلاصه‌ی AI"""
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        engine.report()
    except Exception as e:
        print(f"AI error: {e}")


if __name__ == "__main__":
    print()
    print("=" * 80)
    print("  🤖 تست AI Integration")
    print("=" * 80)
    print()
    
    # تست
    result = get_ai_advice(
        symbol="خگستر",
        category="SAFE_BUY",
        ratio=5.0,
        rsi=25,
        technical_score=70,
        market_change_pct=1.5,
        last_price=10000,
    )
    
    print("  مشاوره AI:")
    for k, v in result.items():
        print(f"     {k}: {v}")
    
    print()
    print("=" * 80)
    print("  ✅ تمام!")
    print("=" * 80)
    print()

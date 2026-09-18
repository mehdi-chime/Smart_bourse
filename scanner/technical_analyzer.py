"""
Project : Smart_Bourse
File    : technical_analyzer.py
Version : 2.1.0
Author  : Mehdi Jalali + Assistant

Description :
    تحلیل تکنیکال با استفاده از IndicatorManager موجود
    - از indicators/rsi.py, macd.py, ... استفاده می‌کند
    - امتیازدهی ترکیبی: جریان پول + تکنیکال
"""

import json
from datetime import datetime
from pathlib import Path
import sys

import algotik_tse as att
import pandas as pd

# اضافه کردن ریشه پروژه به sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from indicators.indicator_manager import IndicatorManager
from models.stock import Stock


# ======================================================================
# تنظیمات
# ======================================================================

DATA_DIR = PROJECT_ROOT / "data"
REAL_FLOW_DIR = DATA_DIR / "real_flow"

WEIGHT_MONEY_FLOW = 0.40
WEIGHT_TECHNICAL = 0.60


# ======================================================================
# تبدیل داده
# ======================================================================

def df_to_stocks(df, symbol):
    """تبدیل DataFrame به لیست Stock"""
    stocks = []

    if "Close" not in df.columns:
        return []

    dates = df.index.tolist()

    for i, (_, row) in enumerate(df.iterrows()):
        s = Stock()
        s.symbol = symbol
        s.close_price = float(row.get("Close", 0) or 0)
        s.open_price = float(row.get("Open", 0) or 0)
        s.high_price = float(row.get("High", 0) or 0)
        s.low_price = float(row.get("Low", 0) or 0)
        s.volume = float(row.get("Volume", 0) or 0)

        if i < len(dates):
            s.trade_date = str(dates[i])
        else:
            s.trade_date = ""

        stocks.append(s)

    return stocks


# ======================================================================
# امتیازدهی
# ======================================================================

def score_rsi(rsi_value):
    """امتیاز RSI"""
    if rsi_value is None or not isinstance(rsi_value, (int, float)):
        return 50
    if rsi_value < 30:
        return 100
    elif rsi_value < 45:
        return 80
    elif rsi_value < 60:
        return 60
    elif rsi_value < 70:
        return 40
    return 20


def score_macd(macd_result):
    """امتیاز MACD"""
    if macd_result is None:
        return 50
    if isinstance(macd_result, dict):
        hist = macd_result.get("histogram") or macd_result.get("macd_signal")
        if hist and hist > 0:
            return 75
        return 35
    return 50


def score_ma(ma_result):
    """امتیاز میانگین متحرک"""
    if ma_result is None:
        return 50
    if isinstance(ma_result, dict):
        signal = ma_result.get("signal") or ma_result.get("trend")
        if signal and "up" in str(signal).lower():
            return 80
        if signal and "down" in str(signal).lower():
            return 30
    return 50


def score_money_flow(ratio):
    """امتیاز جریان پول"""
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


# ======================================================================
# تحلیل یه نماد
# ======================================================================

def analyze_symbol(symbol):
    """تحلیل تکنیکال یه نماد با IndicatorManager"""
    try:
        df = att.get_history(symbol)
    except Exception as e:
        return None

    if df is None or df.empty or len(df) < 30:
        return None

    stocks = df_to_stocks(df, symbol)
    if not stocks:
        return None

    manager = IndicatorManager()
    try:
        indicators = manager.run(stocks)
    except Exception as e:
        return None

    rsi = indicators.get("RSI")
    macd = indicators.get("MACD")
    ma = indicators.get("Moving Average")
    bollinger = indicators.get("Bollinger")
    atr = indicators.get("ATR")

    tech_scores = {
        "rsi": score_rsi(rsi),
        "macd": score_macd(macd),
        "ma": score_ma(ma),
    }
    technical_score = sum(tech_scores.values()) / len(tech_scores)

    return {
        "symbol": symbol,
        "last_price": stocks[-1].close_price,
        "rsi": rsi if isinstance(rsi, (int, float)) else None,
        "macd": macd,
        "ma": ma,
        "bollinger": bollinger,
        "atr": atr,
        "tech_scores": {k: round(v, 1) for k, v in tech_scores.items()},
        "technical_score": round(technical_score, 2),
    }


# ======================================================================
# کلاس اصلی
# ======================================================================

class TechnicalAnalyzer:

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = REAL_FLOW_DIR
        self.data_dir = Path(data_dir)

    def find_latest_json(self):
        if not self.data_dir.exists():
            return None
        files = sorted(self.data_dir.glob("real_flow_*.json"), reverse=True)
        files = [f for f in files if "history" not in str(f)]
        return files[0] if files else None

    def analyze_all(self, json_file=None):
        if json_file is None:
            json_file = self.find_latest_json()

        if json_file is None:
            print("هیچ فایل JSON پیدا نشد")
            return None

        print("خواندن: " + str(json_file))
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        targets = []
        for cat in ["safe_buy", "queue_buy", "safe_sell"]:
            for item in data.get(cat, []):
                symbol = item.get("Symbol") or item.get("symbol")
                if symbol:
                    targets.append({
                        "symbol": symbol,
                        "category": cat.upper(),
                        "ratio": item.get("ratio", 0),
                        "name": item.get("Name", ""),
                        "last": item.get("Last", 0),
                        "value": item.get("Value", 0),
                    })

        print(str(len(targets)) + " نماد برای تحلیل تکنیکال")
        print()

        results = []
        for i, t in enumerate(targets, 1):
            symbol = t["symbol"]
            print("[" + str(i) + "/" + str(len(targets)) + "] " + symbol + " ... ", end="", flush=True)

            tech = analyze_symbol(symbol)
            if tech is None:
                print("رد شد")
                continue

            mf_score = score_money_flow(t["ratio"])
            final_score = (
                WEIGHT_MONEY_FLOW * mf_score
                + WEIGHT_TECHNICAL * tech["technical_score"]
            )

            result = dict(t)
            result.update(tech)
            result["money_flow_score"] = round(mf_score, 2)
            result["final_score"] = round(final_score, 2)
            results.append(result)
            print("OK | تکنیکال: " + str(round(tech["technical_score"], 1)) + " | نهایی: " + str(round(final_score, 1)))

        results.sort(key=lambda x: x["final_score"], reverse=True)

        return {
            "date": data.get("date"),
            "generated_at": datetime.now().isoformat(),
            "results": results,
        }

    def save(self, analysis):
        if not analysis:
            return

        date = analysis.get("date", datetime.now().strftime("%Y-%m-%d"))
        out_file = self.data_dir / ("technical_" + date + ".json")

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)

        print()
        print("ذخیره شد: " + str(out_file))
        return out_file

    def print_top(self, analysis, top_n=15):
        if not analysis:
            return

        results = analysis["results"][:top_n]

        print()
        print("=" * 100)
        print("نمادهای برتر - ترکیب جریان پول + تکنیکال")
        print("=" * 100)
        print("   # | نماد       | دسته       | نسبت    | RSI   | تکنیکال | جریان | نهایی")
        print("   " + "-" * 96)

        for i, r in enumerate(results, 1):
            rsi_val = r.get("rsi") or 0
            print(
                "   " + str(i).ljust(3)
                + " | " + str(r["symbol"])[:10].ljust(10)
                + " | " + str(r["category"])[:10].ljust(10)
                + " | " + str(round(r["ratio"], 2)).rjust(7)
                + " | " + str(round(rsi_val, 1)).rjust(6)
                + " | " + str(round(r["technical_score"], 1)).rjust(7)
                + " | " + str(round(r["money_flow_score"], 0)).rjust(6)
                + " | " + str(round(r["final_score"], 1)).rjust(6)
            )

        print("=" * 100)


# ======================================================================
# اجرا
# ======================================================================

if __name__ == "__main__":
    print("شروع تحلیل تکنیکال")
    print()

    analyzer = TechnicalAnalyzer()
    analysis = analyzer.analyze_all()

    if analysis:
        analyzer.print_top(analysis, top_n=20)
        analyzer.save(analysis)
        print()
        print("تمام!")
    else:
        print()
        print("اول real_flow_filter.py رو اجرا کن")

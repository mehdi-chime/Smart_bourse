"""
Project : Smart_Bourse
File    : scanner/ai_advisor.py
Version : 2.0.0
Description :
    مشاور AI — با cache برای سرعت ۳ برابر
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
        self._history_cache = {}

    def find_latest_json(self):
        if not self.data_dir.exists():
            return None
        files = sorted(self.data_dir.glob("real_flow_*.json"), reverse=True)
        files = [f for f in files if "history" not in str(f)]
        return files[0] if files else None

    def _lookup_price(self, symbol, days_ago):
        """قیمت چند روز پیش — با cache (یه بار درخواست، چند قیمت)"""
        if symbol not in self._history_cache:
            try:
                df = att.get_history(symbol)
                if df is not None and not df.empty and "Close" in df.columns:
                    self._history_cache[symbol] = df["Close"].tolist()
                else:
                    self._history_cache[symbol] = []
            except Exception:
                self._history_cache[symbol] = []

        prices = self._history_cache[symbol]
        if len(prices) <= days_ago:
            return None
        try:
            return float(prices[-1 - days_ago])
        except Exception:
            return None

    def run(self, json_file=None):
        print()
        print("=" * 70)
        print("  Smart_Bourse AI Advisor")
        print("=" * 70)

        print()
        print("چک نتایج سیگنال‌های قبلی ...")
        checked = self.engine.check_outcomes(self._lookup_price)
        print("   " + str(checked) + " نتیجه جدید چک شد")

        self.engine.report()

        if json_file is None:
            json_file = self.find_latest_json()

        if json_file is None:
            print()
            print("هیچ فایل JSON پیدا نشد")
            return

        print()
        print("خواندن سیگنال‌های جدید: " + json_file.name)
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        trade_date = data.get("date")

        print()
        print("ثبت سیگنال‌ها تو حافظه AI ...")

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
        print("  توصیه AI برای هر نماد")
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
                print("      " + advice["advice"])

        print()
        print("=" * 70)
        print("  تمام")
        print("=" * 70)


if __name__ == "__main__":
    advisor = AIAdvisor()
    advisor.run()

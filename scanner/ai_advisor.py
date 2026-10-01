
import sys
import json
from datetime import datetime
from pathlib import Path

import algotik_tse as att

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ai.ai_engine import AIEngine


DATA_DIR = PROJECT_ROOT / "data"
REAL_FLOW_DIR = DATA_DIR / "real_flow"
ID_MAP_FILE = DATA_DIR / "symbol_id_map.json"


def normalize(s):
    if not s:
        return s
    return (str(s)
            .replace("\u0643", "\u06a9")
            .replace("\u064a", "\u06cc")
            .replace("\u0649", "\u06cc")
            .replace("\u0629", "\u0647")
            .replace("\u0640", "")
            .strip())


def build_id_map():
    """ساخت نقشه name -> instrument_id"""
    if ID_MAP_FILE.exists():
        try:
            with open(ID_MAP_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data:
                return data
        except Exception:
            pass

    print("Building ID map (first time)...")
    syms = att.get_symbols()

    id_map = {}
    for idx, row in syms.iterrows():
        symbol = str(idx)
        inst_id = row.get("instrument_id")
        if inst_id:
            id_map[normalize(symbol)] = int(inst_id)
            id_map[symbol] = int(inst_id)

    ID_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ID_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(id_map, f, ensure_ascii=False, indent=2)

    print("   saved " + str(len(id_map)) + " entries")
    return id_map


class AIAdvisor:

    def __init__(self):
        self.engine = AIEngine()
        self.data_dir = REAL_FLOW_DIR
        self._history_cache = {}
        self.id_map = build_id_map()

    def find_latest_json(self):
        if not self.data_dir.exists():
            return None
        files = sorted(self.data_dir.glob("real_flow_*.json"), reverse=True)
        files = [f for f in files if "history" not in str(f)]
        return files[0] if files else None

    def _lookup_price(self, symbol, days_ago):
        """قیمت با ID مستقیم"""
        if symbol in self._history_cache:
            prices = self._history_cache[symbol]
        else:
            prices = self._fetch_history(symbol)
            self._history_cache[symbol] = prices

        if not prices or len(prices) <= days_ago:
            return None
        try:
            return float(prices[-1 - days_ago])
        except Exception:
            return None

    def _fetch_history(self, symbol):
        """تلاش با ID و بعد با اسم"""
        inst_id = self.id_map.get(symbol) or self.id_map.get(normalize(symbol))
        if inst_id:
            try:
                df = att.get_history(str(inst_id))
                if df is not None and not df.empty and "Close" in df.columns:
                    return df["Close"].tolist()
            except Exception:
                pass

        try:
            df = att.get_history(symbol)
            if df is not None and not df.empty and "Close" in df.columns:
                return df["Close"].tolist()
        except Exception:
            pass

        norm = normalize(symbol)
        if norm != symbol:
            try:
                df = att.get_history(norm)
                if df is not None and not df.empty and "Close" in df.columns:
                    return df["Close"].tolist()
            except Exception:
                pass

        return []

    def run(self, json_file=None):
        print()
        print("=" * 70)
        print("  Smart_Bourse AI Advisor")
        print("=" * 70)

        print()
        print("Symbol map: " + str(len(self.id_map)) + " entries")

        print()
        print("Checking previous signals ...")
        checked = self.engine.check_outcomes(self._lookup_price)
        print("   " + str(checked) + " new results checked")

        self.engine.report()

        if json_file is None:
            json_file = self.find_latest_json()

        if json_file is None:
            print()
            print("No JSON file found")
            return

        print()
        print("Reading new signals: " + json_file.name)
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        trade_date = data.get("date")

        print()
        print("Saving signals to AI memory ...")
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

        print("   done")

        print()
        print("=" * 70)
        print("  AI Advice")
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
            print("  " + cat.upper() + " - " + str(len(items)) + " symbols:")
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
                print("   " + symbol.ljust(10) + " | ratio: " + str(round(advice["ratio"], 2)).rjust(7) + " | score: " + str(advice["final_score"]).rjust(5) + " | conf: " + str(advice["confidence"]))
                print("      " + advice["advice"])

        print()
        print("=" * 70)
        print("  done")
        print("=" * 70)


if __name__ == "__main__":
    advisor = AIAdvisor()
    advisor.run()

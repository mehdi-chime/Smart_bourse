# strategy_50m.py
# استراتژی ۵۰۰ میلیون ریال
# اجرا: python strategy_50m.py

import os
import sys
import json
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np

# ✅ سرمایه به ریال
CAPITAL = 500_000_000  # 500 میلیون ریال = 50 میلیون تومان


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


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


def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    p = np.array(prices, dtype=float)
    deltas = np.diff(p)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    ag = gains[-period:].mean()
    al = losses[-period:].mean()
    if al == 0 and ag > 0:
        return 100
    if al == 0 and ag == 0:
        return 50
    rs = ag / al
    return round(100 - (100 / (1 + rs)), 1)


def calc_atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        trs.append(tr)
    return float(np.mean(trs[-period:]))


def get_history_safe(symbol):
    for alias in [symbol, normalize(symbol)]:
        try:
            df = att.get_history(alias)
            if df is not None and not df.empty and "Close" in df.columns:
                if len(df) >= 15:
                    return df
        except:
            continue
    return None


def analyze_stock(row, layer):
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            return None

        last = float(row.get("Last") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0 or min_a <= 0 or max_a <= 0 or eps <= 0:
            return None

        pe = last / eps

        if layer == "safe":
            if pe > 10:
                return None
            max_rsi = 30
        elif layer == "medium":
            if pe > 15:
                return None
            max_rsi = 40
        elif layer == "aggressive":
            if pe > 15:
                return None
            max_rsi = 20

        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        if vol_buy + vol_sell < 500_000:
            return None

        hist = get_history_safe(symbol)
        if hist is None:
            return None

        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        rsi = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)

        if rsi is None or atr_val is None:
            return None
        if rsi > max_rsi:
            return None

        atr_pct = (atr_val / last * 100) if last > 0 else 0
        if atr_pct < 2.5:
            return None

        profit = (max_a / min_a - 1) * 100 - 1.25
        if profit < 3.5:
            return None

        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        score = 0

        if rsi < 15:
            score += 30
        elif rsi < 20:
            score += 25
        elif rsi < 25:
            score += 20
        elif rsi < 30:
            score += 15
        elif rsi < 40:
            score += 10

        if pe < 3:
            score += 25
        elif pe < 5:
            score += 20
        elif pe < 8:
            score += 15
        elif pe < 12:
            score += 10
        elif pe < 15:
            score += 5

        if vol_sell_n > 0:
            ratio = vol_buy_n / vol_sell_n
            if ratio > 3:
                score += 25
            elif ratio > 1.5:
                score += 20
            elif ratio > 1:
                score += 10
        elif vol_buy_n > 0:
            score += 15

        if atr_pct > 4.5:
            score += 20
        elif atr_pct > 4:
            score += 15
        elif atr_pct > 3:
            score += 10
        elif atr_pct > 2.5:
            score += 5

        return {
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "min_a": min_a,
            "max_a": max_a,
            "eps": eps,
            "pe": round(pe, 2),
            "rsi": rsi,
            "atr_pct": round(atr_pct, 2),
            "score": score,
            "profit": profit,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": round(min_a * 0.98),
        }
    except:
        return None


def main():
    print()
    print("=" * 110)
    print(f"  STRATEGY 50M - استراتژی ۵۰ میلیون تومان")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 110)
    print()

    print(f"  Capital: {CAPITAL:,} rials")
    print(f"           = {CAPITAL//10:,} toman (50M toman)")
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("  ERR")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    print(f"  OK: {len(df)} sahm")
    print()

    layers = {
        "safe": {"name": "امن", "pct": 0.4},
        "medium": {"name": "متوسط", "pct": 0.4},
        "aggressive": {"name": "تهاجمی", "pct": 0.2},
    }

    all_results = {}

    for layer_key, layer_info in layers.items():
        print(f"  Tahlil laye {layer_info['name']} ({layer_info['pct']*100:.0f}%)...")
        results = []
        for _, row in df.iterrows():
            r = analyze_stock(row, layer_key)
            if r:
                results.append(r)

        results.sort(key=lambda x: -x["score"])
        all_results[layer_key] = results[:3]
        print(f"     {len(results)} candidate")

    print()

    # نمایش
    for layer_key, top_stocks in all_results.items():
        layer_info = layers[layer_key]
        capital_layer = CAPITAL * layer_info["pct"]
        per_stock = capital_layer / len(top_stocks) if top_stocks else 0

        print("=" * 110)
        print(f"  LAYE {layer_info['name']} ({layer_info['pct']*100:.0f}%)")
        print(f"  Sarmaye: {capital_layer/10:,.0f} toman")
        print(f"  Har sahm: {per_stock/10:,.0f} toman")
        print("=" * 110)
        print()

        if not top_stocks:
            print("  Hich sahm")
            print()
            continue

        print(f"  {'#':<3} | {'Namad':<10} | {'Gheymat':>10} | {'PE':>5} | {'RSI':>5} | {'ATR':>5} | {'Emtiaz':>6} | {'Sood':>6} | {'Tedad':>8} | {'Sarmaye':>10}")
        print("  " + "-" * 120)

        for i, s in enumerate(top_stocks, 1):
            qty = int(per_stock / s['last']) if s['last'] > 0 else 0
            actual = qty * s['last']

            print(
                f"  {i:<3} | "
                f"{s['symbol'][:10]:<10} | "
                f"{int(s['last']):>10,} | "
                f"{s['pe']:>5.1f} | "
                f"{s['rsi']:>5} | "
                f"{s['atr_pct']:>4.1f}% | "
                f"{s['score']:>4}/100 | "
                f"{s['profit']:>5.2f}% | "
                f"{qty:>8,} | "
                f"{actual/10:>8,.0f}T"
            )
        print()

    output = PROJECT_ROOT / "data" / "hunter" / f"strategy_50m_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "capital": CAPITAL,
            "layers": all_results,
        }, f, ensure_ascii=False, indent=2)

    print("=" * 110)
    print(f"  Save: {output}")
    print("=" * 110)
    print()


if __name__ == "__main__":
    main()

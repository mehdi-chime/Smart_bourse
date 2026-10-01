# smart_scanner_v8.py
# اسکنر v8 - فقط P/E < 15
# اجرا: python smart_scanner_v8.py

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

# ═══════════════════════════════════════════════════════════
# تنظیمات - سخت‌گیرانه!
# ═══════════════════════════════════════════════════════════
MIN_RSI = 10
MAX_RSI = 50
MIN_ATR = 2.5
MIN_VOLUME = 500_000
MIN_PROFIT = 3.5
MAX_PE = 15              # ← فیلتر سخت!
MAX_RESULTS = 5


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


def send_eitaa(text):
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
        import requests
        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=15)
        return r.status_code == 200
    except:
        return False


def analyze_full(row):
    try:
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            return None

        last = float(row.get("Last") or row.get("Close") or 0)
        yesterday = float(row.get("Yesterday") or 0)
        min_a = float(row.get("MinAllowed") or 0)
        max_a = float(row.get("MaxAllowed") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0 or min_a <= 0 or max_a <= 0:
            return None

        # ✅ P/E فیلتر سخت
        if eps <= 0:
            return None
        pe = last / eps
        if pe > MAX_PE or pe < 0:
            return None

        vol_buy = float(row.get("Vol_buy_retail") or 0)
        vol_sell = float(row.get("Vol_sell_retail") or 0)
        vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

        total_vol = vol_buy + vol_sell
        if total_vol < MIN_VOLUME:
            return None

        ask_v1 = float(row.get("AskVolume1") or 0)
        bid_v1 = float(row.get("BidVolume1") or 0)
        if bid_v1 == 0 and ask_v1 > 0:
            return None

        hist = get_history_safe(symbol)
        rsi = None
        atr_pct = None

        if hist is not None:
            closes = hist["Close"].tolist()
            highs = hist["High"].tolist() if "High" in hist.columns else closes
            lows = hist["Low"].tolist() if "Low" in hist.columns else closes

            rsi = calc_rsi(closes, 14)
            atr_val = calc_atr(highs, lows, closes, 14)
            if atr_val and last > 0:
                atr_pct = (atr_val / last * 100)

        if rsi is None or atr_pct is None:
            return None

        if not (MIN_RSI <= rsi <= MAX_RSI):
            return None

        if atr_pct < MIN_ATR:
            return None

        profit = (max_a / min_a - 1) * 100 - 1.25
        if profit < MIN_PROFIT:
            return None

        distance_from_min = (last - min_a) / min_a * 100
        if distance_from_min > 10:
            return None

        score = 0
        reasons = []

        # P/E (25 - مهم‌ترین!)
        if pe < 5:
            score += 25
            reasons.append(f"P/E={pe:.1f} kheili khoob")
        elif pe < 8:
            score += 20
            reasons.append(f"P/E={pe:.1f} khoob")
        elif pe < 12:
            score += 15
            reasons.append(f"P/E={pe:.1f} monaseb")
        elif pe < 15:
            score += 10
            reasons.append(f"P/E={pe:.1f} ghabele ghobool")

        # RSI (25)
        if rsi < 20:
            score += 25
            reasons.append(f"RSI={rsi} kheili paeen")
        elif rsi < 30:
            score += 20
            reasons.append(f"RSI={rsi} paeen")
        elif rsi < 40:
            score += 12
            reasons.append(f"RSI={rsi} monaseb")

        # ATR (20)
        if atr_pct > 4:
            score += 20
            reasons.append(f"ATR={atr_pct:.1f}% bala")
        elif atr_pct > 3:
            score += 15
            reasons.append(f"ATR={atr_pct:.1f}% khob")

        # حقوقی (20)
        if vol_sell_n > 0:
            ratio_n = vol_buy_n / vol_sell_n
            if ratio_n > 3:
                score += 20
                reasons.append(f"Hoqoqi={ratio_n:.1f}x ghavi")
            elif ratio_n > 1.5:
                score += 15
                reasons.append(f"Hoqoqi={ratio_n:.1f}x kharidar")
            elif ratio_n > 1:
                score += 8
        elif vol_buy_n > 0:
            score += 15
            reasons.append("Hoqoqi faghat kharidar")

        # حقیقی (10)
        if vol_sell > 0:
            ratio_r = vol_buy / vol_sell
            if ratio_r > 1.5:
                score += 10
                reasons.append(f"Haghighi={ratio_r:.1f}x kharidar")

        return {
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "yesterday": yesterday,
            "min_a": min_a,
            "max_a": max_a,
            "change": change,
            "eps": eps,
            "pe": round(pe, 2),
            "rsi": rsi,
            "atr_pct": atr_pct,
            "vol_buy": vol_buy,
            "vol_sell": vol_sell,
            "vol_buy_n": vol_buy_n,
            "vol_sell_n": vol_sell_n,
            "score": score,
            "profit": profit,
            "distance_from_min": distance_from_min,
            "buy_target": min_a,
            "sell_target": max_a,
            "stop_loss": round(min_a * 0.98),
            "reasons": reasons,
        }
    except Exception:
        return None


def build_message(signals, market_pct, positive, negative):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    msg = f"Smart_Bourse v8\n"
    msg += f"Date: {date_str} | Time: {time_str}\n"
    msg += "========================\n"
    msg += f"Bazar: {market_pct:.1f}% mosbat\n"
    msg += f"   Green: {positive} | Red: {negative}\n"
    msg += f"Filter: P/E < 15\n\n"

    if not signals:
        msg += "Hich signal jadidi nist\n"
        return msg

    msg += f"{len(signals)} sahm pishnahadi:\n"
    msg += "========================\n\n"

    for i, s in enumerate(signals, 1):
        msg += f"{i}. {s['symbol']}\n"
        msg += f"   {s['name'][:25]}\n"
        msg += f"   --------------------\n"
        msg += f"   Gheymat: {int(s['last']):,}\n"
        msg += f"   Taghir:  {s['change']:+.2f}%\n"
        msg += f"   P/E:     {s['pe']} ✅\n"
        msg += f"   EPS:     {int(s['eps']):,}\n"
        msg += f"   RSI:     {s['rsi']}\n"
        msg += f"   ATR:     {s['atr_pct']:.1f}%\n"
        msg += f"   --------------------\n"
        msg += f"   KHARID:  {int(s['buy_target']):,}\n"
        msg += f"   FOROOSH: {int(s['sell_target']):,}\n"
        msg += f"   HAD-ZARAR: {int(s['stop_loss']):,}\n"
        msg += f"   SOOD:    {s['profit']:.2f}%\n"
        msg += f"   EMTIAZ:  {s['score']}/100\n"
        msg += f"   --------------------\n"
        msg += f"   Dalayel:\n"
        for r in s['reasons'][:4]:
            msg += f"      - {r}\n"
        msg += "\n"

    msg += "========================\n"
    msg += "Estrategi:\n"
    msg += "   1. Kharid rooye kaf\n"
    msg += "   2. Foroosh rooye saghf\n"
    msg += "   3. Had-zarar -2%\n"
    msg += "   4. P/E < 15\n"
    msg += "========================\n"

    return msg


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print(f"  Smart_Bourse Scanner v8 (فقط P/E < 15)")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    safe_print("  Daryaft dade...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ERR")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    safe_print(f"  OK: {len(df)} sahm")
    safe_print("")

    positive = 0
    negative = 0
    total = 0

    for _, row in df.iterrows():
        try:
            change = float(row.get("ChangePct") or 0)
            total += 1
            if change > 0:
                positive += 1
            elif change < 0:
                negative += 1
        except:
            continue

    market_pct = positive / total * 100 if total > 0 else 0
    safe_print(f"  Bazar: {market_pct:.1f}% mosbat ({positive}G/{negative}R)")
    safe_print("")

    safe_print("  Tahlil kamel (P/E < 15 + RSI + ATR + Hoqoqi)...")
    safe_print("")

    results = []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        if i % 50 == 0:
            safe_print(f"     {i}/{len(df)}...")

        r = analyze_full(row)
        if r:
            results.append(r)

    safe_print(f"  OK: {len(results)} candidate")
    safe_print("")

    results.sort(key=lambda x: -x["score"])
    top = results[:MAX_RESULTS]

    safe_print("=" * 100)
    safe_print(f"  Behtarin {len(top)} sahm (P/E < 15)")
    safe_print("=" * 100)
    safe_print("")

    safe_print(f"  {'#':<3} | {'Namad':<10} | {'Gheymat':>10} | {'PE':>5} | {'EPS':>10} | {'RSI':>5} | {'ATR':>5} | {'Emtiaz':>6} | {'Sood':>6}")
    safe_print("  " + "-" * 110)

    for i, s in enumerate(top, 1):
        safe_print(
            f"  {i:<3} | "
            f"{s['symbol'][:10]:<10} | "
            f"{int(s['last']):>10,} | "
            f"{s['pe']:>5.1f} | "
            f"{int(s['eps']):>10,} | "
            f"{s['rsi']:>5} | "
            f"{s['atr_pct']:>4.1f}% | "
            f"{s['score']:>4}/100 | "
            f"{s['profit']:>5.2f}%"
        )

    safe_print("")

    # ارسال
    if top:
        msg = build_message(top, market_pct, positive, negative)
        if send_eitaa(msg):
            safe_print("  OK: Eita ersal shod")
        else:
            safe_print("  ERR: Eita")
    else:
        safe_print("  No signal")

    safe_print("")

    output = PROJECT_ROOT / "data" / "hunter" / f"smart_v8_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "market_pct": market_pct,
            "top": top,
            "all": results,
        }, f, ensure_ascii=False, indent=2)

    safe_print(f"  Save: {output}")
    safe_print("")
    safe_print("=" * 100)
    safe_print("")


if __name__ == "__main__":
    main()

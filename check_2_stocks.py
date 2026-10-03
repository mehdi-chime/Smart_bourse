# check_2_stocks.py
# بررسی کامل ۲ سهم: صندوق دواتکس + آسیاتک
# اجرا: python check_2_stocks.py

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
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np

# ═══════════════════════════════════════════════════════════
# تنظیمات — با INS Code (دقیق‌ترین روش)
# ═══════════════════════════════════════════════════════════

STOCKS = [
    {
        "name": "دواتکس (صندوق)",
        "aliases": ["دواس", "دواتکس", "دواتكس", "داتکس", "داتكس"],
        "ins_code": "58108537439201620",
    },
    {
        "name": "آسیاتک",
        "aliases": ["اسياتك", "آسیاتک", "آسياتك", "هاتف"],
        "ins_code": "14079693677610396",
    },
]


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
            .replace(" ", "")
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


def get_ai_advice_safe(symbol, ratio, rsi, tech_score, last_price):
    try:
        from ai_integration import get_ai_advice
        return get_ai_advice(
            symbol=symbol,
            category="SAFE_BUY",
            ratio=ratio,
            rsi=rsi,
            technical_score=tech_score,
            last_price=last_price,
        )
    except Exception as e:
        return {
            "final_score": 50,
            "advice": f"AI error: {e}",
            "confidence": 0.5,
            "mode": "error",
        }


def find_stock(stock_info, df_live):
    """پیدا کردن سهم با INS Code یا alias"""
    found = None

    for _, row in df_live.iterrows():
        live_ins = str(row.get("InsCode") or row.get("insCode") or "")
        live_symbol = str(row.get("Symbol", ""))

        # چک INS Code (دقیق‌ترین)
        if stock_info.get("ins_code") and live_ins == stock_info["ins_code"]:
            return row

        # چک alias
        for alias in stock_info["aliases"]:
            if normalize(alias) == normalize(live_symbol):
                return row

    return None


def analyze_stock(stock_info, df_live):
    result = {
        "name": stock_info["name"],
        "found": False,
        "error": None,
        "ins_code": stock_info.get("ins_code", ""),
    }

    found = find_stock(stock_info, df_live)

    if found is None:
        result["error"] = "Symbol not found"
        return result

    result["found"] = True
    result["symbol"] = str(found.get("Symbol", ""))
    result["full_name"] = str(found.get("Name", ""))
    result["ins_code_found"] = str(found.get("InsCode") or found.get("insCode") or "")

    # قیمت‌ها
    last = float(found.get("Last") or found.get("Close") or 0)
    yesterday = float(found.get("Yesterday") or 0)
    min_a = float(found.get("MinAllowed") or 0)
    max_a = float(found.get("MaxAllowed") or 0)
    change = float(found.get("ChangePct") or 0)
    eps = float(found.get("EPS") or 0)

    result["last"] = last
    result["yesterday"] = yesterday
    result["min_a"] = min_a
    result["max_a"] = max_a
    result["change"] = change
    result["eps"] = eps

    if eps > 0:
        result["pe"] = round(last / eps, 2)
    else:
        result["pe"] = None

    # سفارشات
    vol_buy = float(found.get("Vol_buy_retail") or 0)
    vol_sell = float(found.get("Vol_sell_retail") or 0)
    vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
    vol_sell_n = float(found.get("Vol_sell_institutional") or 0)

    result["vol_buy"] = vol_buy
    result["vol_sell"] = vol_sell
    result["vol_buy_n"] = vol_buy_n
    result["vol_sell_n"] = vol_sell_n

    # صف
    bid_v1 = float(found.get("BidVolume1") or 0)
    ask_v1 = float(found.get("AskVolume1") or 0)
    result["has_buy_queue"] = (ask_v1 == 0 and bid_v1 > 0)
    result["has_sell_queue"] = (bid_v1 == 0 and ask_v1 > 0)

    if vol_sell > 0:
        result["ratio"] = round(vol_buy / vol_sell, 2)
    else:
        result["ratio"] = 1.0

    # RSI + ATR
    hist = get_history_safe(result["symbol"])
    if hist is not None:
        closes = hist["Close"].tolist()
        highs = hist["High"].tolist() if "High" in hist.columns else closes
        lows = hist["Low"].tolist() if "Low" in hist.columns else closes

        result["rsi"] = calc_rsi(closes, 14)
        atr_val = calc_atr(highs, lows, closes, 14)
        if atr_val and last > 0:
            result["atr_pct"] = round((atr_val / last * 100), 2)

    # AI
    ai_result = get_ai_advice_safe(
        symbol=result["symbol"],
        ratio=result.get("ratio", 1.0),
        rsi=result.get("rsi"),
        tech_score=50,
        last_price=last,
    )

    result["ai_score"] = ai_result.get("final_score", 50)
    result["ai_advice"] = ai_result.get("advice", "")
    result["ai_confidence"] = ai_result.get("confidence", 0.5)
    result["ai_mode"] = ai_result.get("mode", "")

    # تصمیم
    if result.get("has_sell_queue"):
        result["decision"] = "RED - Sell Queue"
    elif result.get("has_buy_queue"):
        result["decision"] = "YELLOW - Buy Queue"
    elif result.get("ai_score", 0) >= 70:
        result["decision"] = "GREEN - Buy"
    elif result.get("ai_score", 0) >= 55:
        result["decision"] = "YELLOW - Caution"
    elif result.get("ai_score", 0) >= 40:
        result["decision"] = "ORANGE - Wait"
    else:
        result["decision"] = "RED - Don't buy"

    if min_a > 0 and max_a > 0:
        result["buy_target"] = min_a
        result["sell_target"] = max_a
        result["stop_loss"] = round(min_a * 0.98)
        result["profit"] = round((max_a / min_a - 1) * 100 - 1.25, 2)

    return result


def print_stock(r):
    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  {r['name']} ({r.get('symbol', '?')})")
    safe_print("=" * 80)
    safe_print("")

    if not r.get("found"):
        safe_print(f"  ERROR: {r.get('error', 'not found')}")
        safe_print(f"  INS Code: {r.get('ins_code', '')}")
        return

    safe_print(f"  Name: {r.get('full_name', '')}")
    if r.get("ins_code_found"):
        safe_print(f"  InsCode: {r['ins_code_found']}")
    safe_print("")

    safe_print(f"  PRICE:")
    safe_print(f"     Last:        {int(r['last']):>12,}")
    safe_print(f"     Yesterday:   {int(r['yesterday']):>12,}")
    safe_print(f"     Change:      {r['change']:>11.2f}%")
    safe_print(f"     Min:         {int(r['min_a']):>12,}")
    safe_print(f"     Max:         {int(r['max_a']):>12,}")
    safe_print("")

    safe_print(f"  FUNDAMENTAL:")
    if r.get("pe"):
        safe_print(f"     P/E:         {r['pe']:>12}")
    safe_print(f"     EPS:         {int(r['eps']):>12,}")
    safe_print("")

    safe_print(f"  TECHNICAL:")
    safe_print(f"     RSI:         {r.get('rsi', '?'):>12}")
    safe_print(f"     ATR:         {r.get('atr_pct', '?'):>11}%")
    safe_print("")

    safe_print(f"  ORDERS:")
    safe_print(f"     Retail Buy:  {int(r['vol_buy']):>12,}")
    safe_print(f"     Retail Sell: {int(r['vol_sell']):>12,}")
    safe_print(f"     Inst Buy:    {int(r['vol_buy_n']):>12,}")
    safe_print(f"     Inst Sell:   {int(r['vol_sell_n']):>12,}")
    safe_print(f"     Ratio:       {r.get('ratio', 1):>12}")
    safe_print("")

    if r.get("has_buy_queue"):
        safe_print(f"  QUEUE: BUY")
    elif r.get("has_sell_queue"):
        safe_print(f"  QUEUE: SELL")
    safe_print("")

    safe_print(f"  AI Analysis:")
    safe_print(f"     Score:       {r.get('ai_score', 0):>12}")
    safe_print(f"     Confidence:  {r.get('ai_confidence', 0):>12}")
    safe_print(f"     Mode:        {r.get('ai_mode', ''):>12}")
    safe_print(f"     Advice:      {r.get('ai_advice', ''):>12}")
    safe_print("")

    safe_print(f"  DECISION: {r.get('decision', '?')}")
    safe_print("")

    if r.get("buy_target"):
        safe_print(f"  STRATEGY:")
        safe_print(f"     Buy:         {int(r['buy_target']):>12,}")
        safe_print(f"     Sell:        {int(r['sell_target']):>12,}")
        safe_print(f"     Stop Loss:   {int(r['stop_loss']):>12,}")
        safe_print(f"     Profit:      {r['profit']:>11.2f}%")
        safe_print("")


def build_eitaa_message(results):
    msg = f"Check 2 Stocks\n"
    msg += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg += "--------------------\n\n"

    for r in results:
        if not r.get("found"):
            msg += f"{r['name']}: NOT FOUND\n\n"
            continue

        msg += f"{r['name']} ({r.get('symbol', '')})\n"
        msg += f"Price: {int(r['last']):,} ({r['change']:+.2f}%)\n"

        if r.get("pe"):
            msg += f"P/E: {r['pe']}\n"
        if r.get("rsi"):
            msg += f"RSI: {r['rsi']}\n"
        if r.get("atr_pct"):
            msg += f"ATR: {r['atr_pct']}%\n"

        msg += f"AI Score: {r.get('ai_score', 0)}\n"
        msg += f"Decision: {r.get('decision', '?')}\n"
        msg += "--------------------\n\n"

    return msg


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  Check 2 Stocks - Devatox (ETF) + Asiatech")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 80)
    safe_print("")

    safe_print("  Getting live data...")
    df_live = att.get_live_market()

    if df_live is None or df_live.empty:
        safe_print("  ERROR: no data")
        return

    safe_print(f"     {len(df_live)} stocks")
    safe_print("")

    results = []
    for stock in STOCKS:
        safe_print(f"  Analyzing {stock['name']}...")
        r = analyze_stock(stock, df_live)
        results.append(r)

        if r.get("found"):
            safe_print(f"     FOUND: {r.get('symbol', '')}")
        else:
            safe_print(f"     NOT FOUND")
    safe_print("")

    for r in results:
        print_stock(r)

    output = PROJECT_ROOT / "reports" / f"check_2_stocks_{datetime.now().strftime('%Y-%m-%d')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, "w", encoding="utf-8") as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stocks": results,
        }, f, ensure_ascii=False, indent=2)

    safe_print("")
    safe_print("=" * 80)
    safe_print(f"  JSON: {output}")
    safe_print("=" * 80)

    safe_print("")
    safe_print("  Sending to Eitaa...")
    msg = build_eitaa_message(results)
    if send_eitaa(msg):
        safe_print("     SENT")
    else:
        safe_print("     ERROR")
    safe_print("")


if __name__ == "__main__":
    main()

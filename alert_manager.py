# alert_manager.py
# هشدار خودکار پرتفوی
# اجرا: python alert_manager.py

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

PORTFOLIO_FILE = PROJECT_ROOT / "data" / "my_portfolio.json"


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


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  🚨 هشدار خودکار پرتفوی")
    safe_print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 100)
    safe_print("")

    # بارگذاری
    if not PORTFOLIO_FILE.exists():
        safe_print("  ❌ پرتفوی نیست!")
        return

    portfolio = json.loads(PORTFOLIO_FILE.read_text(encoding="utf-8"))

    # فیلتر: فقط سهم‌های معتبر
    portfolio = [s for s in portfolio if s.get("buy_price", 0) > 0 and s.get("quantity", 0) > 0]

    safe_print(f"  📊 {len(portfolio)} سهم معتبر")
    safe_print("")

    # دریافت
    safe_print("  📡 دریافت داده...")
    df = att.get_live_market()

    if df is None or df.empty:
        safe_print("  ❌ خطا")
        return

    safe_print("")

    # بررسی هر سهم
    alerts = []
    warnings = []
    watch = []

    for pos in portfolio:
        symbol = pos["symbol"]
        buy_price = pos["buy_price"]
        qty = pos["quantity"]

        # پیدا کردن
        found = None
        for _, row in df.iterrows():
            live_symbol = str(row.get("Symbol", ""))
            if normalize(symbol) == normalize(live_symbol):
                found = row
                break

        if found is None:
            continue

        last = float(found.get("Last") or found.get("Close") or 0)
        change = float(found.get("ChangePct") or 0)

        # سود/ضرر
        profit_pct = (last - buy_price) / buy_price * 100
        profit_toman = (last - buy_price) * qty

        # RSI
        hist = get_history_safe(symbol)
        rsi = None
        if hist is not None:
            closes = hist["Close"].tolist()
            rsi = calc_rsi(closes, 14)

        # صف
        bid_v1 = float(found.get("BidVolume1") or 0)
        ask_v1 = float(found.get("AskVolume1") or 0)
        has_buy_queue = (ask_v1 == 0 and bid_v1 > 0)
        has_sell_queue = (bid_v1 == 0 and ask_v1 > 0)

        # تحلیل
        # 🔴 هشدار: حدضرر
        if profit_pct <= -5:
            alerts.append({
                "symbol": symbol,
                "type": "حدضرر",
                "profit_pct": profit_pct,
                "profit_toman": profit_toman,
                "reason": f"ضرر {profit_pct:.1f}%",
            })
        # 🟢 هشدار: سود خوب
        elif profit_pct >= 10:
            alerts.append({
                "symbol": symbol,
                "type": "سود خوب",
                "profit_pct": profit_pct,
                "profit_toman": profit_toman,
                "reason": f"سود {profit_pct:.1f}%",
            })
        # 🟠 هشدار: RSI اشباع
        elif rsi and rsi > 75:
            warnings.append({
                "symbol": symbol,
                "type": "RSI اشباع",
                "profit_pct": profit_pct,
                "rsi": rsi,
            })
        # 🔴 هشدار: صف فروش
        elif has_sell_queue:
            warnings.append({
                "symbol": symbol,
                "type": "صف فروش",
                "profit_pct": profit_pct,
            })
        # 🟡 مراقب
        elif profit_pct <= -3:
            watch.append({
                "symbol": symbol,
                "profit_pct": profit_pct,
                "reason": f"ضرر {profit_pct:.1f}%",
            })

        # نمایش
        emoji = "🟢" if profit_pct > 0 else "🔴"
        rsi_str = f"{rsi}" if rsi else "?"

        safe_print(f"  {symbol:15} | {profit_pct:>+6.2f}% | RSI: {rsi_str:>5} | {emoji}")

        if has_sell_queue:
            safe_print(f"     🔴 صف فروش!")
        elif has_buy_queue:
            safe_print(f"     🟢 صف خرید")

    safe_print("")

    # ارسال هشدارها
    if alerts:
        safe_print("=" * 100)
        safe_print("  🚨 هشدارها!")
        safe_print("=" * 100)
        safe_print("")

        msg = "🚨 هشدار پرتفوی\n\n"

        for a in alerts:
            safe_print(f"  {a['symbol']}: {a['type']}")
            safe_print(f"     {a['reason']}")
            safe_print(f"     سود: {a['profit_toman']:+,} تومان")
            safe_print("")

            msg += f"{a['symbol']}: {a['type']}\n"
            msg += f"   {a['reason']}\n"
            msg += f"   سود: {a['profit_toman']:+,}\n\n"

        if send_eitaa(msg):
            safe_print("  ✅ ارسال به ایتا")
        safe_print("")

    if warnings:
        safe_print("  ⚠️ هشدارهای مراقبت:")
        for w in warnings:
            safe_print(f"     {w['symbol']}: {w['type']}")
        safe_print("")

    if watch:
        safe_print("  🟡 مراقب:")
        for w in watch:
            safe_print(f"     {w['symbol']}: {w['reason']}")
        safe_print("")

    if not alerts and not warnings and not watch:
        safe_print("  ✅ همه چیز خوبه!")
        safe_print("")

    safe_print("=" * 100)


if __name__ == "__main__":
    main()

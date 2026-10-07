# school_mode_v10.py
# Smart_Bourse v10 - School Mode داینامیک
# اجرا: python school_mode_v10.py

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, time as dtime

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

LOG_FILE = PROJECT_ROOT / "logs" / "school_v10.log"
SENT_FILE = PROJECT_ROOT / "data" / "sent_v10.json"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ساعت‌ها
MARKET_START = dtime(8, 45)
MARKET_END = dtime(12, 30)

# فاصله‌ها
CHECK_INTERVAL = 300      # هر 5 دقیقه
FULL_SCAN_INTERVAL = 1800 # هر 30 دقیقه
AI_CHECK_INTERVAL = 600   # هر 10 دقیقه AI


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    try:
        print(line)
    except UnicodeEncodeError:
        print(line.encode('ascii', errors='ignore').decode('ascii'))
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


def send_eitaa(text):
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
        import requests
        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=15)
        if r.status_code == 200:
            log("OK: Eitaa ersal")
            return True
        log(f"Eitaa ERR: {r.status_code}")
        return False
    except Exception as e:
        log(f"Eitaa EXC: {e}")
        return False


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


def analyze_market():
    """تحلیل وضعیت بازار"""
    try:
        df = att.get_live_market()
        if df is None or df.empty:
            return None

        if "InstrumentType" in df.columns:
            df = df[df["InstrumentType"] == 300]

        # آمار
        positive = 0
        negative = 0
        total = 0
        total_volume = 0

        for _, row in df.iterrows():
            try:
                change = float(row.get("ChangePct") or 0)
                volume = float(row.get("Volume") or 0)
                total += 1
                total_volume += volume

                if change > 0:
                    positive += 1
                elif change < 0:
                    negative += 1
            except:
                continue

        market_pct = positive / total * 100 if total > 0 else 0
        avg_volume = total_volume / total if total > 0 else 0

        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "market_pct": round(market_pct, 1),
            "avg_volume": int(avg_volume),
            "df": df,
        }
    except Exception as e:
        log(f"Market error: {e}")
        return None


def get_dynamic_rsi_range(market):
    """تعیین بازه RSI داینامیک"""
    if not market:
        return 22, 28, "معمولی"

    market_pct = market["market_pct"]

    # بازار خیلی داغ
    if market_pct > 70:
        return 28, 38, "خیلی داغ"
    # بازار داغ
    elif market_pct > 55:
        return 28, 40, "داغ"
    # بازار معمولی
    elif market_pct > 45:
        return 25, 35, "معمولی"
    # بازار سرد
    elif market_pct > 30:
        return 22, 30, "سرد"
    # بازار خیلی سرد
    else:
        return 18, 28, "خیلی سرد"


def scan_stocks(market):
    """اسکن سهم‌ها با بازه داینامیک"""
    if not market:
        return []

    df = market["df"]
    MIN_RSI, MAX_RSI, state = get_dynamic_rsi_range(market)

    log(f"Baze RSI: {MIN_RSI}-{MAX_RSI} ({state})")

    candidates = []

    for _, row in df.iterrows():
        symbol = str(row.get("Symbol", ""))
        if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
            continue

        last = float(row.get("Last") or row.get("Close") or 0)
        change = float(row.get("ChangePct") or 0)
        eps = float(row.get("EPS") or 0)

        if last <= 0:
            continue

        # P/E
        pe = None
        if eps > 0:
            pe = round(last / eps, 2)
            if pe > 15 or pe < 0:
                continue

        # تاریخچه
        hist = get_history_safe(symbol)
        if hist is None:
            continue

        closes = hist["Close"].tolist()
        rsi = calc_rsi(closes, 14)
        if rsi is None:
            continue

        # فیلتر داینامیک
        if not (MIN_RSI <= rsi < MAX_RSI):
            continue

        # امتیاز
        score = 0
        mid = (MIN_RSI + MAX_RSI) / 2
        if abs(rsi - mid) < 2:
            score += 50
        elif abs(rsi - mid) < 4:
            score += 30

        if pe and pe < 8:
            score += 20
        elif pe and pe < 12:
            score += 10

        if change < -3:
            score += 20
        elif change < -1:
            score += 10

        candidates.append({
            "symbol": symbol,
            "name": str(row.get("Name", "")),
            "last": last,
            "change": change,
            "pe": pe,
            "rsi": rsi,
            "score": score,
        })

    candidates.sort(key=lambda x: -x["score"])
    return candidates[:5]


def build_message(candidates, market, state, MIN_RSI, MAX_RSI):
    """ساخت پیام"""
    msg = f"📊 Smart_Bourse v10\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    msg += f"📊 بازار: {market['market_pct']:.1f}% مثبت\n"
    msg += f"   🟢 {market['positive']} | 🔴 {market['negative']}\n"
    msg += f"   📊 وضعیت: {state}\n"
    msg += f"   🎯 بازه RSI: {MIN_RSI}-{MAX_RSI}\n\n"

    if not candidates:
        msg += "❌ سیگنالی نیست\n"
        return msg

    msg += f"🏆 {len(candidates)} سهم برتر:\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, s in enumerate(candidates, 1):
        msg += f"{i}. {s['symbol']}\n"
        msg += f"   💰 {int(s['last']):,}\n"
        msg += f"   📉 RSI: {s['rsi']}\n"
        if s['pe']:
            msg += f"   📈 P/E: {s['pe']}\n"
        msg += f"   📊 تغییر: {s['change']:+.2f}%\n"
        msg += f"   🎯 امتیاز: {s['score']}/100\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    return msg


def run_scanner():
    """اجرای اسکنر اصلی"""
    log("Ejraye smart_scanner_v8...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "smart_scanner_v8.py")],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=900,
            encoding='utf-8',
            errors='ignore',
        )
        log(f"   exit: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        log(f"   ERR: {e}")
        return False


def main():
    now = datetime.now()
    now_time = now.time()

    log("=" * 60)
    log("  School Mode v10 - Dynamic")
    log("=" * 60)

    # پیام شروع
    start_msg = f"🎓 Smart_Bourse v10\n"
    start_msg += f"⏰ {now.strftime('%H:%M')}\n"
    start_msg += "🟢 System roshan shod\n"
    start_msg += "🤖 AI داینامیک فعال\n"

    send_eitaa(start_msg)

    if now_time > MARKET_END:
        log("Khorooj - bazar baste")
        return

    if now_time < MARKET_START:
        log(f"Montazere {MARKET_START}...")
        while datetime.now().time() < MARKET_START:
            time.sleep(60)

    log("Shoroo - bazar baz shod")

    last_check = 0
    last_full_scan = 0

    while True:
        now = datetime.now()
        now_time = now.time()

        if now_time > MARKET_END:
            log("Payan - bazar baste")
            break

        # هر 5 دقیقه: تحلیل بازار + اسکن داینامیک
        if time.time() - last_check >= CHECK_INTERVAL:
            last_check = time.time()
            log("Check 5 daqiqe...")

            # ۱. تحلیل بازار
            market = analyze_market()
            if market:
                MIN_RSI, MAX_RSI, state = get_dynamic_rsi_range(market)
                log(f"   Bazar: {market['market_pct']}% | {state}")

                # ۲. اسکن داینامیک
                candidates = scan_stocks(market)
                log(f"   {len(candidates)} candidate")

                # ۳. ارسال
                if candidates:
                    msg = build_message(candidates, market, state, MIN_RSI, MAX_RSI)
                    send_eitaa(msg)

        # هر 30 دقیقه: اسکنر اصلی
        if time.time() - last_full_scan >= FULL_SCAN_INTERVAL:
            last_full_scan = time.time()
            log("Eskene kamel 30 daqiqe...")
            run_scanner()

        time.sleep(60)

    # پیام پایان
    end_msg = f"🏁 Smart_Bourse v10\n"
    end_msg += f"⏰ {datetime.now().strftime('%H:%M')}\n"
    end_msg += "📊 Bazar baste shod"

    send_eitaa(end_msg)

    log("=" * 60)
    log("  Payan")
    log("=" * 60)


if __name__ == "__main__":
    main()

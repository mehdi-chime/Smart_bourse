# school_mode_runner.py
# اجرای خودکار برای وقتی که تو مدرسه‌ای
# اجرا: python school_mode_runner.py

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, time as dtime

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

# ═══════════════════════════════════════════════════════════
# تنظیمات
# ═══════════════════════════════════════════════════════════
HUNTER_DIR = PROJECT_ROOT / "data" / "hunter"
LOG_FILE = PROJECT_ROOT / "logs" / "school_mode.log"
SENT_SIGNALS_FILE = PROJECT_ROOT / "data" / "sent_signals.json"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
SENT_SIGNALS_FILE.parent.mkdir(parents=True, exist_ok=True)

# ساعت‌های اجرا
MARKET_START = dtime(8, 45)
MARKET_END = dtime(12, 30)

# فاصله‌ها (ثانیه)
CHECK_INTERVAL = 60         # هر 1 دقیقه: چک سریع
SCAN_INTERVAL = 300         # هر 5 دقیقه: اسکن کامل
REPORT_INTERVAL = 1800      # هر 30 دقیقه: گزارش

# ═══════════════════════════════════════════════════════════
# لاگ
# ═══════════════════════════════════════════════════════════
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ═══════════════════════════════════════════════════════════
# ایتا
# ═══════════════════════════════════════════════════════════
def send_eitaa(text):
    """ارسال به ایتا"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
        import requests
        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=15)
        if r.status_code == 200:
            log("✅ پیام به ایتا ارسال شد")
            return True
        else:
            log(f"❌ خطا: {r.status_code}")
            return False
    except Exception as e:
        log(f"❌ خطا در ایتا: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# وضعیت بازار
# ═══════════════════════════════════════════════════════════
def check_market_status():
    """وضعیت بازار"""
    import algotik_tse as att
    df = att.get_live_market()
    if df is None or df.empty:
        return None, 0

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    positive = 0
    total = 0

    for _, row in df.iterrows():
        try:
            change = float(row.get("ChangePct") or 0)
            total += 1
            if change > 0:
                positive += 1
        except:
            continue

    if total == 0:
        return None, 0

    return df, positive / total * 100


# ═══════════════════════════════════════════════════════════
# اسکن سریع (watchlist)
# ═══════════════════════════════════════════════════════════
def quick_check(df):
    """چک سریع سهم‌های watchlist"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import WATCH_SYMBOLS
    except:
        WATCH_SYMBOLS = []

    alerts = []

    for item in WATCH_SYMBOLS:
        name = item.get("name", "")
        aliases = item.get("aliases", [name])

        for _, row in df.iterrows():
            sym = str(row.get("Symbol", ""))
            if sym in aliases or sym == name:
                last = float(row.get("Last") or 0)
                change = float(row.get("ChangePct") or 0)
                vol_buy = float(row.get("Vol_buy_retail") or 0)
                vol_sell = float(row.get("Vol_sell_retail") or 0)

                # هشدار: صف
                if vol_buy > 0 and vol_sell == 0:
                    alerts.append(f"🟢 {name}: صف خرید ({int(last):,})")
                elif vol_sell > 0 and vol_buy == 0:
                    alerts.append(f"🔴 {name}: صف فروش ({int(last):,})")

                # هشدار: تغییر > 3%
                if abs(change) >= 3:
                    alerts.append(f"⚡ {name}: {change:+.2f}% ({int(last):,})")

                break

    return alerts


# ═══════════════════════════════════════════════════════════
# اجرای hunter
# ═══════════════════════════════════════════════════════════
def run_hunter():
    """اجرای hunter"""
    log("🎯 اجرای hunter...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scanner" / "opportunity_hunter_v54.py")],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=600,
            encoding='utf-8',
            errors='ignore',
        )
        if result.returncode == 0:
            log("✅ hunter تمام شد")
            return True
        else:
            log(f"❌ hunter خطا (exit {result.returncode})")
            return False
    except Exception as e:
        log(f"❌ خطا: {e}")
        return False


def get_top_signals(n=5):
    """بهترین سیگنال‌ها"""
    hunter_files = sorted(HUNTER_DIR.glob("hunter_*.json"))
    if not hunter_files:
        return []

    latest = hunter_files[-1]
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    if not results:
        return []

    # امتیازدهی: RSI پایین + نسبت بالا
    for r in results:
        rsi_score = max(0, 50 - r.get("rsi", 100)) / 50
        ratio_score = min(r.get("ratio", 0), 5) / 5
        r["score"] = rsi_score * 60 + ratio_score * 40

    results.sort(key=lambda x: -x.get("score", 0))
    return results[:n]


# ═══════════════════════════════════════════════════════════
# فایل سیگنال‌های ارسال‌شده
# ═══════════════════════════════════════════════════════════
def load_sent():
    if SENT_SIGNALS_FILE.exists():
        try:
            with open(SENT_SIGNALS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}


def save_sent(data):
    with open(SENT_SIGNALS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_sent_today(symbol):
    """آیا امروز ارسال شده؟"""
    sent = load_sent()
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{today}_{symbol}"
    return key in sent


def mark_sent(symbol, info):
    """ثبت ارسال"""
    sent = load_sent()
    today = datetime.now().strftime("%Y-%m-%d")
    key = f"{today}_{symbol}"
    sent[key] = {
        "date": today,
        "time": datetime.now().strftime("%H:%M:%S"),
        "info": info,
    }
    save_sent(sent)


# ═══════════════════════════════════════════════════════════
# پیام‌ها
# ═══════════════════════════════════════════════════════════
def build_signal_message(signals, market_pct):
    """پیام سیگنال"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M")

    msg = f"🎯 Smart_Bourse - {date_str} {time_str}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 بازار: {market_pct:.1f}% مثبت\n\n"

    if not signals:
        msg += "❌ سیگنالی نیست\n"
        return msg

    msg += f"🏆 {len(signals)} سهم پیشنهادی:\n\n"

    for i, s in enumerate(signals, 1):
        symbol = s.get("symbol", "?")
        price = s.get("price", 0)
        buy = s.get("buy_target", 0)
        sell = s.get("sell_target", 0)
        stop = s.get("stop_loss", 0)
        rsi = s.get("rsi", 0)

        msg += f"{i}️⃣ 📌 {symbol}\n"
        msg += f"   💰 {int(price):,}\n"
        msg += f"   🟢 خرید: {int(buy):,}\n"
        msg += f"   🔴 فروش: {int(sell):,}\n"
        msg += f"   ⛔ حدضرر: {int(stop):,}\n"
        msg += f"   📊 RSI: {rsi}\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 اگه -3% شد، بخر\n"
    msg += "⛔ حد ضرر جدی\n"

    return msg


def build_report_message(market_pct, alerts, signals):
    """گزارش دوره‌ای"""
    time_str = datetime.now().strftime("%H:%M")

    msg = f"📊 گزارش Smart_Bourse - {time_str}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📈 بازار: {market_pct:.1f}% مثبت\n\n"

    if alerts:
        msg += "⚡ هشدارها:\n"
        for a in alerts[:5]:
            msg += f"   {a}\n"
        msg += "\n"

    if signals:
        msg += f"🎯 {len(signals)} سیگنال فعال:\n"
        for s in signals[:3]:
            msg += f"   📌 {s['symbol']}: خرید {int(s['buy_target']):,}\n"

    return msg


# ═══════════════════════════════════════════════════════════
# اجرای اصلی
# ═══════════════════════════════════════════════════════════
def main():
    log("=" * 60)
    log("  🎓 Smart_Bourse - School Mode")
    log("=" * 60)

    # چک ساعت
    now = datetime.now().time()
    if now < MARKET_START:
        log(f"⏰ هنوز بازار باز نشده ({now})")
        return
    if now > MARKET_END:
        log(f"⏰ بازار بسته شده ({now})")
        return

    log(f"✅ شروع - ساعت {now}")

    # ۱. چک بازار
    log("📊 چک بازار...")
    df, market_pct = check_market_status()
    if df is None:
        log("❌ خطا")
        return

    log(f"   بازار: {market_pct:.1f}% مثبت")

    # ۲. چک سریع watchlist
    alerts = quick_check(df)
    if alerts:
        log(f"   ⚡ {len(alerts)} هشدار")

    # ۳. اسکن کامل
    if market_pct >= 60:
        log("🎯 بازار سبز - اسکن کامل...")
        run_hunter()

        # سیگنال‌ها
        signals = get_top_signals(5)

        # فیلتر: ارسال‌نشده‌ها
        new_signals = [s for s in signals if not is_sent_today(s["symbol"])]

        if new_signals:
            log(f"   📤 {len(new_signals)} سیگنال جدید")
            msg = build_signal_message(new_signals, market_pct)
            send_eitaa(msg)
            for s in new_signals:
                mark_sent(s["symbol"], {"buy": s["buy_target"]})
        else:
            log("   ⚠️ سیگنال جدیدی نیست")
    else:
        log(f"🔴 بازار قرمز ({market_pct:.1f}%)")

        msg = f"🔴 بازار: {market_pct:.1f}% مثبت\n"
        msg += "⏳ صبر می‌کنیم\n"
        if alerts:
            msg += "\n⚡ هشدارها:\n"
            for a in alerts:
                msg += f"   {a}\n"
        send_eitaa(msg)

    log("=" * 60)
    log("  ✅ پایان")
    log("=" * 60)


if __name__ == "__main__":
    main()

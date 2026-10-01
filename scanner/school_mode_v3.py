# school_mode_v3.py
# Smart_Bourse - School Mode v3
# اجرا: python school_mode_v3.py

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
LOG_FILE = PROJECT_ROOT / "logs" / "school_v3.log"
SENT_FILE = PROJECT_ROOT / "data" / "sent_v3.json"
HUNTER_DIR = PROJECT_ROOT / "data" / "hunter"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

MARKET_START = dtime(8, 45)
MARKET_END = dtime(12, 30)

CHECK_INTERVAL = 300      # 5 دقیقه
FULL_SCAN_INTERVAL = 1800 # 30 دقیقه


def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass


# ═══════════════════════════════════════════════════════════
# ایتا
# ═══════════════════════════════════════════════════════════
def send_eitaa(text):
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scanner"))
        from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
        import requests
        url = f"https://eitaayar.ir/api/{EITAA_TOKEN}/sendMessage"
        data = {"chat_id": EITAA_CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=15)
        if r.status_code == 200:
            log("✅ ایتا ارسال شد")
            return True
        log(f"❌ ایتا: {r.status_code}")
        return False
    except Exception as e:
        log(f"❌ ایتا: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# وضعیت بازار
# ═══════════════════════════════════════════════════════════
def get_market_status():
    import algotik_tse as att
    df = att.get_live_market()
    if df is None or df.empty:
        return None, 0, 0, 0

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

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

    if total == 0:
        return None, 0, 0, 0

    return df, positive / total * 100, positive, negative


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


# ═══════════════════════════════════════════════════════════
# تحلیل سهم‌ها (بهبود یافته)
# ═══════════════════════════════════════════════════════════
def analyze_top_stocks(df, n=5):
    """تحلیل و انتخاب بهترین سهم‌ها"""
    candidates = []

    for _, row in df.iterrows():
        try:
            symbol = str(row.get("Symbol", ""))
            if not symbol or symbol.endswith("3") or symbol.endswith("ح"):
                continue

            last = float(row.get("Last") or row.get("Close") or 0)
            yesterday = float(row.get("Yesterday") or 0)
            min_a = float(row.get("MinAllowed") or 0)
            max_a = float(row.get("MaxAllowed") or 0)
            change = float(row.get("ChangePct") or 0)

            if last <= 0 or min_a <= 0 or max_a <= 0:
                continue

            vol_buy = float(row.get("Vol_buy_retail") or 0)
            vol_sell = float(row.get("Vol_sell_retail") or 0)
            vol_buy_n = float(row.get("Vol_buy_institutional") or 0)
            vol_sell_n = float(row.get("Vol_sell_institutional") or 0)

            # فیلتر: فاصله از کف (0-5%)
            distance_from_min = (last - min_a) / min_a * 100
            if distance_from_min > 5:
                continue

            # فیلتر: حجم
            total_vol = vol_buy + vol_sell
            if total_vol < 100_000:
                continue

            # امتیازدهی
            score = 0

            # ۱. فاصله از کف (30 نمره)
            if distance_from_min < 1:
                score += 30  # نزدیک کف = بهترین
            elif distance_from_min < 2:
                score += 25
            elif distance_from_min < 3:
                score += 20
            elif distance_from_min < 5:
                score += 10

            # ۲. حقوقی خریدار (40 نمره)
            if vol_sell_n > 0:
                ratio_n = vol_buy_n / vol_sell_n
                if ratio_n > 5:
                    score += 40  # حقوقی قوی خریدار
                elif ratio_n > 3:
                    score += 30
                elif ratio_n > 1.5:
                    score += 20
                elif ratio_n > 1:
                    score += 10

            # ۳. حقیقی خریدار (20 نمره)
            if vol_sell > 0:
                ratio_r = vol_buy / vol_sell
                if ratio_r > 2:
                    score += 20
                elif ratio_r > 1.5:
                    score += 15
                elif ratio_r > 1:
                    score += 10

            # ۴. تغییر (10 نمره)
            if -3 < change < 0:
                score += 10  # منفی کم = فرصت
            elif 0 <= change < 1:
                score += 5   # نزدیک صفر

            # سود بالقوه
            profit = (max_a / min_a - 1) * 100 - 1.25

            candidates.append({
                "symbol": symbol,
                "last": last,
                "yesterday": yesterday,
                "min_a": min_a,
                "max_a": max_a,
                "change": change,
                "distance_from_min": distance_from_min,
                "vol_buy": vol_buy,
                "vol_sell": vol_sell,
                "vol_buy_n": vol_buy_n,
                "vol_sell_n": vol_sell_n,
                "score": score,
                "profit": profit,
                "buy_target": min_a,
                "sell_target": max_a,
                "stop_loss": min_a * 0.98,
            })
        except:
            continue

    candidates.sort(key=lambda x: -x["score"])
    return candidates[:n]


# ═══════════════════════════════════════════════════════════
# پیام
# ═══════════════════════════════════════════════════════════
def build_signal_msg(signals, market_pct, positive, negative):
    time_str = datetime.now().strftime("%H:%M")

    msg = f"🎯 Smart_Bourse - {time_str}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 بازار: {market_pct:.1f}% مثبت\n"
    msg += f"   🟢 {positive} | 🔴 {negative}\n\n"

    if not signals:
        msg += "❌ سیگنالی نیست\n"
        return msg

    msg += f"🏆 {len(signals)} فرصت:\n\n"

    for i, s in enumerate(signals, 1):
        msg += f"{i}️⃣ {s['symbol']}\n"
        msg += f"   💰 {int(s['last']):,} ({s['change']:+.2f}%)\n"
        msg += f"   🟢 خرید: {int(s['buy_target']):,}\n"
        msg += f"   🔴 فروش: {int(s['sell_target']):,}\n"
        msg += f"   ⛔ حدضرر: {int(s['stop_loss']):,}\n"
        msg += f"   💰 سود: {s['profit']:.1f}%\n"

        # حقوقی
        if s['vol_sell_n'] > 0:
            ratio_n = s['vol_buy_n'] / s['vol_sell_n']
            if ratio_n > 2:
                msg += f"   🏛️ حقوقی خریدار ({ratio_n:.1f}x)\n"
        msg += "\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 اگه -3% شد، بخر\n"
    msg += "⛔ حد ضرر جدی\n"

    return msg


def build_report_msg(market_pct, positive, negative, signals):
    time_str = datetime.now().strftime("%H:%M")

    msg = f"📊 گزارش {time_str}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📈 بازار: {market_pct:.1f}% مثبت\n"
    msg += f"   🟢 {positive} | 🔴 {negative}\n\n"

    if signals:
        msg += f"🎯 {len(signals)} فرصت فعال:\n"
        for s in signals[:3]:
            msg += f"   📌 {s['symbol']}: خرید {int(s['buy_target']):,}\n"
    else:
        msg += "⏳ فرصت جدیدی نیست\n"

    return msg


# ═══════════════════════════════════════════════════════════
# ذخیره
# ═══════════════════════════════════════════════════════════
def load_sent():
    if SENT_FILE.exists():
        try:
            with open(SENT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}


def save_sent(data):
    try:
        with open(SENT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass


# ═══════════════════════════════════════════════════════════
# اجرای hunter
# ═══════════════════════════════════════════════════════════
def run_hunter():
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
        log(f"   exit: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        log(f"❌ {e}")
        return False


# ═══════════════════════════════════════════════════════════
# حلقه اصلی
# ═══════════════════════════════════════════════════════════
def main():
    log("=" * 60)
    log("  🎓 School Mode v3 - شروع")
    log("=" * 60)

    # پیام شروع
    start_msg = f"🎓 Smart_Bourse v3\n"
    start_msg += f"⏰ {datetime.now().strftime('%H:%M')}\n"
    start_msg += "🟢 سیستم روشن شد\n"
    start_msg += "📊 در حال چک بازار..."
    send_eitaa(start_msg)

    last_check = 0
    last_full_scan = 0
    last_status = None

    while True:
        now = datetime.now()
        now_time = now.time()

        if now_time < MARKET_START:
            time.sleep(60)
            continue

        if now_time > MARKET_END:
            log("⏰ بازار بسته شد")
            break

        # وضعیت بازار
        df, market_pct, positive, negative = get_market_status()
        if df is None:
            time.sleep(60)
            continue

        # هر 5 دقیقه: چک
        if time.time() - last_check >= CHECK_INTERVAL:
            last_check = time.time()
            log(f"📊 چک: {market_pct:.1f}% ({positive}🟢/{negative}🔴)")

            signals = analyze_top_stocks(df, 5)

            # فیلتر ارسال‌نشده
            sent = load_sent()
            today = now.strftime("%Y-%m-%d")
            new_signals = []
            for s in signals:
                key = f"{today}_{s['symbol']}"
                if key not in sent:
                    new_signals.append(s)
                    sent[key] = {"time": now.strftime("%H:%M")}

            if new_signals:
                log(f"📤 {len(new_signals)} سیگنال جدید")
                msg = build_signal_msg(new_signals, market_pct, positive, negative)
                send_eitaa(msg)
                save_sent(sent)
            else:
                log("⏳ سیگنال جدیدی نیست")

        # هر 30 دقیقه: اسکن کامل
        if time.time() - last_full_scan >= FULL_SCAN_INTERVAL:
            last_full_scan = time.time()
            log("🎯 اسکن کامل...")

            if market_pct >= 50:
                run_hunter()

                signals = analyze_top_stocks(df, 5)
                if signals:
                    msg = build_report_msg(market_pct, positive, negative, signals)
                    send_eitaa(msg)

        time.sleep(60)

    # پیام پایان
    end_msg = f"🏁 Smart_Bourse v3\n"
    end_msg += f"⏰ {datetime.now().strftime('%H:%M')}\n"
    end_msg += "📊 بازار بسته شد\n"
    send_eitaa(end_msg)

    log("=" * 60)
    log("  ✅ پایان")
    log("=" * 60)


if __name__ == "__main__":
    main()

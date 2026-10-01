# school_mode_v2.py
# سیستم خودکار مدرسه - نسخه کامل
# اجرا: python school_mode_v2.py

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
LOG_FILE = PROJECT_ROOT / "logs" / "school_mode_v2.log"
SENT_FILE = PROJECT_ROOT / "data" / "sent_signals_v2.json"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ساعت‌ها
MARKET_START = dtime(8, 45)
MARKET_END = dtime(12, 30)

# فاصله‌ها (ثانیه)
CHECK_INTERVAL = 300      # 5 دقیقه: چک سریع
FULL_SCAN_INTERVAL = 1800 # 30 دقیقه: اسکن کامل

# ═══════════════════════════════════════════════════════════
# لاگ
# ═══════════════════════════════════════════════════════════
def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


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
        return None, 0

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
        return None, 0

    return df, positive / total * 100


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


def get_best_signals(n=5):
    """بهترین سیگنال‌ها با MinAllowed"""
    import algotik_tse as att
    
    hunter_files = sorted(HUNTER_DIR.glob("hunter_*.json"))
    if not hunter_files:
        return []
    
    with open(hunter_files[-1], "r", encoding="utf-8") as f:
        data = json.load(f)
    
    results = data.get("results", [])
    if not results:
        return []
    
    # دریافت داده زنده
    live_df = att.get_live_market()
    if live_df is None or live_df.empty:
        return []
    
    if "InstrumentType" in live_df.columns:
        live_df = live_df[live_df["InstrumentType"] == 300]
    
    # برای هر سهم، MinAllowed و حقوقی رو چک کن
    best = []
    
    def normalize(s):
        return (str(s).replace("\u0643", "\u06a9").replace("\u064a", "\u06cc")
                .replace("\u0649", "\u06cc").replace("\u0629", "\u0647")
                .replace("\u0640", "").strip())
    
    for r in results:
        symbol = r["symbol"]
        
        # پیدا کردن
        found = None
        for _, row in live_df.iterrows():
            if normalize(str(row.get("Symbol", ""))) == normalize(symbol):
                found = row
                break
        
        if found is None:
            continue
        
        last = float(found.get("Last") or 0)
        min_a = float(found.get("MinAllowed") or 0)
        max_a = float(found.get("MaxAllowed") or 0)
        vol_buy_n = float(found.get("Vol_buy_institutional") or 0)
        vol_sell_n = float(found.get("Vol_sell_institutional") or 0)
        rsi = r.get("rsi", 100)
        
        if min_a <= 0 or max_a <= 0:
            continue
        
        # امتیازدهی
        score = 0
        
        # RSI
        if rsi < 30:
            score += 40
        elif rsi < 40:
            score += 30
        elif rsi < 50:
            score += 20
        
        # حقوقی
        if vol_buy_n > vol_sell_n * 3:
            score += 40
        elif vol_buy_n > vol_sell_n:
            score += 20
        
        # فاصله تا کف
        if last > 0:
            distance = (last - min_a) / min_a * 100
            if distance < 1:
                score += 20
            elif distance < 2:
                score += 15
            elif distance < 3:
                score += 10
        
        best.append({
            "symbol": symbol,
            "last": last,
            "min_a": min_a,
            "max_a": max_a,
            "rsi": rsi,
            "score": score,
            "vol_buy_n": vol_buy_n,
            "vol_sell_n": vol_sell_n,
            "profit": ((max_a / min_a) - 1) * 100 - 1.25,
        })
    
    best.sort(key=lambda x: -x["score"])
    return best[:n]


# ═══════════════════════════════════════════════════════════
# پیام‌ها
# ═══════════════════════════════════════════════════════════
def build_signal_msg(signals, market_pct):
    time_str = datetime.now().strftime("%H:%M")
    
    msg = f"🎯 Smart_Bourse - {time_str}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += f"📊 بازار: {market_pct:.1f}% مثبت\n\n"
    
    if not signals:
        msg += "❌ سیگنالی نیست\n"
        return msg
    
    msg += f"🏆 {len(signals)} سهم برتر:\n\n"
    
    for i, s in enumerate(signals, 1):
        msg += f"{i}️⃣ {s['symbol']}\n"
        msg += f"   💰 {int(s['last']):,}\n"
        msg += f"   🟢 {int(s['min_a']):,}\n"
        msg += f"   🔴 {int(s['max_a']):,}\n"
        msg += f"   ⛔ {int(s['min_a'] * 0.98):,}\n"
        msg += f"   📊 RSI: {s['rsi']} | سود: {s['profit']:.1f}%\n"
        msg += f"   🏛️ حقوقی: {int(s['vol_buy_n']/1_000_000)}M vs {int(s['vol_sell_n']/1_000_000)}M\n\n"
    
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "💡 اگه -3% شد، بخر\n"
    msg += "⛔ حد ضرر جدی\n"
    
    return msg


def build_report_msg(market_pct, signals):
    time_str = datetime.now().strftime("%H:%M")
    
    msg = f"📊 گزارش {time_str}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📈 بازار: {market_pct:.1f}% مثبت\n\n"
    
    if signals:
        msg += f"🎯 {len(signals)} فرصت:\n"
        for s in signals[:3]:
            msg += f"   📌 {s['symbol']}: خرید {int(s['min_a']):,}\n"
    else:
        msg += "⏳ فرصت جدیدی نیست\n"
    
    return msg


# ═══════════════════════════════════════════════════════════
# ذخیره ارسال‌شده
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
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════
# حلقه اصلی
# ═══════════════════════════════════════════════════════════
def main():
    log("=" * 60)
    log("  🎓 School Mode v2 - شروع")
    log("=" * 60)
    
    last_full_scan = 0
    last_check = 0
    
    while True:
        now = datetime.now()
        now_time = now.time()
        
        # چک ساعت
        if now_time < MARKET_START:
            log(f"⏰ صبر تا {MARKET_START}")
            time.sleep(60)
            continue
        
        if now_time > MARKET_END:
            log("⏰ بازار بسته شد")
            break
        
        # چک بازار
        df, market_pct = get_market_status()
        if df is None:
            time.sleep(60)
            continue
        
        # هر 5 دقیقه: چک سیگنال
        if time.time() - last_check >= CHECK_INTERVAL:
            last_check = time.time()
            log(f"📊 چک {market_pct:.1f}%...")
            
            signals = get_best_signals(5)
            
            # فیلتر: ارسال‌نشده‌ها
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
                msg = build_signal_msg(new_signals, market_pct)
                send_eitaa(msg)
                save_sent(sent)
            else:
                log("⏳ سیگنال جدیدی نیست")
        
        # هر 30 دقیقه: اسکن کامل
        if time.time() - last_full_scan >= FULL_SCAN_INTERVAL:
            last_full_scan = time.time()
            log("🎯 اسکن کامل...")
            
            if market_pct >= 60:
                run_hunter()
                
                signals = get_best_signals(5)
                if signals:
                    msg = build_report_msg(market_pct, signals)
                    send_eitaa(msg)
        
        # صبر
        time.sleep(60)
    
    log("=" * 60)
    log("  ✅ پایان")
    log("=" * 60)


if __name__ == "__main__":
    main()

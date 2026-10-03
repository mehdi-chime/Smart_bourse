# school_mode_v8.py
# Smart_Bourse v8 - School Mode + Eitaa Signals
# اجرا: python school_mode_v8.py

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

LOG_FILE = PROJECT_ROOT / "logs" / "school_v8.log"
SENT_FILE = PROJECT_ROOT / "data" / "sent_v8.json"

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# ساعت‌ها
MARKET_START = dtime(8, 45)
MARKET_END = dtime(12, 30)

# فاصله‌ها
CHECK_INTERVAL = 300      # هر 5 دقیقه
FULL_SCAN_INTERVAL = 1800 # هر 30 دقیقه


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
    """ارسال به ایتا"""
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


def run_scanner():
    """اجرای smart_scanner_v8"""
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

        if result.stdout:
            for line in result.stdout.split("\n")[-10:]:
                if line.strip():
                    log(f"   {line}")

        return result.returncode == 0
    except Exception as e:
        log(f"   ERR: {e}")
        return False


def get_latest_hunter_file():
    """پیدا کردن آخرین فایل hunter"""
    hunter_dir = PROJECT_ROOT / "data" / "hunter"
    if not hunter_dir.exists():
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    files = sorted(hunter_dir.glob(f"*{today}*.json"), reverse=True)

    if not files:
        files = sorted(hunter_dir.glob("*.json"), reverse=True)

    return files[0] if files else None


def send_scanner_result():
    """ارسال نتیجه اسکنر به ایتا"""
    log("Send scanner result...")

    latest = get_latest_hunter_file()
    if not latest:
        log("   No hunter file")
        return False

    try:
        data = json.loads(latest.read_text(encoding="utf-8"))
    except Exception as e:
        log(f"   JSON error: {e}")
        return False

    top = data.get("top", [])
    if not top:
        log("   No signals")
        return False

    # چک تکراری
    sent = load_sent()
    today = datetime.now().strftime("%Y-%m-%d")
    last_hash = sent.get(today, "")

    current_hash = f"{len(top)}_{top[0].get('symbol', '')}_{top[0].get('score', 0)}"
    if last_hash == current_hash:
        log("   Already sent")
        return False

    # پیام
    msg = f"📊 Smart_Bourse Scanner v8\n"
    msg += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, s in enumerate(top[:5], 1):
        msg += f"{i}. {s.get('symbol', '?')}\n"
        msg += f"   💰 {int(s.get('last', 0)):,}\n"
        msg += f"   📉 RSI: {s.get('rsi', '?')}\n"
        msg += f"   📈 P/E: {s.get('pe', '?')}\n"
        msg += f"   🎯 {s.get('score', '?')}/100\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if send_eitaa(msg):
        sent[today] = current_hash
        save_sent(sent)
        log(f"   Sent {len(top)} signals")
        return True

    return False


def load_sent():
    if SENT_FILE.exists():
        try:
            return json.loads(SENT_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {}


def save_sent(data):
    try:
        SENT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except:
        pass


def send_market_status():
    """ارسال وضعیت بازار"""
    log("Send market status...")

    try:
        import algotik_tse as att
        df = att.get_live_market()

        if df is None or df.empty:
            return False

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

        pct = positive / total * 100 if total > 0 else 0

        msg = f"📊 وضعیت بازار\n"
        msg += f"📅 {datetime.now().strftime('%H:%M')}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🟢 مثبت: {positive}\n"
        msg += f"🔴 منفی: {negative}\n"
        msg += f"📈 درصد: {pct:.1f}%\n"
        msg += "━━━━━━━━━━━━━━━━━━━━"

        return send_eitaa(msg)
    except Exception as e:
        log(f"   ERR: {e}")
        return False


def main():
    now = datetime.now()
    now_time = now.time()

    log("=" * 60)
    log("  School Mode v8 - Shoroo")
    log("=" * 60)

    # پیام شروع
    start_msg = f"🎓 Smart_Bourse v8\n"
    start_msg += f"⏰ {now.strftime('%H:%M')}\n"
    start_msg += "🟢 System roshan shod\n"

    if now_time < MARKET_START:
        start_msg += f"⏳ Montazere bazar (8:45)..."
    elif now_time > MARKET_END:
        start_msg += "⏰ Bazar baste"
    else:
        start_msg += "📊 Dar hale check bazar..."

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

        # هر 5 دقیقه
        if time.time() - last_check >= CHECK_INTERVAL:
            last_check = time.time()
            log("Check 5 daqiqe...")
            run_scanner()
            send_scanner_result()

        # هر 30 دقیقه
        if time.time() - last_full_scan >= FULL_SCAN_INTERVAL:
            last_full_scan = time.time()
            log("Eskene kamel 30 daqiqe...")
            run_scanner()
            send_market_status()
            send_scanner_result()

        time.sleep(60)

    end_msg = f"🏁 Smart_Bourse v8\n"
    end_msg += f"⏰ {datetime.now().strftime('%H:%M')}\n"
    end_msg += "📊 Bazar baste shod"
    send_eitaa(end_msg)

    log("=" * 60)
    log("  Payan")
    log("=" * 60)


if __name__ == "__main__":
    main()

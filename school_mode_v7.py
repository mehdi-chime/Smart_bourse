# school_mode_v7.py
# Smart_Bourse - نسخه نهایی
# اجرا: python school_mode_v7.py

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, time as dtime

# ✅ UTF-8
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

LOG_FILE = PROJECT_ROOT / "logs" / "school_v7.log"
SENT_FILE = PROJECT_ROOT / "data" / "sent_v7.json"

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
    """اجرای smart_scanner_v5"""
    log("Ejraye smart_scanner_v5...")
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "smart_scanner_v5.py")],
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


def get_market_status():
    import algotik_tse as att
    try:
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
        return df, positive / total * 100 if total > 0 else 0
    except:
        return None, 0


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


def main():
    now = datetime.now()
    now_time = now.time()

    log("=" * 60)
    log("  School Mode v7 - Shoroo")
    log("=" * 60)

    # پیام شروع
    start_msg = f"🎓 Smart_Bourse v7\n"
    start_msg += f"⏰ {now.strftime('%H:%M')}\n"
    start_msg += "🟢 System roshan shod\n"

    if now_time < MARKET_START:
        start_msg += f"⏳ Montazere bazar (8:45)..."
        log("Montazere 8:45...")
    elif now_time > MARKET_END:
        start_msg += f"⏰ Bazar baste"
        log("Bazar baste")
    else:
        start_msg += f"📊 Dar hale check bazar..."

    send_eitaa(start_msg)

    # چک ساعت
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

        # هر 30 دقیقه
        if time.time() - last_full_scan >= FULL_SCAN_INTERVAL:
            last_full_scan = time.time()
            log("Eskene kamel 30 daqiqe...")
            run_scanner()

        time.sleep(60)

    end_msg = f"🏁 Smart_Bourse v7\n"
    end_msg += f"⏰ {datetime.now().strftime('%H:%M')}\n"
    end_msg += "📊 Bazar baste shod"
    send_eitaa(end_msg)

    log("=" * 60)
    log("  Payan")
    log("=" * 60)


if __name__ == "__main__":
    main()

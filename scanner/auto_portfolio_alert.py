
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

LOCK_FILE = PROJECT_ROOT / "data" / "portfolio_alert.lock"
LOG_DIR = PROJECT_ROOT / "logs"


def log(msg):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / ("auto_alert_" + datetime.now().strftime("%Y-%m-%d") + ".log")
    line = "[" + datetime.now().strftime("%H:%M:%S") + "] " + msg
    print(line)
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def check_lock():
    if LOCK_FILE.exists():
        try:
            age = time.time() - LOCK_FILE.stat().st_mtime
            if age < 120:
                log("already running - exiting")
                return False
        except Exception:
            pass
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(str(datetime.now().isoformat()))
    return True


def release_lock():
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
    except Exception:
        pass


def is_weekend():
    wd = datetime.now().weekday()
    return wd not in [5, 6, 0, 1, 2]


def wait_until_market():
    """اگه قبل ۹ صبح بود، صبر کن"""
    while True:
        now = datetime.now()
        h, m = now.hour, now.minute
        if h < 9:
            # چک هر ۵ دقیقه
            log("before 9:00 - waiting")
            time.sleep(300)
            continue
        return True


def is_market_time():
    now = datetime.now()
    h, m = now.hour, now.minute
    if h < 9:
        return False
    if h > 12:
        return False
    if h == 12 and m > 30:
        return False
    return True


def main():
    log("=" * 50)
    log("Portfolio Alert auto-start")

    if is_weekend():
        log("weekend - exiting")
        return

    now = datetime.now()
    if now.hour > 12 or (now.hour == 12 and now.minute > 30):
        log("after market - exiting")
        return

    if not check_lock():
        return

    try:
        if now.hour < 9:
            wait_until_market()

        log("starting alert monitor...")
        from scanner.portfolio_alert import main as alert_main
        alert_main()
    except KeyboardInterrupt:
        log("stopped by user")
    except Exception as e:
        log("error: " + str(e)[:100])
    finally:
        release_lock()


if __name__ == "__main__":
    main()

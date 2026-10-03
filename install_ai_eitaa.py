# install_ai_eitaa.py
# نصب و اصلاح خودکار پل AI ↔ ایتا
# اجرا: python install_ai_eitaa.py

import os
import sys
from pathlib import Path

# ===== مسیرها =====
PROJECT_ROOT = Path(__file__).parent.absolute()
EITAA_DIR = PROJECT_ROOT / "eitaa"
BRIDGE_FILE = EITAA_DIR / "ai_eitaa_bridge.py"

print("=" * 60)
print("🤖 نصب خودکار پل AI ↔ ایتا")
print("=" * 60)
print()

# ===== قدم ۱: ساخت پوشه eitaa =====
print("📁 قدم ۱: ساخت پوشه eitaa...")
EITAA_DIR.mkdir(exist_ok=True)
print(f"   ✅ ساخته شد: {EITAA_DIR}")
print()

# ===== قدم ۲: ساخت فایل bridge =====
print("📝 قدم ۲: ساخت ai_eitaa_bridge.py...")

bridge_content = '''# eitaa/ai_eitaa_bridge.py
# پل بین AI و ایتا (نسخه بدون HTML)
# AI → ایتا

import requests
import logging
from pathlib import Path
import sys

# لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# مسیر پروژه
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scanner"))

# ⚠️ از alert_config.py بخون
try:
    from alert_config import EITAA_TOKEN, EITAA_CHAT_ID
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "alert_config",
        PROJECT_ROOT / "scanner" / "alert_config.py"
    )
    alert_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(alert_config)
    EITAA_TOKEN = alert_config.EITAA_TOKEN
    EITAA_CHAT_ID = alert_config.EITAA_CHAT_ID


class EitaaBridge:
    """پل ارسال پیام به ایتا"""

    def __init__(self, token=None, chat_id=None):
        self.token = token or EITAA_TOKEN
        self.chat_id = chat_id or EITAA_CHAT_ID
        self.base_url = f"https://eitaayar.ir/api/{self.token}"

    def send_message(self, text, chat_id=None):
        """ارسال پیام ساده (بدون HTML)"""
        target = chat_id or self.chat_id
        url = f"{self.base_url}/sendMessage"

        data = {
            "chat_id": target,
            "text": text
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("✅ پیام به ایتا ارسال شد")
                return True
            else:
                logger.error(f"❌ خطا: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ خطا در ارسال: {e}")
            return False

    def send_ai_signal(self, symbol, advice, score, confidence, mode):
        """ارسال سیگنال AI (بدون HTML)"""
        emoji = "🟢" if score > 70 else "🟡" if score > 50 else "🔴"

        text = f"""{emoji} سیگنال AI {emoji}

📊 نماد: {symbol}
💡 مشاوره: {advice}
🎯 امتیاز: {score:.1f}
📈 اعتماد: {confidence:.2f}
🤖 حالت: {mode}

⏰ Smart_Bourse"""
        return self.send_message(text)

    def send_ai_signals_list(self, signals):
        """ارسال لیست سیگنال‌ها"""
        if not signals:
            return self.send_message("🔴 هیچ سیگنالی برای امروز نیست")

        text = "🤖 سیگنال‌های AI امروز 🤖\\n\\n"
        for i, sig in enumerate(signals, 1):
            emoji = "🟢" if sig.get("score", 0) > 70 else "🟡" if sig.get("score", 0) > 50 else "🔴"
            text += f"{emoji} {i}. {sig.get('symbol', '?')}\\n"
            text += f"   امتیاز: {sig.get('score', 0):.1f}\\n"
            text += f"   مشاوره: {sig.get('advice', '?')}\\n\\n"

        text += "⏰ Smart_Bourse"
        return self.send_message(text)


# ===== تست =====
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 تست ارسال به ایتا")
    print("=" * 60)

    bridge = EitaaBridge()

    # تست ۱: پیام ساده
    print("\\n📤 تست ۱: پیام ساده...")
    result = bridge.send_message("🤖 سلام از Smart_Bourse!\\nاین یه تست از AI است.")
    print(f"   نتیجه: {'✅ موفق' if result else '❌ ناموفق'}")

    # تست ۲: سیگنال AI
    if result:
        print("\\n📤 تست ۲: سیگنال AI...")
        result2 = bridge.send_ai_signal(
            symbol="خگستر",
            advice="فرصت خوب",
            score=76.5,
            confidence=0.65,
            mode="ML+weight"
        )
        print(f"   نتیجه: {'✅ موفق' if result2 else '❌ ناموفق'}")

    # تست ۳: لیست سیگنال‌ها
    if result:
        print("\\n📤 تست ۳: لیست سیگنال‌ها...")
        result3 = bridge.send_ai_signals_list([
            {"symbol": "خگستر", "score": 76.5, "advice": "فرصت خوب"},
            {"symbol": "فولاد", "score": 62.0, "advice": "کاندید متوسط"},
            {"symbol": "احیا", "score": 51.8, "advice": "ضعیف"},
        ])
        print(f"   نتیجه: {'✅ موفق' if result3 else '❌ ناموفق'}")

    print("\\n" + "=" * 60)
'''

BRIDGE_FILE.write_text(bridge_content, encoding="utf-8")
print(f"   ✅ ساخته شد: {BRIDGE_FILE}")
print()

# ===== قدم ۳: چک alert_config.py =====
print("🔍 قدم ۳: چک alert_config.py...")
ALERT_CONFIG = PROJECT_ROOT / "scanner" / "alert_config.py"
if ALERT_CONFIG.exists():
    print(f"   ✅ وجود دارد: {ALERT_CONFIG}")
else:
    print(f"   ⚠️  پیدا نشد: {ALERT_CONFIG}")
    print("   لطفاً فایل alert_config.py رو بساز!")
print()

# ===== قدم ۴: چک requests =====
print("🧪 قدم ۴: چک کتابخانه requests...")
try:
    import requests
    print(f"   ✅ نصب شده (نسخه {requests.__version__})")
except ImportError:
    print("   ⚠️  نصب نیست! نصب می‌کنم...")
    os.system(f"{sys.executable} -m pip install requests")
print()

# ===== قدم ۵: تست =====
print("=" * 60)
print("🎯 قدم ۵: تست ارسال به ایتا")
print("=" * 60)
print()

# تغییر مسیر به eitaa
os.chdir(EITAA_DIR)
os.system(f"{sys.executable} ai_eitaa_bridge.py")

print()
print("=" * 60)
print("🎉 نصب کامل شد!")
print("=" * 60)
print()
print("📋 قدم بعدی:")
print("   - پیام‌های تست رو توی ایتا چک کن")
print("   - اگه رسیدن → بریم مرحله بعد (اتصال AI)")
print()

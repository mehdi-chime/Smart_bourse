# install_telegram.py
# نصب خودکار ربات تلگرام Smart_Bourse
# اجرا: python install_telegram.py

import os
import sys
import shutil
from pathlib import Path

# ⚠️ توکن رو اینجا بذار
TELEGRAM_BOT_TOKEN = "7620060007:AAFQQu87_zcEBkEqAZVHHkHEe-fGmUMqVv0"

# مسیر پروژه
PROJECT_ROOT = Path(__file__).parent.absolute()
TELEGRAM_DIR = PROJECT_ROOT / "telegram_bot"

print("=" * 60)
print("🤖 نصب خودکار ربات تلگرام Smart_Bourse")
print("=" * 60)
print()

# ===== قدم ۱: ساخت پوشه =====
print("📁 قدم ۱: ساخت پوشه telegram_bot...")
TELEGRAM_DIR.mkdir(exist_ok=True)
print(f"   ✅ ساخته شد: {TELEGRAM_DIR}")
print()

# ===== قدم ۲: حذف پوشه قدیمی telegram (اگه هست) =====
OLD_DIR = PROJECT_ROOT / "telegram"
if OLD_DIR.exists() and OLD_DIR.is_dir():
    try:
        # فقط اگه پوشه‌ی ماست حذف کن
        contents = list(OLD_DIR.iterdir())
        if len(contents) <= 5:  # فایل‌های ما
            print("🗑️  حذف پوشه‌ی قدیمی telegram...")
            shutil.rmtree(OLD_DIR)
            print("   ✅ حذف شد")
        else:
            print(f"⚠️  پوشه telegram فایل زیاد داره ({len(contents)} تا)، حذف نشد")
    except Exception as e:
        print(f"⚠️  نتونستم حذف کنم: {e}")
    print()

# ===== قدم ۳: ساخت config.py =====
print("📝 قدم ۳: ساخت telegram_bot/config.py...")
config_content = f'''# telegram_bot/config.py
# ⚠️ این فایل نباید توی GitHub بره!

TELEGRAM_BOT_TOKEN = "{TELEGRAM_BOT_TOKEN}"

# chat_id خودت رو بعداً پر می‌کنیم
TELEGRAM_CHAT_ID = None
'''

config_file = TELEGRAM_DIR / "config.py"
config_file.write_text(config_content, encoding="utf-8")
print(f"   ✅ ساخته شد: {config_file}")
print()

# ===== قدم ۴: ساخت __init__.py =====
print("📝 قدم ۴: ساخت telegram_bot/__init__.py...")
init_file = TELEGRAM_DIR / "__init__.py"
init_file.write_text("# telegram_bot package\n", encoding="utf-8")
print(f"   ✅ ساخته شد: {init_file}")
print()

# ===== قدم ۵: ساخت telegram_bot.py =====
print("📝 قدم ۵: ساخت telegram_bot/telegram_bot.py...")
bot_content = '''# telegram_bot/telegram_bot.py
# ربات تلگرام Smart_Bourse

import asyncio
import logging
import os
import sys

# اضافه کردن مسیر به sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Bot
from telegram.error import TelegramError

# لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """ربات تلگرام ساده برای ارسال پیام"""

    def __init__(self, token, chat_id=None):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)

    async def send_message(self, text, chat_id=None):
        """ارسال پیام ساده"""
        target = chat_id or self.chat_id
        if not target:
            logger.error("chat_id مشخص نیست!")
            return False

        try:
            await self.bot.send_message(
                chat_id=target,
                text=text,
                parse_mode='HTML'
            )
            logger.info(f"پیام ارسال شد به {target}")
            return True
        except TelegramError as e:
            logger.error(f"خطا در ارسال: {e}")
            return False

    async def get_me(self):
        """اطلاعات ربات"""
        return await self.bot.get_me()

    async def get_updates(self):
        """آخرین پیام‌ها (برای پیدا کردن chat_id)"""
        updates = await self.bot.get_updates()
        return updates


async def main():
    """تست اتصال"""
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

    bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

    # اطلاعات ربات
    me = await bot.get_me()
    print()
    print("=" * 60)
    print(f"✅ ربات متصل شد: @{me.username}")
    print(f"   نام: {me.first_name}")
    print(f"   ID: {me.id}")
    print("=" * 60)
    print()
    print("🎯 قدم بعدی: برو توی تلگرام، ربات رو پیدا کن و /start بزن")
    print(f"   لینک: https://t.me/{me.username}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
'''

bot_file = TELEGRAM_DIR / "telegram_bot.py"
bot_file.write_text(bot_content, encoding="utf-8")
print(f"   ✅ ساخته شد: {bot_file}")
print()

# ===== قدم ۶: تست import =====
print("🧪 قدم ۶: تست نصب...")
try:
    import telegram
    print(f"   ✅ python-telegram-bot نصب شده (نسخه {telegram.__version__})")
except ImportError:
    print("   ❌ python-telegram-bot نصب نیست!")
    print("   اجرا کن: pip install python-telegram-bot")
    sys.exit(1)
print()

# ===== قدم ۷: چک ساختار =====
print("📂 قدم ۷: چک ساختار نهایی...")
files = list(TELEGRAM_DIR.glob("*.py"))
for f in files:
    size = f.stat().st_size
    print(f"   ✅ {f.name} ({size} bytes)")
print()

# ===== پایان =====
print("=" * 60)
print("🎉 نصب کامل شد!")
print("=" * 60)
print()
print("📋 قدم بعدی:")
print(f'   cd "{TELEGRAM_DIR}"')
print("   python telegram_bot.py")
print()

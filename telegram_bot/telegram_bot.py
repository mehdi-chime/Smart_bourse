# telegram_bot/telegram_bot.py
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

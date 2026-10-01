# telegram_reader.py
# خواندن کانال‌های عمومی تلگرام
# اجرا: python telegram_reader.py

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

# ═══════════════════════════════════════════════════════════
# کانال‌های عمومی بورسی
# ═══════════════════════════════════════════════════════════
CHANNELS = [
    "bourse24ir",
    "Rasadchi24",
    "Codal360_ir",
    "SahamShenas",
    "tehbours",
    "BazarBourseTehran",
    "parsistahlil",
    "nabzebourse_ir",
]

# ═══════════════════════════════════════════════════════════
# API
# ═══════════════════════════════════════════════════════════
API_ID = 0        # ← از my.telegram.org
API_HASH = ""     # ← از my.telegram.org

# ═══════════════════════════════════════════════════════════
# ذخیره
# ═══════════════════════════════════════════════════════════
OUTPUT_DIR = PROJECT_ROOT / "data" / "telegram"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


async def read_channel(client, channel_name):
    """خواندن یه کانال"""
    try:
        from telethon.tl.functions.channels import GetFullChannelRequest

        entity = await client.get_entity(channel_name)
        full = await client(GetFullChannelRequest(entity))

        # ۲۰ پیام آخر
        messages = []
        async for msg in client.iter_messages(entity, limit=20):
            if msg.text:
                messages.append({
                    "date": msg.date.strftime("%Y-%m-%d %H:%M"),
                    "text": msg.text[:500],
                    "views": msg.views or 0,
                    "forwards": msg.forwards or 0,
                })

        return {
            "channel": channel_name,
            "title": entity.title,
            "subscribers": full.full_chat.participants_count,
            "messages": messages,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        safe_print(f"  ERR {channel_name}: {e}")
        return None


async def main_async():
    safe_print("")
    safe_print("=" * 90)
    safe_print(f"  Telegram Reader - کانال‌های بورسی")
    safe_print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 90)
    safe_print("")

    if not API_ID or not API_HASH:
        safe_print("  ❌ API_ID و API_HASH تنظیم نشده!")
        safe_print("")
        safe_print("  مراحل:")
        safe_print("  ۱. برو به my.telegram.org")
        safe_print("  ۲. لاگین کن با شماره تلفن")
        safe_print("  ۳. API development tools")
        safe_print("  ۴. API_ID و API_HASH رو بردار")
        safe_print("  ۵. تو کد بذار")
        return

    from telethon import TelegramClient

    client = TelegramClient('session_bourse', API_ID, API_HASH)
    await client.start()

    safe_print("  ✅ Telegram connected")
    safe_print("")

    results = []
    for ch in CHANNELS:
        safe_print(f"  📡 {ch}...")
        data = await read_channel(client, ch)
        if data:
            results.append(data)
            safe_print(f"     ✅ {data['title']} ({data['subscribers']:,} عضو)")
        safe_print("")

    # ذخیره
    output = OUTPUT_DIR / f"telegram_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    safe_print("=" * 90)
    safe_print(f"  ✅ {len(results)} کانال")
    safe_print(f"  💾 {output}")
    safe_print("=" * 90)
    safe_print("")


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        safe_print("\n  ⏹ متوقف شد")


if __name__ == "__main__":
    main()

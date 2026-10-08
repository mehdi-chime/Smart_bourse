# install_groq_setup.py
# راه‌اندازی Groq + Fallback خودکار
# اجرا: python install_groq_setup.py

import os
import sys
import re
import json
import shutil
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
CONFIG_FILE = PROJECT_ROOT / "config" / "llm_config.py"
AI_FILE = PROJECT_ROOT / "ai" / "llm_analyzer.py"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  🚀 راه‌اندازی Groq + Fallback")
    safe_print("=" * 70)
    safe_print("")

    # ===== قدم ۱: چک فایل‌ها =====
    if not CONFIG_FILE.exists():
        safe_print(f"❌ {CONFIG_FILE} پیدا نشد!")
        input("Enter...")
        return
    if not AI_FILE.exists():
        safe_print(f"❌ {AI_FILE} پیدا نشد!")
        input("Enter...")
        return
    safe_print("✅ فایل‌ها پیدا شدن")
    safe_print("")

    # ===== قدم ۲: بکاپ =====
    safe_print("[1] بکاپ گرفتن...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_ROOT / "backup" / "groq_setup"
    backup_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(CONFIG_FILE, backup_dir / f"llm_config_{timestamp}.py")
    shutil.copy2(AI_FILE, backup_dir / f"llm_analyzer_{timestamp}.py")
    safe_print(f"   ✅ بکاپ در: {backup_dir.name}")
    safe_print("")

    # ===== قدم ۳: گرفتن کلید Groq =====
    safe_print("=" * 70)
    safe_print("  🔑 کلید Groq رو وارد کن")
    safe_print("=" * 70)
    safe_print("")
    safe_print("  📌 برو به: https://console.groq.com/keys")
    safe_print("  📌 ثبت‌نام کن (رایگان، بدون کارت)")
    safe_print("  📌 API Key بگیر (با gsk_ شروع می‌شه)")
    safe_print("")
    safe_print("  👇 کلید رو اینجا پیست کن (راست‌کلیک یا Ctrl+V):")
    safe_print("")

    groq_key = ""
    while not groq_key:
        try:
            groq_key = input("  🔑 Groq API Key: ").strip()
        except (EOFError, KeyboardInterrupt):
            safe_print("\n❌ لغو شد.")
            return

        if not groq_key:
            safe_print("  ⚠️  خالیه! دوباره...")
            continue

        # اگه خواست skip کنه
        if groq_key.lower() in ["skip", "no", "n", "-"]:
            safe_print("  ⏭️  رد شد (فقط Fallback)")
            groq_key = ""
            break

        if not groq_key.startswith("gsk_"):
            safe_print(f"  ⚠️  کلید با gsk_ شروع نمی‌شه! مطمئنی؟")
            confirm = input("  ادامه؟ (y/n/skip): ").strip().lower()
            if confirm == "skip":
                groq_key = ""
                break
            if confirm != "y":
                groq_key = ""
                continue

        if len(groq_key) < 20:
            safe_print(f"  ⚠️  کلید کوتاهه ({len(groq_key)})! مطمئنی؟")
            confirm = input("  ادامه؟ (y/n): ").strip().lower()
            if confirm != "y":
                groq_key = ""
                continue

    if groq_key:
        safe_print("")
        safe_print(f"  ✅ کلید Groq دریافت شد ({len(groq_key)} کاراکتر)")
        safe_print(f"  📌 شروع: {groq_key[:10]}...")
    else:
        safe_print("  ⏭️  Groq رد شد. فقط Fallback استفاده می‌شه.")
    safe_print("")

    # ===== قدم ۴: آپدیت llm_config.py =====
    safe_print("[2] آپدیت llm_config.py...")

    config_content = CONFIG_FILE.read_text(encoding="utf-8")

    # حذف تنظیمات قبلی Groq (اگه بود)
    config_content = re.sub(
        r'\n# ===== Groq =====.*?(?=\n# =====|\Z)',
        '',
        config_content,
        flags=re.DOTALL
    )

    # اضافه کردن Groq
    groq_config = f"""

# ===== Groq (رایگان) =====
GROQ_API_KEY = "{groq_key}" if "{groq_key}" else ""
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "llama-3.3-70b-versatile"

# ===== LLM Mode =====
# auto: اول Groq، بعد DeepSeek
# groq: فقط Groq
# deepseek: فقط DeepSeek
# fallback: بدون LLM
LLM_MODE = "auto"
"""

    # اگه GROQ قبلاً نبود، اضافه کن
    if "GROQ_API_KEY" not in config_content:
        config_content += groq_config
    else:
        # آپدیت کن
        config_content = re.sub(
            r'GROQ_API_KEY\s*=\s*.+',
            f'GROQ_API_KEY = "{groq_key}"',
            config_content
        )

    CONFIG_FILE.write_text(config_content, encoding="utf-8")
    safe_print(f"   ✅ llm_config.py آپدیت شد")
    safe_print("")

    # ===== قدم ۵: آپدیت llm_analyzer.py =====
    safe_print("[3] آپدیت llm_analyzer.py...")

    # نسخه‌ی جدید llm_analyzer با پشتیبانی Groq + Fallback
    new_analyzer = '''# ai/llm_analyzer.py
# تحلیل‌گر LLM v2 — با Groq + Fallback
# اجرا: python ai/llm_analyzer.py

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(r"F:\\python\\har roz ba python\\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))

# ===== config =====
try:
    from config.llm_config import (
        DEEPSEEK_API_KEY,
        GROQ_API_KEY,
        GROQ_BASE_URL,
        GROQ_MODEL,
        LLM_MODEL,
        LLM_BASE_URL,
        LLM_MODE,
        LLM_TEMPERATURE,
        LLM_MAX_TOKENS,
        SYSTEM_PROMPT,
    )
    CONFIG_OK = True
except ImportError as e:
    logger.warning(f"Config error: {e}")
    CONFIG_OK = False
    LLM_MODE = "fallback"


class LLMAnalyzer:
    """تحلیل‌گر LLM با Groq + DeepSeek + Fallback"""

    def __init__(self):
        self.client = None
        self.mode = "fallback"
        self.backend = None

        if not CONFIG_OK:
            logger.warning("Config not loaded — Fallback mode")
            return

        # ۱. Groq
        if GROQ_API_KEY and GROQ_API_KEY.startswith("gsk_"):
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url=GROQ_BASE_URL
                )
                self.mode = "groq"
                self.backend = "Groq"
                self.model = GROQ_MODEL
                logger.info(f"✅ Groq ready ({GROQ_MODEL})")
                return
            except Exception as e:
                logger.error(f"Groq init error: {e}")

        # ۲. DeepSeek
        if DEEPSEEK_API_KEY and DEEPSEEK_API_KEY.startswith("sk-"):
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=DEEPSEEK_API_KEY,
                    base_url=LLM_BASE_URL
                )
                self.mode = "deepseek"
                self.backend = "DeepSeek"
                self.model = LLM_MODEL
                logger.info(f"✅ DeepSeek ready")
                return
            except Exception as e:
                logger.error(f"DeepSeek init error: {e}")

        # ۳. Fallback
        logger.warning("⚠️  No LLM available — Fallback mode")
        self.mode = "fallback"

    def _call_llm(self, user_prompt, system_prompt=None):
        """فراخوانی LLM"""
        if not self.client:
            return None
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            return None

    def _fallback_news(self, news_text):
        """Fallback — تحلیل ساده خبر"""
        try:
            from news.news_sentiment import NewsSentiment
            ns = NewsSentiment()
            result = ns.analyze_text(news_text)
            return json.dumps({
                "sentiment": "negative" if result["score"] < 0 else "positive" if result["score"] > 0 else "neutral",
                "impact": result["score"],
                "symbols": result.get("symbols", []),
                "advice": "تحلیل با Fallback (بدون LLM)",
                "mode": "fallback"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "mode": "fallback"
            }, ensure_ascii=False)

    def analyze_news(self, news_text):
        """تحلیل خبر"""
        if self.mode == "fallback":
            return self._fallback_news(news_text)

        prompt = f"""این خبر بورسی رو تحلیل کن:

{news_text}

خروجی JSON:
{{
  "sentiment": "positive/negative/neutral",
  "impact": -10 to +10,
  "symbols": ["نمادهای تأثیرپذیر"],
  "advice": "توصیه کوتاه فارسی"
}}"""
        result = self._call_llm(prompt)
        if result is None:
            return self._fallback_news(news_text)
        return result

    def advise_stock(self, symbol, rsi, pe, change_pct):
        """مشاوره سهم"""
        if self.mode == "fallback":
            return f"سهم {symbol}: RSI={rsi}, P/E={pe}, تغییر={change_pct}% (بدون LLM)"

        prompt = f"""این سهم رو تحلیل کن:

نماد: {symbol}
RSI: {rsi}
P/E: {pe}
تغییر: {change_pct}%

۲-۳ خط توصیه به فارسی."""
        result = self._call_llm(prompt)
        if result is None:
            return f"سهم {symbol}: RSI={rsi}, P/E={pe} (بدون LLM)"
        return result


# ===== تست =====
if __name__ == "__main__":
    analyzer = LLMAnalyzer()
    print(f"Mode: {analyzer.mode}")
    print(f"Backend: {analyzer.backend}")
    print()
    print("=" * 60)

    result = analyzer.analyze_news("تحریم جدید خودروسازی اعمال شد")
    print(f"Result:\n{result}")
'''

    AI_FILE.write_text(new_analyzer, encoding="utf-8")
    safe_print(f"   ✅ llm_analyzer.py آپدیت شد")
    safe_print("")

    # ===== قدم ۶: تست =====
    safe_print("=" * 70)
    safe_print("  🧪 تست")
    safe_print("=" * 70)
    safe_print("")

    result = os.popen(f'{sys.executable} "{AI_FILE}"').read()
    safe_print(result)

    # ===== قدم ۷: نتیجه =====
    safe_print("=" * 70)
    safe_print("  🎉 تمام!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📋 نتیجه:")
    if groq_key:
        safe_print("   • Groq: ✅ فعال")
    else:
        safe_print("   • Groq: ⏭️  رد شد")
    safe_print(f"   • حالت: {LLM_MODE}")
    safe_print(f"   • بکاپ در: {backup_dir}")
    safe_print("")

    input("  Enter...")


if __name__ == "__main__":
    main()

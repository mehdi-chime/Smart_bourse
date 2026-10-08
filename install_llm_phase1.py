# install_llm_phase1.py
# فاز ۱: LLM Integration
# اجرا: python install_llm_phase1.py

import os
import sys
import json
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
AI_DIR = PROJECT_ROOT / "ai"
NEWS_DIR = PROJECT_ROOT / "news"
CONFIG_DIR = PROJECT_ROOT / "config"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 70)
    safe_print("  🧠 فاز ۱: LLM Integration")
    safe_print("=" * 70)
    safe_print("")

    # ===== قدم ۱: نصب کتابخانه‌ها =====
    safe_print("[1] نصب کتابخانه‌ها...")
    os.system(f'{sys.executable} -m pip install openai httpx --quiet')
    safe_print("   OK: openai + httpx")
    safe_print("")

    # ===== قدم ۲: ساخت پوشه config =====
    safe_print("[2] ساخت پوشه config...")
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    safe_print("   OK: " + str(CONFIG_DIR))
    safe_print("")

    # ===== قدم ۳: ساخت config/llm_config.py =====
    safe_print("[3] ساخت config/llm_config.py...")

    config_lines = []
    config_lines.append("# config/llm_config.py")
    config_lines.append("# تنظیمات LLM")
    config_lines.append("")
    config_lines.append("# ===== DeepSeek API =====")
    config_lines.append("# کلیدت رو از https://platform.deepseek.com بگیر")
    config_lines.append("DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')")
    config_lines.append("")
    config_lines.append("# ===== مدل =====")
    config_lines.append("LLM_MODEL = 'deepseek-chat'")
    config_lines.append("LLM_BASE_URL = 'https://api.deepseek.com'")
    config_lines.append("")
    config_lines.append("# ===== تنظیمات =====")
    config_lines.append("LLM_TEMPERATURE = 0.3")
    config_lines.append("LLM_MAX_TOKENS = 500")
    config_lines.append("LLM_TIMEOUT = 30")
    config_lines.append("")
    config_lines.append("# ===== سیستم پرامپت =====")
    config_lines.append("SYSTEM_PROMPT = '''تو یه تحلیل‌گر بورس ایران هستی.")
    config_lines.append("وظیفه‌ت: تحلیل خبر، پیشنهاد خرید/فروش، هشدار ریسک.")
    config_lines.append("جواب‌هات کوتاه، دقیق، به فارسی.'''")
    config_lines.append("")

    config_file = CONFIG_DIR / "llm_config.py"
    # اصلاح: os باید import بشه
    config_content = "import os\n\n" + "\n".join(config_lines)
    config_file.write_text(config_content, encoding="utf-8")
    safe_print("   OK: " + str(config_file))
    safe_print("")

    # ===== قدم ۴: ساخت config/__init__.py =====
    init_file = CONFIG_DIR / "__init__.py"
    init_file.write_text("# config package\n", encoding="utf-8")
    safe_print("   OK: " + str(init_file))
    safe_print("")

    # ===== قدم ۵: ساخت ai/llm_analyzer.py =====
    safe_print("[5] ساخت ai/llm_analyzer.py...")

    analyzer_lines = []
    analyzer_lines.append("# ai/llm_analyzer.py")
    analyzer_lines.append("# تحلیل‌گر LLM")
    analyzer_lines.append("")
    analyzer_lines.append("import sys")
    analyzer_lines.append("import json")
    analyzer_lines.append("import logging")
    analyzer_lines.append("from pathlib import Path")
    analyzer_lines.append("from datetime import datetime")
    analyzer_lines.append("")
    analyzer_lines.append("logging.basicConfig(")
    analyzer_lines.append("    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',")
    analyzer_lines.append("    level=logging.INFO")
    analyzer_lines.append(")")
    analyzer_lines.append("logger = logging.getLogger(__name__)")
    analyzer_lines.append("")
    analyzer_lines.append("PROJECT_ROOT = Path(r'F:\\python\\har roz ba python\\smart_bours')")
    analyzer_lines.append("sys.path.insert(0, str(PROJECT_ROOT))")
    analyzer_lines.append("")
    analyzer_lines.append("try:")
    analyzer_lines.append("    from config.llm_config import (")
    analyzer_lines.append("        DEEPSEEK_API_KEY, LLM_MODEL, LLM_BASE_URL,")
    analyzer_lines.append("        LLM_TEMPERATURE, LLM_MAX_TOKENS, SYSTEM_PROMPT")
    analyzer_lines.append("    )")
    analyzer_lines.append("    LLM_AVAILABLE = True")
    analyzer_lines.append("except ImportError as e:")
    analyzer_lines.append("    logger.warning(f'LLM config not found: {e}')")
    analyzer_lines.append("    LLM_AVAILABLE = False")
    analyzer_lines.append("")
    analyzer_lines.append("")
    analyzer_lines.append("class LLMAnalyzer:")
    analyzer_lines.append("    '''تحلیل‌گر LLM'''")
    analyzer_lines.append("")
    analyzer_lines.append("    def __init__(self):")
    analyzer_lines.append("        self.client = None")
    analyzer_lines.append("        self.available = False")
    analyzer_lines.append("        if LLM_AVAILABLE and DEEPSEEK_API_KEY:")
    analyzer_lines.append("            try:")
    analyzer_lines.append("                from openai import OpenAI")
    analyzer_lines.append("                self.client = OpenAI(")
    analyzer_lines.append("                    api_key=DEEPSEEK_API_KEY,")
    analyzer_lines.append("                    base_url=LLM_BASE_URL")
    analyzer_lines.append("                )")
    analyzer_lines.append("                self.available = True")
    analyzer_lines.append("                logger.info('LLM client ready')")
    analyzer_lines.append("            except Exception as e:")
    analyzer_lines.append("                logger.error(f'LLM init error: {e}')")
    analyzer_lines.append("")
    analyzer_lines.append("    def _call(self, user_prompt, system_prompt=None):")
    analyzer_lines.append("        '''فراخوانی LLM'''")
    analyzer_lines.append("        if not self.available:")
    analyzer_lines.append("            return None")
    analyzer_lines.append("        try:")
    analyzer_lines.append("            response = self.client.chat.completions.create(")
    analyzer_lines.append("                model=LLM_MODEL,")
    analyzer_lines.append("                messages=[")
    analyzer_lines.append("                    {'role': 'system', 'content': system_prompt or SYSTEM_PROMPT},")
    analyzer_lines.append("                    {'role': 'user', 'content': user_prompt}")
    analyzer_lines.append("                ],")
    analyzer_lines.append("                temperature=LLM_TEMPERATURE,")
    analyzer_lines.append("                max_tokens=LLM_MAX_TOKENS")
    analyzer_lines.append("            )")
    analyzer_lines.append("            return response.choices[0].message.content")
    analyzer_lines.append("        except Exception as e:")
    analyzer_lines.append("            logger.error(f'LLM call error: {e}')")
    analyzer_lines.append("            return None")
    analyzer_lines.append("")
    analyzer_lines.append("    def analyze_news(self, news_text):")
    analyzer_lines.append("        '''تحلیل خبر'''")
    analyzer_lines.append("        prompt = f'''این خبر رو تحلیل کن:")
    analyzer_lines.append("")
    analyzer_lines.append("{news_text}")
    analyzer_lines.append("")
    analyzer_lines.append("خروجی JSON:")
    analyzer_lines.append("{{")
    analyzer_lines.append('  \"sentiment\": \"positive/negative/neutral\",')
    analyzer_lines.append('  \"impact\": -10 to +10,')
    analyzer_lines.append('  \"symbols\": [\"سهم‌های تأثیرپذیر\"],')
    analyzer_lines.append('  \"advice\": \"توصیه کوتاه\"')
    analyzer_lines.append("}}'''")
    analyzer_lines.append("        return self._call(prompt)")
    analyzer_lines.append("")
    analyzer_lines.append("    def advise_stock(self, symbol, rsi, pe, change_pct):")
    analyzer_lines.append("        '''مشاوره سهم'''")
    analyzer_lines.append("        prompt = f'''این سهم رو تحلیل کن:")
    analyzer_lines.append("")
    analyzer_lines.append("نماد: {symbol}")
    analyzer_lines.append("RSI: {rsi}")
    analyzer_lines.append("P/E: {pe}")
    analyzer_lines.append("تغییر: {change_pct}%")
    analyzer_lines.append("")
    analyzer_lines.append("خروجی: ۲-۳ خط توصیه به فارسی.'''")
    analyzer_lines.append("        return self._call(prompt)")
    analyzer_lines.append("")
    analyzer_lines.append("")
    analyzer_lines.append("if __name__ == '__main__':")
    analyzer_lines.append("    analyzer = LLMAnalyzer()")
    analyzer_lines.append("    print('LLM Available:', analyzer.available)")
    analyzer_lines.append("    if analyzer.available:")
    analyzer_lines.append("        result = analyzer.analyze_news('تحریم جدید خودروسازی اعمال شد')")
    analyzer_lines.append("        print('Result:', result)")
    analyzer_lines.append("    else:")
    analyzer_lines.append("        print('API Key not set!')")

    analyzer_file = AI_DIR / "llm_analyzer.py"
    analyzer_file.write_text("\n".join(analyzer_lines), encoding="utf-8")
    safe_print("   OK: " + str(analyzer_file))
    safe_print("")

    # ===== قدم ۶: چک نهایی =====
    safe_print("=" * 70)
    safe_print("  چک نهایی")
    safe_print("=" * 70)
    safe_print("")

    files_to_check = [
        CONFIG_DIR / "llm_config.py",
        CONFIG_DIR / "__init__.py",
        AI_DIR / "llm_analyzer.py",
    ]

    for f in files_to_check:
        if f.exists():
            size = f.stat().st_size
            safe_print(f"   OK: {f.name} ({size:,} bytes)")
        else:
            safe_print(f"   MISSING: {f.name}")

    safe_print("")
    safe_print("=" * 70)
    safe_print("  فاز ۱.۱ و ۱.۲ تمام شد!")
    safe_print("=" * 70)
    safe_print("")
    safe_print("📋 قدم بعدی:")
    safe_print("")
    safe_print("۱. برو به https://platform.deepseek.com")
    safe_print("۲. ثبت‌نام کن")
    safe_print("۳. API Key بگیر")
    safe_print("۴. کلید رو توی این فایل بذار:")
    safe_print("   " + str(CONFIG_DIR / "llm_config.py"))
    safe_print("")
    safe_print("یا کلید رو به عنوان env variable بذار:")
    safe_print("   set DEEPSEEK_API_KEY=sk-xxxxx")
    safe_print("")
    safe_print("۵. تست کن:")
    safe_print("   python ai\\llm_analyzer.py")
    safe_print("")


if __name__ == "__main__":
    main()

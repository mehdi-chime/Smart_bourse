# install_final_docs.py
# فاز ۱۲: مستندات نهایی
# اجرا: python install_final_docs.py

import os
import sys
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
DOCS_DIR = PROJECT_ROOT / "docs"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


# ═══════════════════════════════════════════════════════════
# docs/AI.md
# ═══════════════════════════════════════════════════════════

DOCS_AI_LINES = [
    "# 🤖 مستندات AI",
    "",
    "## 📁 ساختار",
    "",
    "| فایل | کار |",
    "|:---|:---|",
    "| `ai_engine.py` | موتور اصلی (advise, check_outcomes) |",
    "| `memory.py` | حافظه (JSONL) |",
    "| `learner.py` | یادگیری (تنظیم وزن) |",
    "| `ml_model.py` | مدل ML (RandomForest) |",
    "| `trainer.py` | آموزش |",
    "| `ml_model_xgb.py` | مدل XGBoost (اختیاری) |",
    "",
    "## 🔄 چرخه",
    "",
    "1. جمع‌آوری داده",
    "2. تحلیل (`advise`)",
    "3. ثبت سیگنال (`memory.save_signal`)",
    "4. انتظار (1-7 روز)",
    "5. چک نتیجه (`check_outcomes`)",
    "6. یادگیری (`learner.adjust_weights`)",
    "7. تنظیم وزن‌ها",
    "8. ML training (`trainer`)",
    "9. سیگنال بهتر",
    "",
    "## 🎯 فرمول امتیاز",
    "",
    "```",
    "final_score =",
    "    0.6 * ml_score +",
    "    0.4 * (",
    "        money_flow * mf_score +",
    "        technical * tech_score +",
    "        context * context_score",
    "    )",
    "```",
    "",
    "## 📊 وزن‌ها",
    "",
    "| وزن | مقدار پیش‌فرض |",
    "|:---|:---:|",
    "| money_flow | 0.40 |",
    "| technical | 0.35 |",
    "| context | 0.25 |",
    "",
    "## 🧠 ML Model",
    "",
    "- **الگوریتم:** RandomForest",
    "- **ویژگی‌ها:** 6 (ratio, rsi, tech_score, weight_score, price, market_pct)",
    "- **آموزش:** از `outcomes.jsonl`",
    "- **ذخیره:** `data/ai/ml_model.pkl`",
    "",
    "## 📌 استفاده",
    "",
    "```python",
    "from ai_integration import get_ai_advice",
    "",
    "result = get_ai_advice(",
    "    symbol='خگستر',",
    "    category='SAFE_BUY',",
    "    ratio=5.0,",
    "    rsi=25,",
    "    last_price=10000,",
    ")",
    "```",
]


# ═══════════════════════════════════════════════════════════
# docs/INSTALL.md
# ═══════════════════════════════════════════════════════════

DOCS_INSTALL_LINES = [
    "# 📦 نصب Smart_Bourse",
    "",
    "## پیش‌نیازها",
    "",
    "- Python 3.10+",
    "- pip",
    "",
    "## نصب",
    "",
    "```bash",
    "pip install -r requirements.txt",
    "```",
    "",
    "## اجرا",
    "",
    "```bash",
    "# منوی اصلی",
    "python smart_bourse_v10.py",
    "",
    "# اسکنر",
    "python smart_scanner_v8.py",
    "",
    "# حالت مدرسه",
    "python school_mode_v7.py",
    "",
    "# بررسی شبانه",
    "python night_check.py",
    "",
    "# AI",
    "python daily_ai_runner.py",
    "",
    "# داشبورد",
    "python build_dashboard.py",
    "",
    "# بک‌تست",
    "python backtest_v2.py",
    "```",
    "",
    "## تست",
    "",
    "```bash",
    "pytest tests/ -v",
    "pytest tests/ --cov=. --cov-report=html",
    "```",
]


# ═══════════════════════════════════════════════════════════
# docs/STRUCTURE.md
# ═══════════════════════════════════════════════════════════

DOCS_STRUCTURE_LINES = [
    "# 📁 ساختار پروژه",
    "",
    "```",
    "smart_bours/",
    "├── ai/                    # AI",
    "│   ├── ai_engine.py",
    "│   ├── memory.py",
    "│   ├── learner.py",
    "│   ├── ml_model.py",
    "│   ├── trainer.py",
    "│   └── ml_model_xgb.py",
    "├── analysis/              # تحلیل",
    "├── backtest/              # بک‌تست",
    "├── charts/                # نمودار",
    "├── core/                  # هسته",
    "├── data/                  # داده‌ها",
    "│   ├── ai/",
    "│   ├── history/",
    "│   ├── hunter/",
    "│   └── smart_bourse_v2.db",
    "├── database/              # دیتابیس",
    "├── docs/                  # مستندات",
    "├── engines/               # موتورها",
    "├── indicators/            # اندیکاتورها",
    "├── market/                # بازار",
    "├── portfolio/             # پرتفوی",
    "├── reports/               # گزارش‌ها",
    "├── risk/                  # ریسک",
    "├── scanner/               # اسکنرها",
    "├── strategy/              # استراتژی",
    "├── tests/                 # تست‌ها",
    "├── utils/                 # ابزار",
    "├── README.md",
    "├── CHANGELOG.md",
    "├── requirements.txt",
    "├── PROJECT_MEMORY.md",
    "├── ROADMAP_5.md",
    "└── ...",
    "```",
]


def write_file(path, lines):
    content = "\n".join(lines)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📚 فاز ۱۲: مستندات نهایی")
    safe_print("=" * 80)
    safe_print("")

    # ۱. AI.md
    safe_print("  📄 ساخت docs/AI.md...")
    size = write_file(DOCS_DIR / "AI.md", DOCS_AI_LINES)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۲. INSTALL.md
    safe_print("  📄 ساخت docs/INSTALL.md...")
    size = write_file(DOCS_DIR / "INSTALL.md", DOCS_INSTALL_LINES)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۳. STRUCTURE.md
    safe_print("  📄 ساخت docs/STRUCTURE.md...")
    size = write_file(DOCS_DIR / "STRUCTURE.md", DOCS_STRUCTURE_LINES)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۴. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ docs/AI.md")
    safe_print("  ✅ docs/INSTALL.md")
    safe_print("  ✅ docs/STRUCTURE.md")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()

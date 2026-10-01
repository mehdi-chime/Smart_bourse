# build_dashboard.py
# ساخت مستقیم داشبورد
# اجرا: python build_dashboard.py

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
sys.path.insert(0, str(PROJECT_ROOT))


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 ساخت داشبورد")
    safe_print("=" * 80)
    safe_print("")

    # ۱. بارگذاری AI
    safe_print("  🤖 بارگذاری AI...")
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        insight = engine.get_insight()
        safe_print("     ✅ AI")
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        insight = {"memory": {}, "weights": {}, "category_stats": {}}

    # ۲. بارگذاری سیگنال‌ها
    safe_print("  📊 بارگذاری سیگنال‌ها...")
    try:
        from ai.memory import AIMemory
        memory = AIMemory()
        signals = memory.load_signals()
        safe_print(f"     ✅ {len(signals)} سیگنال")
    except Exception as e:
        safe_print(f"     ❌ خطا: {e}")
        signals = []

    # ۳. آمار
    memory_stats = insight.get("memory", {})
    weights = insight.get("weights", {})
    total_signals = memory_stats.get("total_signals", 0)
    checked = memory_stats.get("total_outcomes", 0)
    success = memory_stats.get("success_count", 0)
    failed = memory_stats.get("failure_count", 0)
    pending = memory_stats.get("pending", 0)
    success_rate = round(success / checked * 100, 1) if checked > 0 else 0

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ۴. ساخت HTML
    safe_print("  📄 ساخت HTML...")

    weights_rows = ""
    for k, v in weights.items():
        weights_rows += f"<tr><td>{k}</td><td>{round(v, 3)}</td></tr>\n"

    signals_rows = ""
    for s in signals[-20:]:
        signals_rows += f"<tr><td>{s.get('date', '')}</td><td>{s.get('symbol', '')}</td><td>{s.get('category', '')}</td><td>{s.get('rsi', '')}</td><td>{s.get('ratio', '')}</td></tr>\n"

    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Smart_Bourse Dashboard</title>
<style>
body {{ font-family: Tahoma, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
h1 {{ color: #00d4ff; }}
h2 {{ color: #00d4ff; border-bottom: 2px solid #0f3460; padding-bottom: 10px; }}
.stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
.stat {{ background: #16213e; padding: 20px; border-radius: 8px; border-left: 4px solid #00d4ff; }}
.stat-value {{ font-size: 2em; color: #00d4ff; font-weight: bold; }}
.stat-label {{ color: #888; margin-top: 5px; }}
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
th {{ background: #0f3460; padding: 12px; text-align: right; }}
td {{ padding: 10px; border-bottom: 1px solid #333; }}
tr:hover {{ background: #16213e; }}
.section {{ background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }}
.footer {{ text-align: center; color: #666; margin-top: 30px; }}
</style>
</head>
<body>
<h1>🎯 Smart_Bourse Dashboard</h1>
<p>آخرین آپدیت: {now}</p>

<div class="section">
<h2>📊 آمار AI</h2>
<div class="stats">
<div class="stat"><div class="stat-value">{total_signals}</div><div class="stat-label">کل سیگنال‌ها</div></div>
<div class="stat"><div class="stat-value">{checked}</div><div class="stat-label">چک شده</div></div>
<div class="stat"><div class="stat-value">{success}</div><div class="stat-label">موفق</div></div>
<div class="stat"><div class="stat-value">{failed}</div><div class="stat-label">ناموفق</div></div>
<div class="stat"><div class="stat-value">{pending}</div><div class="stat-label">در انتظار</div></div>
<div class="stat"><div class="stat-value">{success_rate}%</div><div class="stat-label">نرخ موفقیت</div></div>
</div>
</div>

<div class="section">
<h2>⚖️ وزن‌های AI</h2>
<table>
<tr><th>وزن</th><th>مقدار</th></tr>
{weights_rows}
</table>
</div>

<div class="section">
<h2>📋 آخرین سیگنال‌ها</h2>
<table>
<tr><th>تاریخ</th><th>نماد</th><th>دسته</th><th>RSI</th><th>نسبت</th></tr>
{signals_rows}
</table>
</div>

<div class="footer">
<p>Smart_Bourse v3.0 — AI با ML</p>
</div>

</body>
</html>"""

    # ۵. ذخیره
    output = PROJECT_ROOT / "reports" / "dashboard_v2.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")

    safe_print(f"     ✅ {output}")
    safe_print(f"     📏 {len(html):,} کاراکتر")
    safe_print("")

    # ۶. باز کردن در مرورگر
    safe_print("  🌐 باز کردن در مرورگر...")
    import webbrowser
    webbrowser.open(f"file:///{output.as_posix()}")
    safe_print("     ✅ باز شد")
    safe_print("")

    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()

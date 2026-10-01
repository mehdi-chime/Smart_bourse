# install_dashboard.py
# فاز ۸: داشبورد HTML
# اجرا: python install_dashboard.py

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


# ═══════════════════════════════════════════════════════════
# dashboard_builder_v2.py
# ═══════════════════════════════════════════════════════════

DASHBOARD = '''"""
Project : Smart_Bourse
File    : dashboard_builder_v2.py
Version : 1.0.0

Description :
    ساخت داشبورد HTML با AI
"""

import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_ai_insight():
    """بارگذاری بینش AI"""
    try:
        from ai.ai_engine import AIEngine
        engine = AIEngine()
        return engine.get_insight()
    except Exception as e:
        return {"error": str(e)}


def load_signals():
    """بارگذاری سیگنال‌ها"""
    try:
        from ai.memory import AIMemory
        memory = AIMemory()
        signals = memory.load_signals()
        return signals[-20:]
    except Exception:
        return []


def build_html(insight, signals):
    """ساخت HTML"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Smart_Bourse Dashboard</title>
<style>
body {{ font-family: Tahoma, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
h1 {{ color: #00d4ff; }}
.stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
.stat {{ background: #16213e; padding: 15px; border-radius: 8px; border-left: 4px solid #00d4ff; }}
.stat-value {{ font-size: 2em; color: #00d4ff; }}
.stat-label {{ color: #888; }}
table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
th {{ background: #0f3460; padding: 10px; text-align: right; }}
td {{ padding: 8px; border-bottom: 1px solid #333; }}
tr:hover {{ background: #16213e; }}
.success {{ color: #4ade80; }}
.fail {{ color: #f87171; }}
.section {{ background: #16213e; padding: 20px; border-radius: 8px; margin: 20px 0; }}
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

</body>
</html>"""
    
    # آمار
    memory = insight.get("memory", {})
    total_signals = memory.get("total_signals", 0)
    checked = memory.get("total_outcomes", 0)
    success = memory.get("success_count", 0)
    failed = memory.get("failure_count", 0)
    pending = memory.get("pending", 0)
    
    success_rate = round(success / checked * 100, 1) if checked > 0 else 0
    
    # وزن‌ها
    weights = insight.get("weights", {})
    weights_rows = "\\n".join([
        f"<tr><td>{k}</td><td>{round(v, 3)}</td></tr>"
        for k, v in weights.items()
    ])
    
    # سیگنال‌ها
    signals_rows = "\\n".join([
        f"<tr><td>{s.get('date', '')}</td><td>{s.get('symbol', '')}</td>"
        f"<td>{s.get('category', '')}</td><td>{s.get('rsi', '')}</td>"
        f"<td>{s.get('ratio', '')}</td></tr>"
        for s in signals[-20:]
    ])
    
    return html.format(
        now=now,
        total_signals=total_signals,
        checked=checked,
        success=success,
        failed=failed,
        pending=pending,
        success_rate=success_rate,
        weights_rows=weights_rows,
        signals_rows=signals_rows,
    )


def main():
    print()
    print("=" * 80)
    print("  📊 ساخت داشبورد HTML")
    print("=" * 80)
    print()
    
    insight = load_ai_insight()
    signals = load_signals()
    
    html = build_html(insight, signals)
    
    # ذخیره
    output = PROJECT_ROOT / "reports" / "dashboard_v2.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    
    print(f"  ✅ ذخیره: {output}")
    print(f"  📏 حجم: {len(html):,} کاراکتر")
    print()
    print("=" * 80)
    print("  ✅ تمام!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
'''


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 فاز ۸: داشبورد")
    safe_print("=" * 80)
    safe_print("")

    # ۱. ساخت dashboard
    safe_print("  📄 ساخت dashboard_builder_v2.py...")
    size = write_file(PROJECT_ROOT / "dashboard_builder_v2.py", DASHBOARD)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۲. تست
    safe_print("  🧪 تست dashboard...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "dashboard_builder_v2.py")],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        encoding="utf-8",
        errors="ignore",
    )
    
    for line in result.stdout.split("\\n")[-10:]:
        if line.strip():
            safe_print(f"     {line}")
    safe_print("")

    # ۳. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ dashboard_builder_v2.py")
    safe_print("  ✅ reports/dashboard_v2.html")
    safe_print("")
    safe_print("  🎯 دستور:")
    safe_print("     python dashboard_builder_v2.py")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()

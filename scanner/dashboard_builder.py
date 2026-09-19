"""
Project : Smart_Bourse
File    : scanner/dashboard_builder.py
Version : 1.0.0
Description :
    ساخت داشبورد HTML یکپارچه از تمام خروجی‌ها
"""

import json
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


DATA_DIR = PROJECT_ROOT / "data"
REAL_FLOW_DIR = DATA_DIR / "real_flow"
REPORTS_DIR = PROJECT_ROOT / "reports"


# ======================================================================
# HTML Template
# ======================================================================

HTML_HEAD = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smart Bourse — داشبورد</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Tahoma', 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    min-height: 100vh;
    padding: 20px;
    color: #fff;
}
.container { max-width: 1400px; margin: 0 auto; }

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 35px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.header h1 { font-size: 32px; margin-bottom: 10px; }
.header .meta { font-size: 14px; opacity: 0.9; margin-top: 8px; }

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 18px;
    margin-bottom: 25px;
}
.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 16px;
    padding: 25px;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.3);
}
.card .num { font-size: 42px; font-weight: bold; margin-bottom: 8px; }
.card .label { font-size: 14px; opacity: 0.85; }
.card.buy { background: linear-gradient(135deg, rgba(17,153,142,0.4), rgba(56,239,125,0.3)); }
.card.sell { background: linear-gradient(135deg, rgba(235,51,73,0.4), rgba(244,92,67,0.3)); }
.card.queue { background: linear-gradient(135deg, rgba(242,153,74,0.4), rgba(242,201,76,0.3)); }
.card.normal { background: linear-gradient(135deg, rgba(75,108,183,0.4), rgba(24,40,72,0.3)); }
.card.ai { background: linear-gradient(135deg, rgba(118,75,162,0.4), rgba(102,126,234,0.3)); }

.section {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 25px;
}
.section h2 {
    font-size: 22px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid rgba(255,255,255,0.15);
    display: flex;
    align-items: center;
    gap: 10px;
}

table { width: 100%; border-collapse: collapse; font-size: 14px; }
th {
    background: rgba(255,255,255,0.08);
    padding: 12px 10px;
    text-align: right;
    font-weight: 600;
    color: #b8c6db;
}
td { padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); }
tr:hover { background: rgba(255,255,255,0.05); }
.symbol { font-weight: bold; color: #fff; font-size: 15px; }

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
}
.badge-buy { background: rgba(56,239,125,0.25); color: #38ef7d; border: 1px solid #38ef7d; }
.badge-sell { background: rgba(244,92,67,0.25); color: #f45c43; border: 1px solid #f45c43; }
.badge-queue { background: rgba(242,201,76,0.25); color: #f2c94c; border: 1px solid #f2c94c; }
.badge-high { background: rgba(56,239,125,0.25); color: #38ef7d; }
.badge-med { background: rgba(242,201,76,0.25); color: #f2c94c; }
.badge-low { background: rgba(244,92,67,0.25); color: #f45c43; }

.advice {
    font-size: 13px;
    color: #b8c6db;
    margin-top: 5px;
    padding-right: 15px;
}

.empty { text-align: center; padding: 30px; color: #8898aa; font-style: italic; }

.footer {
    text-align: center;
    padding: 25px;
    color: #8898aa;
    font-size: 13px;
}

.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 25px;
}

@media (max-width: 900px) {
    .grid-2 { grid-template-columns: 1fr; }
    .header h1 { font-size: 24px; }
    .card .num { font-size: 32px; }
}

.progress-bar {
    height: 8px;
    background: rgba(255,255,255,0.1);
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
}
.progress-bar .fill {
    height: 100%;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 4px;
    transition: width 0.3s;
}
</style>
</head>
<body>
<div class="container">
"""


HTML_FOOT = """
<div class="footer">
    Smart Bourse © {year} — Mehdi Jalali
    <br>
    این داشبورد فقط برای کمک به تصمیم‌گیری است، نه جایگزین آن.
</div>

</div>
</body>
</html>
"""


# ======================================================================
# کلاس اصلی
# ======================================================================

class DashboardBuilder:

    def __init__(self):
        self.data_dir = REAL_FLOW_DIR
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------

    def find_latest(self, pattern):
        if not self.data_dir.exists():
            return None
        files = sorted(self.data_dir.glob(pattern), reverse=True)
        files = [f for f in files if "history" not in str(f)]
        return files[0] if files else None

    # ------------------------------------------------------------------

    def load_data(self):
        result = {"flow": None, "technical": None, "ai": None}

        # فیلتر جریان
        f = self.find_latest("real_flow_*.json")
        if f:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    result["flow"] = json.load(fp)
            except Exception:
                pass

        # تکنیکال
        t = self.find_latest("technical_*.json")
        if t:
            try:
                with open(t, "r", encoding="utf-8") as fp:
                    result["technical"] = json.load(fp)
            except Exception:
                pass

        # AI memory
        ai_dir = self.data_dir.parent / "ai"
        memory_file = ai_dir / "memory.jsonl"
        outcomes_file = ai_dir / "outcomes.jsonl"
        weights_file = ai_dir / "weights.json"

        ai_data = {"signals": [], "outcomes": [], "weights": {}}
        if memory_file.exists():
            with open(memory_file, "r", encoding="utf-8") as fp:
                for line in fp:
                    try:
                        ai_data["signals"].append(json.loads(line))
                    except Exception:
                        pass
        if outcomes_file.exists():
            with open(outcomes_file, "r", encoding="utf-8") as fp:
                for line in fp:
                    try:
                        ai_data["outcomes"].append(json.loads(line))
                    except Exception:
                        pass
        if weights_file.exists():
            try:
                with open(weights_file, "r", encoding="utf-8") as fp:
                    ai_data["weights"] = json.load(fp)
            except Exception:
                pass

        result["ai"] = ai_data
        return result

    # ------------------------------------------------------------------

    def _fmt(self, n):
        """فرمت عدد با کاما"""
        try:
            return "{:,}".format(int(n or 0))
        except Exception:
            return "0"

    def _fmt_b(self, n):
        """فرمت میلیارد"""
        try:
            return "{:.2f}".format(float(n or 0) / 1_000_000_000)
        except Exception:
            return "0.00"

    # ------------------------------------------------------------------

    def _build_advice_badge(self, score):
        if score >= 75:
            return '<span class="badge badge-high">' + str(round(score, 1)) + '</span>'
        elif score >= 55:
            return '<span class="badge badge-med">' + str(round(score, 1)) + '</span>'
        return '<span class="badge badge-low">' + str(round(score, 1)) + '</span>'

    def _build_rsi_badge(self, rsi):
        if rsi is None:
            return "-"
        if rsi >= 70:
            return '<span class="badge badge-low">' + str(round(rsi, 1)) + '</span>'
        elif rsi >= 30:
            return '<span class="badge badge-med">' + str(round(rsi, 1)) + '</span>'
        return '<span class="badge badge-high">' + str(round(rsi, 1)) + '</span>'

    # ------------------------------------------------------------------

    def build_flow_section(self, flow, tech_lookup):
        if not flow:
            return '<div class="section"><h2>📊 فیلتر جریان پول</h2><div class="empty">داده‌ای نیست</div></div>'

        summary = flow.get("summary", {})
        date = flow.get("date", "?")

        sections = []

        for cat, icon, title in [
            ("safe_buy", "🟢", "SAFE_BUY — سهام امن برای خرید"),
            ("queue_buy", "🟡", "QUEUE_BUY — صف خرید"),
            ("safe_sell", "🔴", "SAFE_SELL — سهام امن برای فروش"),
        ]:
            items = flow.get(cat, [])
            if not items:
                continue

            items = sorted(items, key=lambda x: x.get("ratio", 0) or 0, reverse=True)

            rows = []
            for it in items[:20]:
                symbol = it.get("Symbol") or it.get("symbol") or "?"
                tech = tech_lookup.get(symbol, {})
                rsi = tech.get("rsi")
                ratio = it.get("ratio", 0) or 0
                last = it.get("Last", 0) or 0
                value = it.get("Value", 0) or 0
                name = str(it.get("Name", ""))[:30]

                rows.append(
                    "<tr>"
                    "<td class=\"symbol\">" + str(symbol) + "</td>"
                    "<td>" + name + "</td>"
                    "<td>" + self._fmt(last) + "</td>"
                    "<td><span class=\"badge badge-" + ("buy" if cat == "safe_buy" else "queue" if cat == "queue_buy" else "sell") + "\">" + "{:.2f}".format(ratio) + "</span></td>"
                    "<td>" + self._build_rsi_badge(rsi) + "</td>"
                    "<td>" + self._fmt_b(value) + "</td>"
                    "</tr>"
                )

            sections.append(
                '<h3 style="margin: 20px 0 10px 0; color: #b8c6db; font-size: 16px;">' + icon + " " + title + " (" + str(len(items)) + ")</h3>"
                '<table>'
                '<thead><tr>'
                '<th>نماد</th><th>نام شرکت</th><th>قیمت</th>'
                '<th>نسبت</th><th>RSI</th><th>ارزش (میلیارد)</th>'
                '</tr></thead>'
                '<tbody>' + "".join(rows) + '</tbody>'
                '</table>'
            )

        return (
            '<div class="section">'
            '<h2>📊 فیلتر جریان پول حقیقی — ' + str(date) + '</h2>'
            + "".join(sections) +
            '</div>'
        )

    # ------------------------------------------------------------------

    def build_ai_section(self, ai):
        signals = ai.get("signals", [])
        outcomes = ai.get("outcomes", [])
        weights = ai.get("weights", {})

        success = sum(1 for o in outcomes if o.get("success"))
        fail = sum(1 for o in outcomes if o.get("success") is False)

        # آمار دسته‌ها
        cat_stats = {}
        for o in outcomes:
            cat = o.get("category", "UNKNOWN")
            if cat not in cat_stats:
                cat_stats[cat] = {"total": 0, "success": 0}
            cat_stats[cat]["total"] += 1
            if o.get("success"):
                cat_stats[cat]["success"] += 1

        rows = []
        for cat, s in cat_stats.items():
            rate = (s["success"] / s["total"] * 100) if s["total"] > 0 else 0
            rows.append(
                "<tr>"
                "<td>" + cat + "</td>"
                "<td>" + str(s["total"]) + "</td>"
                "<td>" + str(s["success"]) + "</td>"
                '<td><div class="progress-bar"><div class="fill" style="width: ' + "{:.0f}".format(rate) + '%;"></div></div>'
                '<small style="color: #b8c6db;">' + "{:.1f}".format(rate) + '%</small></td>'
                "</tr>"
            )

        weights_html = ""
        for k, v in weights.items():
            weights_html += (
                '<div style="display:flex; justify-content:space-between; margin: 8px 0;">'
                '<span>' + k + '</span>'
                '<span style="color: #38ef7d;">' + "{:.0f}".format(v * 100) + '%</span>'
                '</div>'
                '<div class="progress-bar"><div class="fill" style="width: ' + "{:.0f}".format(v * 100) + '%;"></div></div>'
            )

        return (
            '<div class="grid-2">'
            '<div class="section">'
            '<h2>🧠 حافظه AI</h2>'
            '<div class="card ai" style="margin-bottom: 15px;">'
            '<div class="num">' + str(len(signals)) + '</div>'
            '<div class="label">کل سیگنال‌ها</div>'
            '</div>'
            '<div style="display:grid; grid-template-columns:1fr 1fr; gap: 10px;">'
            '<div class="card ai" style="padding:15px;">'
            '<div class="num" style="font-size:28px; color:#38ef7d;">' + str(success) + '</div>'
            '<div class="label">✅ موفق</div>'
            '</div>'
            '<div class="card ai" style="padding:15px;">'
            '<div class="num" style="font-size:28px; color:#f45c43;">' + str(fail) + '</div>'
            '<div class="label">❌ ناموفق</div>'
            '</div>'
            '</div>'
            '<h3 style="margin: 20px 0 10px 0; color: #b8c6db;">⚖️ وزن‌های یادگرفته</h3>'
            + weights_html +
            '</div>'
            '<div class="section">'
            '<h2>📊 آمار دسته‌ها</h2>'
            + ('<table><thead><tr><th>دسته</th><th>کل</th><th>موفق</th><th>نرخ موفقیت</th></tr></thead><tbody>' + "".join(rows) + '</tbody></table>' if rows else '<div class="empty">هنوز نتیجه‌ای چک نشده</div>') +
            '</div>'
            '</div>'
        )

    # ------------------------------------------------------------------

    def build(self):
        print("📊 ساخت داشبورد ...")
        data = self.load_data()

        flow = data["flow"]
        tech = data["technical"]
        ai = data["ai"]

        if not flow:
            print("❌ فایل فیلتر جریان پول پیدا نشد")
            return None

        # ساخت lookup برای تکنیکال
        tech_lookup = {}
        if tech:
            for r in tech.get("results", []):
                tech_lookup[r.get("symbol")] = r

        summary = flow.get("summary", {})
        date = flow.get("date", "?")
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        # شروع HTML
        html = HTML_HEAD

        # هدر
        html += (
            '<div class="header">'
            '<h1>📈 Smart Bourse — داشبورد</h1>'
            '<div class="meta">تاریخ معاملاتی: ' + str(date) + '</div>'
            '<div class="meta">ساخته‌شده: ' + now + '</div>'
            '</div>'
        )

        # کارت‌های خلاصه
        html += (
            '<div class="cards">'
            '<div class="card buy"><div class="num">' + str(summary.get("safe_buy", 0)) + '</div><div class="label">🟢 SAFE_BUY</div></div>'
            '<div class="card sell"><div class="num">' + str(summary.get("safe_sell", 0)) + '</div><div class="label">🔴 SAFE_SELL</div></div>'
            '<div class="card queue"><div class="num">' + str(summary.get("queue_buy", 0)) + '</div><div class="label">🟡 QUEUE_BUY</div></div>'
            '<div class="card normal"><div class="num">' + str(summary.get("normal", 0)) + '</div><div class="label">⚪ NORMAL</div></div>'
            '<div class="card ai"><div class="num">' + str(len(ai.get("signals", []))) + '</div><div class="label">🧠 AI Signals</div></div>'
            '</div>'
        )

        # بخش AI
        html += self.build_ai_section(ai)

        # بخش فیلتر
        html += self.build_flow_section(flow, tech_lookup)

        # پایان
        html += HTML_FOOT.format(year=datetime.now().year)

        # ذخیره
        out_file = self.reports_dir / ("dashboard_" + str(date) + ".html")
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(html)
            print("✅ داشبورد ذخیره شد: " + str(out_file))
            return out_file
        except Exception as e:
            print("❌ خطا در ذخیره: " + str(e))
            return None


if __name__ == "__main__":
    d = DashboardBuilder()
    f = d.build()
    if f:
        print()
        print("برای باز کردن:")
        print('   start "" "' + str(f) + '"')

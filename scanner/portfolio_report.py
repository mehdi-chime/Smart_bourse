"""
Project : Smart_Bourse
File    : scanner/portfolio_report.py
Version : 1.1.0
Description :
    گزارش HTML پرتفوی
"""

import json
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from portfolio.journal import TradeJournal


REPORTS_DIR = PROJECT_ROOT / "reports"


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Smart Bourse — پرتفوی</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: 'Tahoma', sans-serif;
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    min-height: 100vh;
    padding: 20px;
    color: #fff;
}}
.container {{ max-width: 1200px; margin: 0 auto; }}
.header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    margin-bottom: 25px;
}}
.header h1 {{ font-size: 30px; margin-bottom: 8px; }}
.header .meta {{ font-size: 14px; opacity: 0.9; }}
.cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}}
.card {{
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 15px;
    padding: 20px;
    text-align: center;
}}
.card .num {{ font-size: 32px; font-weight: bold; margin-bottom: 5px; }}
.card .label {{ font-size: 13px; opacity: 0.85; }}
.card.win {{ background: linear-gradient(135deg, rgba(17,153,142,0.4), rgba(56,239,125,0.3)); }}
.card.loss {{ background: linear-gradient(135deg, rgba(235,51,73,0.4), rgba(244,92,67,0.3)); }}
.card.info {{ background: linear-gradient(135deg, rgba(75,108,183,0.4), rgba(24,40,72,0.3)); }}
.section {{
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 25px;
}}
.section h2 {{
    font-size: 20px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(255,255,255,0.1);
}}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
th {{ background: rgba(255,255,255,0.08); padding: 12px; text-align: right; color: #b8c6db; }}
td {{ padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
tr:hover {{ background: rgba(255,255,255,0.05); }}
.symbol {{ font-weight: bold; font-size: 15px; }}
.profit {{ color: #38ef7d; font-weight: bold; }}
.loss {{ color: #f45c43; font-weight: bold; }}
.badge {{ display: inline-block; padding: 4px 10px; border-radius: 15px; font-size: 12px; }}
.badge-buy {{ background: rgba(56,239,125,0.2); color: #38ef7d; }}
.badge-sell {{ background: rgba(244,92,67,0.2); color: #f45c43; }}
.empty {{ text-align: center; padding: 30px; color: #8898aa; }}
.footer {{ text-align: center; padding: 20px; color: #8898aa; font-size: 13px; }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>💼 پرتفوی Smart_Bourse</h1>
        <div class="meta">ساخته‌شده: {now}</div>
    </div>

    <div class="cards">
        <div class="card info">
            <div class="num">{open_count}</div>
            <div class="label">📂 پوزیشن باز</div>
        </div>
        <div class="card info">
            <div class="num">{closed_count}</div>
            <div class="label">✅ بسته‌شده</div>
        </div>
        <div class="card win">
            <div class="num">{win_rate}%</div>
            <div class="label">🎯 نرخ موفقیت</div>
        </div>
        <div class="card {profit_class}">
            <div class="num">{total_profit}</div>
            <div class="label">💰 سود کل (تومان)</div>
        </div>
    </div>

    {open_section}
    {closed_section}

    <div class="footer">
        Smart Bourse © {year} — Mehdi Jalali
    </div>
</div>
</body>
</html>
"""


class PortfolioReport:

    def __init__(self):
        self.journal = TradeJournal()
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _fmt(self, n):
        try:
            return "{:,}".format(int(n or 0))
        except Exception:
            return "0"

    def _build_open(self):
        positions = self.journal.open_positions
        if not positions:
            return '<div class="section"><h2>📂 پوزیشن‌های باز</h2><div class="empty">هیچ پوزیشن بازی نداری</div></div>'

        rows = []
        total_invested = 0
        for p in positions:
            total_invested += p.get("invested", 0)
            rows.append(
                "<tr>"
                "<td class='symbol'>" + str(p["symbol"]) + "</td>"
                "<td>" + self._fmt(p["quantity"]) + "</td>"
                "<td>" + self._fmt(p["buy_price"]) + "</td>"
                "<td>" + self._fmt(p["invested"]) + "</td>"
                "<td>" + str(p["buy_date"]) + "</td>"
                "<td style='color:#b8c6db; font-size:12px;'>" + str(p.get("reason", ""))[:50] + "</td>"
                "</tr>"
            )

        return (
            '<div class="section">'
            '<h2>📂 پوزیشن‌های باز (' + str(len(positions)) + ') — سرمایه: ' + self._fmt(total_invested) + ' تومان</h2>'
            '<table>'
            '<thead><tr><th>نماد</th><th>تعداد</th><th>قیمت خرید</th><th>سرمایه</th><th>تاریخ</th><th>دلیل</th></tr></thead>'
            '<tbody>' + "".join(rows) + '</tbody>'
            '</table>'
            '</div>'
        )

    def _build_closed(self):
        closed = self.journal.closed_positions
        if not closed:
            return '<div class="section"><h2>📊 معاملات بسته‌شده</h2><div class="empty">هیچ معامله‌ی بسته‌شده‌ای نداری</div></div>'

        rows = []
        for c in reversed(closed[-50:]):
            cls = "profit" if c["profit"] > 0 else "loss"
            sign = "+" if c["profit"] > 0 else ""
            rows.append(
                "<tr>"
                "<td class='symbol'>" + str(c["symbol"]) + "</td>"
                "<td>" + self._fmt(c["buy_price"]) + "</td>"
                "<td>" + self._fmt(c["sell_price"]) + "</td>"
                "<td>" + self._fmt(c["quantity"]) + "</td>"
                "<td class='" + cls + "'>" + sign + self._fmt(c["profit"]) + "</td>"
                "<td class='" + cls + "'>" + "{:+.2f}%".format(c["profit_pct"]) + "</td>"
                "<td>" + str(c["hold_days"]) + " روز</td>"
                "<td style='font-size:12px; color:#b8c6db;'>" + str(c.get("sell_reason", ""))[:40] + "</td>"
                "</tr>"
            )

        return (
            '<div class="section">'
            '<h2>📊 معاملات بسته‌شده (' + str(len(closed)) + ')</h2>'
            '<table>'
            '<thead><tr><th>نماد</th><th>خرید</th><th>فروش</th><th>تعداد</th><th>سود</th><th>درصد</th><th>مدت</th><th>دلیل فروش</th></tr></thead>'
            '<tbody>' + "".join(rows) + '</tbody>'
            '</table>'
            '</div>'
        )

    def build(self):
        print("📊 ساخت گزارش پرتفوی ...")

        s = self.journal.stats()

        profit_class = "win" if s.get("total_profit", 0) > 0 else "loss"

        html = HTML_TEMPLATE.format(
            now=datetime.now().strftime("%Y-%m-%d %H:%M"),
            open_count=s["open_positions"],
            closed_count=s["closed_trades"],
            win_rate=s["win_rate"],
            total_profit="{:,.0f}".format(s.get("total_profit", 0)),
            profit_class=profit_class,
            open_section=self._build_open(),
            closed_section=self._build_closed(),
            year=datetime.now().year,
        )

        date = datetime.now().strftime("%Y-%m-%d")
        out_file = self.reports_dir / ("portfolio_" + date + ".html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ گزارش ذخیره شد: " + str(out_file))
        return out_file


if __name__ == "__main__":
    r = PortfolioReport()
    f = r.build()
    if f:
        print()
        print('start "" "' + str(f) + '"')

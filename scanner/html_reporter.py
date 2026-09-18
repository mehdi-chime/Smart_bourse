"""
Project : Smart_Bourse
File    : html_reporter.py
Version : 1.0.0
Author  : Mehdi Jalali + Assistant

Description :
    ساخت گزارش HTML زیبا از خروجی real_flow_filter
"""

import json
from datetime import datetime
from pathlib import Path


# ======================================================================
# تنظیمات
# ======================================================================

DATA_DIR = Path(__file__).parent.parent / "data"
REAL_FLOW_DIR = DATA_DIR / "real_flow"


# ======================================================================
# HTML Template
# ======================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smart Bourse — گزارش جریان پول حقیقی</title>
<style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
        font-family: 'Tahoma', 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        min-height: 100vh;
        padding: 20px;
        color: #333;
    }}
    .container {{
        max-width: 1200px;
        margin: 0 auto;
        background: white;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        overflow: hidden;
    }}
    .header {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        text-align: center;
    }}
    .header h1 {{
        font-size: 28px;
        margin-bottom: 10px;
    }}
    .header .date {{
        font-size: 14px;
        opacity: 0.9;
    }}
    .summary {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        padding: 25px;
        background: #f8f9fa;
    }}
    .summary-card {{
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        transition: transform 0.2s;
    }}
    .summary-card:hover {{ transform: translateY(-3px); }}
    .summary-card.buy {{ background: linear-gradient(135deg, #11998e, #38ef7d); }}
    .summary-card.sell {{ background: linear-gradient(135deg, #eb3349, #f45c43); }}
    .summary-card.queue {{ background: linear-gradient(135deg, #f2994a, #f2c94c); }}
    .summary-card.normal {{ background: linear-gradient(135deg, #4b6cb7, #182848); }}
    .summary-card .num {{
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 5px;
    }}
    .summary-card .label {{
        font-size: 14px;
        opacity: 0.95;
    }}
    .section {{
        padding: 25px 30px;
    }}
    .section h2 {{
        font-size: 22px;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 3px solid;
    }}
    .section.buy h2 {{ color: #11998e; border-color: #11998e; }}
    .section.sell h2 {{ color: #eb3349; border-color: #eb3349; }}
    .section.queue h2 {{ color: #f2994a; border-color: #f2994a; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        font-size: 14px;
    }}
    th {{
        background: #f1f3f5;
        padding: 12px 10px;
        text-align: right;
        font-weight: 600;
        color: #495057;
        border-bottom: 2px solid #dee2e6;
    }}
    td {{
        padding: 10px;
        border-bottom: 1px solid #e9ecef;
    }}
    tr:hover {{ background: #f8f9fa; }}
    .symbol {{
        font-weight: bold;
        color: #212529;
    }}
    .ratio-badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
    }}
    .ratio-buy {{ background: #d4edda; color: #155724; }}
    .ratio-sell {{ background: #f8d7da; color: #721c24; }}
    .ratio-queue {{ background: #fff3cd; color: #856404; }}
    .empty {{
        text-align: center;
        padding: 30px;
        color: #6c757d;
        font-style: italic;
    }}
    .footer {{
        padding: 20px;
        text-align: center;
        background: #f8f9fa;
        color: #6c757d;
        font-size: 13px;
    }}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📊 گزارش جریان پول حقیقی</h1>
        <div class="date">Smart Bourse — تاریخ معاملاتی: {trade_date}</div>
        <div class="date">ساخته‌شده: {generated_at}</div>
    </div>

    <div class="summary">
        <div class="summary-card buy">
            <div class="num">{total_safe_buy}</div>
            <div class="label">🟢 SAFE_BUY</div>
        </div>
        <div class="summary-card sell">
            <div class="num">{total_safe_sell}</div>
            <div class="label">🔴 SAFE_SELL</div>
        </div>
        <div class="summary-card queue">
            <div class="num">{total_queue_buy}</div>
            <div class="label">🟡 QUEUE_BUY</div>
        </div>
        <div class="summary-card normal">
            <div class="num">{total_normal}</div>
            <div class="label">⚪ NORMAL</div>
        </div>
    </div>

    {sections}

    <div class="footer">
        Smart Bourse © {year} — Mehdi Jalali
        <br>
        این گزارش فقط برای کمک به تصمیم‌گیری است، نه جایگزین آن.
    </div>
</div>
</body>
</html>
"""


# ======================================================================
# کلاس اصلی
# ======================================================================

class HTMLReporter:

    def __init__(self, data_dir: Path = None):
        if data_dir is None:
            data_dir = REAL_FLOW_DIR
        self.data_dir = Path(data_dir)

    # ------------------------------------------------------------------

    def find_latest_json(self):
        """پیدا کردن آخرین فایل JSON"""
        if not self.data_dir.exists():
            return None
        files = sorted(self.data_dir.glob("real_flow_*.json"), reverse=True)
        # فایل‌های history رو حذف کن
        files = [f for f in files if "history" not in str(f)]
        return files[0] if files else None

    # ------------------------------------------------------------------

    def _build_table(self, items: list, badge_class: str):
        """ساخت جدول HTML"""
        if not items:
            return '<div class="empty">هیچ نمادی در این دسته نیست</div>'

        rows = []
        for it in items:
            symbol = it.get("Symbol") or it.get("symbol") or "?"
            last = it.get("Last") or 0
            ratio = it.get("ratio") or 0
            buy_real = it.get("Vol_buy_retail") or 0
            sell_real = it.get("Vol_sell_retail") or 0
            value = it.get("Value") or 0
            value_b = value / 1_000_000_000 if value else 0
            name = it.get("Name") or ""
            sector = it.get("SectorCode") or ""

            rows.append(f"""
                <tr>
                    <td class="symbol">{symbol}</td>
                    <td>{name[:35]}</td>
                    <td>{int(last):,}</td>
                    <td><span class="ratio-badge {badge_class}">{ratio:.2f}</span></td>
                    <td>{int(buy_real):,}</td>
                    <td>{int(sell_real):,}</td>
                    <td>{value_b:.2f}</td>
                </tr>
            """)

        return f"""
            <table>
                <thead>
                    <tr>
                        <th>نماد</th>
                        <th>نام شرکت</th>
                        <th>قیمت</th>
                        <th>نسبت</th>
                        <th>خرید حقیقی</th>
                        <th>فروش حقیقی</th>
                        <th>ارزش (میلیارد)</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        """

    # ------------------------------------------------------------------

    def build_report(self, json_file: Path):
        """ساخت گزارش HTML از فایل JSON"""
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        trade_date = data.get("date", "?")
        generated_at = data.get("generated_at", "?")
        summary = data.get("summary", {})

        safe_buy = data.get("safe_buy", [])
        safe_sell = data.get("safe_sell", [])
        queue_buy = data.get("queue_buy", [])
        normal = data.get("normal", [])

        # مرتب‌سازی بر اساس نسبت
        safe_buy = sorted(safe_buy, key=lambda x: x.get("ratio", 0) or 0, reverse=True)
        safe_sell = sorted(safe_sell, key=lambda x: x.get("ratio", 0) or 0)
        queue_buy = sorted(queue_buy, key=lambda x: x.get("ratio", 0) or 0, reverse=True)

        # ساخت بخش‌ها
        sections = ""

        # SAFE_BUY
        sections += f"""
            <div class="section buy">
                <h2>🟢 SAFE_BUY — سهام امن برای خرید</h2>
                {self._build_table(safe_buy, "ratio-buy")}
            </div>
        """

        # SAFE_SELL
        sections += f"""
            <div class="section sell">
                <h2>🔴 SAFE_SELL — سهام امن برای فروش</h2>
                {self._build_table(safe_sell, "ratio-sell")}
            </div>
        """

        # QUEUE_BUY
        sections += f"""
            <div class="section queue">
                <h2>🟡 QUEUE_BUY — صف خرید</h2>
                {self._build_table(queue_buy, "ratio-queue")}
            </div>
        """

        # رندر نهایی
        html = HTML_TEMPLATE.format(
            trade_date=trade_date,
            generated_at=generated_at,
            total_safe_buy=summary.get("safe_buy", len(safe_buy)),
            total_safe_sell=summary.get("safe_sell", len(safe_sell)),
            total_queue_buy=summary.get("queue_buy", len(queue_buy)),
            total_normal=summary.get("normal", len(normal)),
            sections=sections,
            year=datetime.now().year,
        )

        return html

    # ------------------------------------------------------------------

    def save_report(self, json_file: Path = None):
        """ساخت و ذخیره‌ی گزارش HTML"""
        if json_file is None:
            json_file = self.find_latest_json()

        if json_file is None:
            print("❌ هیچ فایل JSON پیدا نشد")
            return None

        print(f"📄 خواندن: {json_file}")
        html = self.build_report(json_file)

        # نام فایل HTML
        html_file = json_file.with_suffix(".html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ گزارش HTML ذخیره شد: {html_file}")
        return html_file


# ======================================================================
# اجرای مستقیم
# ======================================================================

if __name__ == "__main__":
    print("🚀 ساخت گزارش HTML\n")
    reporter = HTMLReporter()
    result = reporter.save_report()
    if result:
        print(f"\n🎉 تمام! فایل رو تو مرورگر باز کن:")
        print(f"   {result}")
        print()
        print("برای باز کردن:")
        print(f'   start "" "{result}"')
    else:
        print("\n⚠️  اول باید real_flow_filter.py رو اجرا کنی تا داده ساخته شه")

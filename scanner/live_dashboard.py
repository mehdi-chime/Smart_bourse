
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


# ═══════════════════════════════════════════════════════════
# پرتفوی کامل
# ═══════════════════════════════════════════════════════════
HOLDINGS = [
    {"user_name": "تابان",   "aliases": ["تابان"],                "qty": 3697,   "buy_price": None},
    {"user_name": "پکویر",   "aliases": ["پكوير", "پکویر"],      "qty": 23518,  "buy_price": None},
    {"user_name": "سمهریز",  "aliases": ["سهرمز", "سمهریز"],     "qty": 5350,   "buy_price": None},
    {"user_name": "احیا",    "aliases": ["احیا", "احياء"],        "qty": 49122,  "buy_price": None},
    {"user_name": "پیزد",    "aliases": ["پیزد"],                  "qty": 23220,  "buy_price": None},
    {"user_name": "خپارس",   "aliases": ["خپارس"],                 "qty": 217948, "buy_price": None},
    {"user_name": "خگستر",   "aliases": ["خگستر"],                 "qty": 468777, "buy_price": 4327},
    {"user_name": "فولاد",   "aliases": ["فولاد"],                 "qty": 431948, "buy_price": 3394},
]

DATA_FILE = PROJECT_ROOT / "data" / "live_snapshot.json"
REPORT_FILE = PROJECT_ROOT / "reports" / "live_dashboard.html"


def normalize(s):
    if not s:
        return s
    return (str(s)
            .replace("\u0643", "\u06a9")
            .replace("\u064a", "\u06cc")
            .replace("\u0649", "\u06cc")
            .replace("\u0629", "\u0647")
            .replace("\u0640", "")
            .strip())


def find_symbol(df, aliases):
    for alias in aliases:
        target = normalize(alias)
        for _, row in df.iterrows():
            if normalize(row.get("Symbol", "")) == target:
                return row
    for alias in aliases:
        target = normalize(alias)
        for _, row in df.iterrows():
            if normalize(row.get("Symbol", "")).startswith(target):
                return row
    return None


def fetch_data():
    df = att.get_live_market()
    if df is None or df.empty:
        return None

    df_full = df.copy()

    result = {
        "timestamp": datetime.now().isoformat(),
        "time": datetime.now().strftime("%H:%M:%S"),
        "holdings": [],
        "total_value": 0,
        "total_cost": 0,
        "total_profit": 0,
    }

    for h in HOLDINGS:
        r = find_symbol(df_full, h["aliases"])
        if r is None:
            result["holdings"].append({
                "user_name": h["user_name"],
                "status": "NOT_FOUND",
            })
            continue

        symbol = str(r.get("Symbol", h["user_name"]))
        price = float(r.get("Last") or r.get("Close") or 0)
        change = float(r.get("ChangePct") or 0)
        value = price * h["qty"]
        result["total_value"] += value

        buy_q = float(r.get("BuyQueueVolume") or 0)
        sell_q = float(r.get("SellQueueVolume") or 0)

        status = "NORMAL"
        if buy_q > 0 and sell_q == 0:
            status = "BUY_QUEUE"
        elif sell_q > 0 and buy_q == 0:
            status = "SELL_QUEUE"

        profit_pct = None
        profit_value = None
        if h.get("buy_price"):
            cost = h["buy_price"] * h["qty"]
            result["total_cost"] += cost
            profit_value = value - cost
            result["total_profit"] += profit_value
            profit_pct = (price - h["buy_price"]) / h["buy_price"] * 100

        result["holdings"].append({
            "symbol": symbol,
            "user_name": h["user_name"],
            "qty": h["qty"],
            "buy_price": h.get("buy_price"),
            "price": price,
            "change_pct": round(change, 2),
            "value": value,
            "profit_value": profit_value,
            "profit_pct": round(profit_pct, 2) if profit_pct is not None else None,
            "status": status,
        })

    return result


def build_html(data):
    rows = ""
    for h in data.get("holdings", []):
        if h.get("status") == "NOT_FOUND":
            rows += "<tr><td>" + h["user_name"] + "</td><td colspan='7'>NOT FOUND</td></tr>"
            continue

        change = h.get("change_pct", 0)
        color = "#38ef7d" if change > 0 else "#f45c43" if change < 0 else "#fff"

        status = h.get("status", "NORMAL")
        badge = ""
        if status == "BUY_QUEUE":
            badge = "<span class='badge buy'>BUY</span>"
        elif status == "SELL_QUEUE":
            badge = "<span class='badge sell'>SELL</span>"

        profit_html = "-"
        if h.get("profit_pct") is not None:
            pc = h["profit_pct"]
            pv = h["profit_value"]
            pcolor = "#38ef7d" if pc > 0 else "#f45c43"
            profit_html = "<span style='color:" + pcolor + "'>" + "{:+.2f}%".format(pc) + "</span>"
            profit_html += "<br><small style='color:" + pcolor + "'>" + "{:+,.0f}".format(pv / 10_000_000) + "M ت</small>"

        buy_p = h.get("buy_price")
        buy_p_html = "{:,}".format(int(buy_p)) if buy_p else "-"

        rows += "<tr>"
        rows += "<td><b>" + h["symbol"] + "</b></td>"
        rows += "<td>" + "{:,}".format(int(h["qty"])) + "</td>"
        rows += "<td>" + buy_p_html + "</td>"
        rows += "<td>" + "{:,}".format(int(h["price"])) + "</td>"
        rows += "<td style='color:" + color + "'>" + "{:+.2f}%".format(change) + "</td>"
        rows += "<td>" + "{:,.1f}".format(h["value"] / 1_000_000) + " M</td>"
        rows += "<td>" + profit_html + "</td>"
        rows += "<td>" + badge + "</td>"
        rows += "</tr>"

    total = data.get("total_value", 0)
    total_cost = data.get("total_cost", 0)
    total_profit = data.get("total_profit", 0)

    profit_total_html = ""
    if total_cost > 0:
        pcolor = "#38ef7d" if total_profit > 0 else "#f45c43"
        pct = (total_profit / total_cost) * 100
        profit_total_html = "<div style='text-align:center;margin-top:10px;font-size:18px'>"
        profit_total_html += "سود/ضرر: <b style='color:" + pcolor + "'>" + "{:+,.0f}".format(total_profit / 10_000_000) + "M تومان"
        profit_total_html += " (" + "{:+.2f}%".format(pct) + ")</b>"
        profit_total_html += "</div>"

    html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Smart Bourse - Live</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Tahoma,sans-serif;background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);min-height:100vh;padding:20px;color:#fff}
.container{max-width:1400px;margin:0 auto}
.header{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:20px;padding:30px;text-align:center;margin-bottom:20px}
.header h1{font-size:28px}
.header .time{font-size:14px;opacity:.9;margin-top:8px}
.card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:25px;margin-bottom:20px}
.card h2{font-size:20px;margin-bottom:15px;padding-bottom:10px;border-bottom:2px solid rgba(255,255,255,.1)}
table{width:100%;border-collapse:collapse;font-size:14px}
th{background:rgba(255,255,255,.08);padding:12px;text-align:right;color:#b8c6db}
td{padding:12px;border-bottom:1px solid rgba(255,255,255,.05)}
tr:hover{background:rgba(255,255,255,.05)}
.badge{display:inline-block;padding:4px 10px;border-radius:15px;font-size:12px;font-weight:bold}
.badge.buy{background:rgba(56,239,125,.25);color:#38ef7d;border:1px solid #38ef7d}
.badge.sell{background:rgba(244,92,67,.25);color:#f45c43;border:1px solid #f45c43}
.total{text-align:center;font-size:24px;margin-top:20px;padding:15px;background:rgba(56,239,125,.15);border-radius:12px}
.footer{text-align:center;padding:15px;color:#8898aa;font-size:12px}
</style>
<script>
setTimeout(function(){location.reload();}, 30000);
</script>
</head>
<body>
<div class="container">
<div class="header">
<h1>📊 Live Dashboard</h1>
<div class="time">آخرین به‌روزرسانی: """ + data.get("time", "?") + """ | Auto-refresh هر 30 ثانیه</div>
</div>
<div class="card">
<h2>💼 پرتفوی (8 سهم)</h2>
<table>
<thead><tr><th>نماد</th><th>تعداد</th><th>خرید</th><th>قیمت</th><th>تغییر</th><th>ارزش (M)</th><th>سود/ضرر</th><th>وضعیت</th></tr></thead>
<tbody>""" + rows + """</tbody>
</table>
<div class="total">ارزش کل: <b>""" + "{:,.1f}".format(total / 1_000_000) + """ M ریال</b></div>
""" + profit_total_html + """
</div>
<div class="footer">
Smart Bourse © """ + str(datetime.now().year) + """ - Mehdi Jalali
</div>
</div>
</body>
</html>"""

    return html


def main():
    print()
    print("=" * 75)
    print("  Live Dashboard Builder")
    print("=" * 75)
    print()

    print("Fetching data ...")
    data = fetch_data()
    if not data:
        print("No data")
        return

    print("Holdings: " + str(len(data.get("holdings", []))))
    print("Total: " + "{:,.1f}".format(data.get("total_value", 0) / 1_000_000) + " M rials")
    if data.get("total_cost", 0) > 0:
        print("Profit: " + "{:+,.0f}".format(data["total_profit"] / 10_000_000) + " M toman")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(data)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print()
    print("HTML: " + str(REPORT_FILE))
    print()
    print('Open: start "" "' + str(REPORT_FILE) + '"')
    print()


if __name__ == "__main__":
    main()

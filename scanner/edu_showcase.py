import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"


def load_json(path):
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def main():
    print("Building Educational Showcase...")
    today = datetime.now().strftime("%Y-%m-%d")

    portfolio_data = None
    pf = DATA_DIR / "portfolio_history" / (today + ".jsonl")
    if pf.exists():
        with open(pf, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
            if lines:
                portfolio_data = json.loads(lines[-1])
    print("Portfolio: " + ("OK" if portfolio_data else "missing"))

    market_ctx = load_json(DATA_DIR / "market_context" / ("context_" + today + ".json"))
    print("Market: " + ("OK" if market_ctx else "missing"))

    flow_data = load_json(DATA_DIR / "real_flow" / ("real_flow_" + today + ".json"))
    print("Flow: " + ("OK" if flow_data else "missing"))

    ai_count = 0
    ai_file = DATA_DIR / "ai" / "memory.jsonl"
    if ai_file.exists():
        with open(ai_file, "r", encoding="utf-8") as f:
            ai_count = len([l for l in f if l.strip()])
    print("AI signals: " + str(ai_count))

    html = build(portfolio_data, market_ctx, flow_data, ai_count)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out = REPORTS_DIR / ("edu_showcase_" + today + ".html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved: " + str(out))


def build(portfolio, market, flow, ai_count):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    pf_rows = ""
    total = 0
    if portfolio:
        for h in portfolio.get("holdings", []):
            total += h.get("value", 0)
            c = "#38ef7d" if h.get("change_pct", 0) > 0 else "#f45c43"
            pf_rows += "<tr><td><b>" + h["symbol"] + "</b></td>"
            pf_rows += "<td>" + "{:,}".format(int(h["qty"])) + "</td>"
            pf_rows += "<td>" + "{:,}".format(int(h["price"])) + "</td>"
            pf_rows += "<td style='color:" + c + ";'>" + "{:+.2f}%".format(h["change_pct"]) + "</td>"
            pf_rows += "<td>" + "{:,.1f}".format(h["value"] / 1_000_000) + " M</td></tr>"

    mk = ""
    if market and market.get("index"):
        idx = market["index"]
        mk += "<div class='stat'><div class='lbl'>Shakhes Kol</div>"
        mk += "<div class='val'>" + "{:,}".format(int(idx.get("total", 0))) + "</div>"
        mk += "<div class='chg'>" + "{:+.2f}%".format(idx.get("total_change_pct", 0)) + "</div></div>"
    if market and market.get("breadth"):
        b = market["breadth"]
        mk += "<div class='stat'><div class='lbl'>Sooudi / Nozouli</div>"
        mk += "<div class='val'>" + str(b.get("advancers", 0)) + " / " + str(b.get("decliners", 0)) + "</div></div>"

    fl = ""
    if flow:
        s = flow.get("summary", {})
        fl += "<div class='stat'><div class='lbl'>SAFE_BUY</div>"
        fl += "<div class='val' style='color:#38ef7d;'>" + str(s.get("safe_buy", 0)) + "</div></div>"
        fl += "<div class='stat'><div class='lbl'>SAFE_SELL</div>"
        fl += "<div class='val' style='color:#f45c43;'>" + str(s.get("safe_sell", 0)) + "</div></div>"

    html = "<!DOCTYPE html>"
    html += "<html lang='fa' dir='rtl'>"
    html += "<head><meta charset='UTF-8'>"
    html += "<title>Smart Bourse - Educational</title>"
    html += "<style>"
    html += "*{box-sizing:border-box;margin:0;padding:0}"
    html += "body{font-family:Tahoma,sans-serif;background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);min-height:100vh;padding:25px;color:#fff}"
    html += ".container{max-width:1400px;margin:0 auto}"
    html += ".header{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:20px;padding:40px;text-align:center;margin-bottom:25px}"
    html += ".header h1{font-size:36px;margin-bottom:12px}"
    html += ".quote{font-style:italic;font-size:16px;margin-top:15px;padding:15px;background:rgba(0,0,0,.15);border-radius:10px}"
    html += ".meta{font-size:14px;opacity:.85;margin-top:15px}"
    html += ".section{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:25px;margin-bottom:25px}"
    html += ".section h2{font-size:24px;margin-bottom:20px;padding-bottom:12px;border-bottom:2px solid rgba(255,255,255,.15)}"
    html += ".stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px}"
    html += ".stat{background:rgba(255,255,255,.08);border-radius:12px;padding:20px;text-align:center}"
    html += ".lbl{font-size:13px;color:#b8c6db;margin-bottom:8px}"
    html += ".val{font-size:28px;font-weight:bold}"
    html += ".chg{font-size:14px;margin-top:5px}"
    html += "table{width:100%;border-collapse:collapse;font-size:14px}"
    html += "th{background:rgba(255,255,255,.08);padding:12px;text-align:right;color:#b8c6db}"
    html += "td{padding:12px;border-bottom:1px solid rgba(255,255,255,.05)}"
    html += ".footer{text-align:center;padding:25px;color:#8898aa;font-size:13px}"
    html += ".badge{display:inline-block;padding:6px 14px;border-radius:20px;font-size:13px;margin:5px;background:rgba(102,126,234,.3);border:1px solid #667eea}"
    html += "</style></head><body>"
    html += "<div class='container'>"
    html += "<div class='header'>"
    html += "<h1>Smart_Bourse - Educational</h1>"
    html += "<div class='quote'>All is math. Order is the best example of AI order.</div>"
    html += "<div class='meta'>Built: " + now + "</div>"
    html += "</div>"
    html += "<div class='section'><h2>Market Context</h2>"
    html += "<div class='stats'>" + mk + fl + "</div></div>"
    html += "<div class='section'><h2>Live Portfolio</h2>"
    html += "<table><thead><tr><th>Symbol</th><th>Qty</th><th>Price</th><th>Change</th><th>Value (M)</th></tr></thead>"
    html += "<tbody>" + pf_rows + "</tbody></table>"
    html += "<div style='text-align:center;margin-top:20px;font-size:20px'>"
    html += "Total: <b style='color:#38ef7d'>" + "{:,.1f}".format(total / 1_000_000) + " M Rials</b>"
    html += "</div></div>"
    html += "<div class='section'><h2>AI</h2>"
    html += "<div class='stats'>"
    html += "<div class='stat'><div class='lbl'>AI Signals</div><div class='val'>" + str(ai_count) + "</div></div>"
    html += "<div class='stat'><div class='lbl'>Algorithms</div><div class='val'>5</div></div>"
    html += "</div>"
    html += "<div style='text-align:center;margin-top:20px'>"
    html += "<span class='badge'>Python</span>"
    html += "<span class='badge'>Pandas</span>"
    html += "<span class='badge'>TSETMC API</span>"
    html += "<span class='badge'>RSI</span>"
    html += "<span class='badge'>MACD</span>"
    html += "<span class='badge'>AI Memory</span>"
    html += "</div></div>"
    html += "<div class='section'><h2>Why it matters</h2>"
    html += "<ul style='line-height:2;padding-right:20px'>"
    html += "<li><b>Real data:</b> from Tehran Stock Exchange</li>"
    html += "<li><b>Math:</b> RSI, MACD, moving average</li>"
    html += "<li><b>Order:</b> saved every 30 seconds</li>"
    html += "<li><b>AI:</b> learns from results</li>"
    html += "<li><b>Science, not myth:</b> data-driven</li>"
    html += "</ul></div>"
    html += "<div class='footer'>Smart Bourse (c) " + str(datetime.now().year) + " - Mehdi Jalali"
    html += "<br>Built with open-source tools. Free for education.</div>"
    html += "</div></body></html>"
    return html


if __name__ == "__main__":
    main()

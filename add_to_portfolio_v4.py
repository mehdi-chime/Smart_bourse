# add_to_portfolio_v4.py
# پرتفوی نهایی (بدون فجر انرژی)
# اجرا: python add_to_portfolio_v4.py

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
PORTFOLIO_FILE = PROJECT_ROOT / "data" / "my_portfolio.json"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def save_portfolio(data):
    PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    PORTFOLIO_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 پرتفوی نهایی")
    safe_print("=" * 80)
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # پرتفوی جدید (بدون فجر)
    # ═══════════════════════════════════════════════════════

    portfolio = [
        # (symbol, buy_price, quantity)
        ("وتوصا", 3027, 3027),
        ("چاپ", 19644, 4072),
        ("خزر", 2082, 52068),
        ("حفاری", 5857, 34327),
    ]

    data = []
    total_cost = 0

    for symbol, buy_price, quantity in portfolio:
        cost = buy_price * quantity
        total_cost += cost

        data.append({
            "symbol": symbol,
            "buy_price": buy_price,
            "quantity": quantity,
            "buy_date": datetime.now().strftime("%Y-%m-%d"),
        })

    save_portfolio(data)

    safe_print(f"  ✅ {len(data)} سهم ذخیره شد")
    safe_print("")
    safe_print(f"  {'نماد':<15} | {'قیمت':>10} | {'تعداد':>10} | {'مبلغ':>15}")
    safe_print("  " + "-" * 70)

    for d in data:
        cost = d['buy_price'] * d['quantity']
        safe_print(f"  {d['symbol']:15} | {d['buy_price']:>10,} | {d['quantity']:>10,} | {cost:>15,} ریال")

    safe_print("")
    safe_print(f"  💰 کل سرمایه: {total_cost:,} ریال")
    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()

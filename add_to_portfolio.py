# add_to_portfolio.py
# اضافه کردن سهم به پرتفوی من
# اجرا: python add_to_portfolio.py

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


def load_portfolio():
    if PORTFOLIO_FILE.exists():
        try:
            return json.loads(PORTFOLIO_FILE.read_text(encoding="utf-8"))
        except:
            return []
    return []


def save_portfolio(data):
    PORTFOLIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    PORTFOLIO_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def add_stock(symbol, buy_price, quantity, ins_code="", note=""):
    """اضافه کردن سهم"""
    portfolio = load_portfolio()

    # چک تکراری
    for s in portfolio:
        if s["symbol"] == symbol:
            safe_print(f"  ℹ️ {symbol} از قبل هست")
            return

    portfolio.append({
        "symbol": symbol,
        "ins_code": ins_code,
        "buy_price": buy_price,
        "quantity": quantity,
        "buy_date": datetime.now().strftime("%Y-%m-%d"),
        "note": note,
    })

    save_portfolio(portfolio)
    safe_print(f"  ✅ {symbol} اضافه شد")


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 اضافه کردن سهم به پرتفوی")
    safe_print("=" * 80)
    safe_print("")

    # سهم‌هایی که داری
    # اینجا اسم + قیمت خرید + تعداد رو بذار
    MY_STOCKS = [
        # (symbol, buy_price, quantity, ins_code)
        ("وتوصا", 3030, 100, ""),
        ("خزر", 2100, 50, ""),
        ("حفاری", 5800, 20, ""),
        ("چاپ", 19600, 10, ""),
        ("رتاپ", 0, 0, ""),  # فروختی
    ]

    for symbol, buy_price, quantity, ins_code in MY_STOCKS:
        add_stock(symbol, buy_price, quantity, ins_code)

    safe_print("")
    safe_print("=" * 80)

    # نمایش
    portfolio = load_portfolio()
    safe_print(f"  📊 پرتفوی: {len(portfolio)} سهم")
    safe_print("")

    for s in portfolio:
        safe_print(f"     {s['symbol']:15} | خرید: {s['buy_price']:>10,} | تعداد: {s['quantity']}")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()

# record_all_trades.py
# ثبت همه معاملات امروز
# اجرا: python record_all_trades.py

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
TRADES_FILE = PROJECT_ROOT / "data" / "trade_history.json"
PORTFOLIO_FILE = PROJECT_ROOT / "data" / "my_portfolio.json"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def load_json(path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except:
            pass
    return default if default is not None else []


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def main():
    safe_print("")
    safe_print("=" * 100)
    safe_print("  📊 ثبت معاملات امروز")
    safe_print("=" * 100)
    safe_print("")

    trades = load_json(TRADES_FILE, [])
    portfolio = load_json(PORTFOLIO_FILE, [])

    # ═══════════════════════════════════════════════════════
    # فروش‌ها
    # ═══════════════════════════════════════════════════════

    sells = [
        # (نماد, تعداد, قیمت خرید, قیمت فروش)
        ("رتاپ", 8377, 9060, 9734),
        ("فرآورده تزریقی", 8422, 44464, 46607),
        ("کاویر تایر", 23518, 3714, 3697),
    ]

    total_profit = 0

    for symbol, qty, buy_price, sell_price in sells:
        profit = (sell_price - buy_price) * qty
        profit_pct = (sell_price - buy_price) / buy_price * 100

        trades.append({
            "type": "SELL",
            "symbol": symbol,
            "quantity": qty,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "profit": profit,
            "profit_pct": profit_pct,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        total_profit += profit

        emoji = "🟢" if profit > 0 else "🔴"
        safe_print(f"  {emoji} {symbol:20} | {qty:>6} سهم | {profit:+15,.0f} ریال ({profit_pct:+.2f}%)")

    safe_print("")
    safe_print(f"  💰 سود کل فروش: {total_profit:+,.0f} ریال")
    safe_print("")

    # ═══════════════════════════════════════════════════════
    # خریدها
    # ═══════════════════════════════════════════════════════

    buys = [
        # (نماد, تعداد, قیمت خرید)
        ("وتوصا", 24848, 3001),
        ("چاپ", 16972, 8331),
        ("خزر", 52068, 2082),
        ("حفاری", 34327, 5857),
        ("فجر انرژی", 34284, 10740),
    ]

    safe_print("  📊 خریدها:")
    safe_print("")

    for symbol, qty, buy_price in buys:
        trades.append({
            "type": "BUY",
            "symbol": symbol,
            "quantity": qty,
            "buy_price": buy_price,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        safe_print(f"  🟢 {symbol:20} | {qty:>6} سهم | {buy_price:>10,.0f} ریال")

    # ═══════════════════════════════════════════════════════
    # آپدیت پرتفوی
    # ═══════════════════════════════════════════════════════

    # پرتفوی جدید
    new_portfolio = []

    # سهم‌های قبلی که نگه داشتی
    old_symbols = ["خزر", "حفاری", "چاپ"]  # ← اینا قبلاً داشتی

    for symbol, qty, buy_price in buys:
        new_portfolio.append({
            "symbol": symbol,
            "quantity": qty,
            "buy_price": buy_price,
            "buy_date": datetime.now().strftime("%Y-%m-%d"),
        })

    save_json(PORTFOLIO_FILE, new_portfolio)

    # ذخیره
    save_json(TRADES_FILE, trades)

    safe_print("")
    safe_print("=" * 100)
    safe_print(f"  💾 ذخیره: {TRADES_FILE}")
    safe_print(f"  💾 ذخیره: {PORTFOLIO_FILE}")
    safe_print("=" * 100)


if __name__ == "__main__":
    main()

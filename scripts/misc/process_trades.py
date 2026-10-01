"""
Project : Smart_Bourse
File    : process_trades.py
Version : 1.0.0
Description :
    خواندن معاملات از فایل متنی (trades_input.txt)
    و ثبت آن‌ها در ژورنال

فرمت فایل:
    BUY  | نماد | قیمت | تعداد | دلیل
    SELL | نماد | قیمت | تعداد | دلیل

مثال:
    BUY | وکغدیر | 6960 | 1000 | نسبت خرید حقیقی 20.3
    BUY | نوری | 46400 | 100 | تکنیکال
    SELL | وکغدیر | 7500 | 1000 | حد سود
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from portfolio.journal import TradeJournal


INPUT_FILE = PROJECT_ROOT / "trades_input.txt"


def ensure_input_file():
    """اگه فایل نبود، بسازش"""
    if not INPUT_FILE.exists():
        sample = """# فایل معاملات Smart_Bourse
# ------------------------------
# هر خط یه معامله. فرمت:
#   BUY  | نماد | قیمت | تعداد | دلیل
#   SELL | نماد | قیمت | تعداد | دلیل
#
# نکته: خطوطی که با # شروع بشن، نادیده گرفته می‌شن.
# ------------------------------
# نمونه (این خطوط رو پاک کن و مال خودت رو بنویس):
#
# BUY | وکغدیر | 6960 | 1000 | نسبت خرید حقیقی 20.3
# BUY | نوری | 46400 | 100 | تکنیکال
# SELL | وکغدیر | 7500 | 1000 | رسید به حد سود
#
# ------------------------------
"""
        INPUT_FILE.write_text(sample, encoding="utf-8")
        print("OK | فایل نمونه ساخته شد: " + str(INPUT_FILE))
        print()
        print("حالا با Notepad بازش کن و معاملاتت رو بنویس:")
        print('   notepad trades_input.txt')
        print()
        print("بعد دوباره این اسکریپت رو اجرا کن.")
        return False
    return True


def parse_line(line):
    """تجزیه یه خط"""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 4:
        return None

    action = parts[0].upper()
    symbol = parts[1]
    try:
        price = float(parts[2])
        quantity = int(parts[3])
    except ValueError:
        return None
    reason = parts[4] if len(parts) > 4 else ""

    if action not in ("BUY", "SELL"):
        return None

    return {
        "action": action,
        "symbol": symbol,
        "price": price,
        "quantity": quantity,
        "reason": reason,
    }


def main():
    print()
    print("=" * 70)
    print("  📝 پردازش معاملات از فایل")
    print("=" * 70)
    print()

    if not ensure_input_file():
        return

    content = INPUT_FILE.read_text(encoding="utf-8")
    lines = content.split("\n")

    trades = []
    for line in lines:
        t = parse_line(line)
        if t:
            trades.append(t)

    if not trades:
        print("هیچ معامله‌ای تو فایل پیدا نشد.")
        print()
        print("فایل: " + str(INPUT_FILE))
        print()
        print("با Notepad بازش کن:")
        print('   notepad trades_input.txt')
        return

    print("📋 " + str(len(trades)) + " معامله پیدا شد")
    print()

    journal = TradeJournal()
    applied = 0
    failed = 0

    for t in trades:
        try:
            if t["action"] == "BUY":
                journal.buy(
                    symbol=t["symbol"],
                    price=t["price"],
                    quantity=t["quantity"],
                    reason=t["reason"],
                )
            else:
                journal.sell(
                    symbol=t["symbol"],
                    price=t["price"],
                    quantity=t["quantity"],
                    reason=t["reason"],
                )
            applied += 1
        except Exception as e:
            print("X | خطا در " + t["symbol"] + ": " + str(e))
            failed += 1

    print()
    print("=" * 70)
    print("  ✅ " + str(applied) + " معامله ثبت شد")
    if failed:
        print("  ❌ " + str(failed) + " خطا")
    print("=" * 70)
    print()

    # گزارش سریع
    journal.report()
    journal.show_open()

    # پاک کردن خطوط پردازش‌شده
    print()
    ans = input("فایل ورودی پاک شود؟ (y/n): ").strip().lower()
    if ans == "y":
        sample = """# فایل معاملات Smart_Bourse
# ------------------------------
# هر خط یه معامله. فرمت:
#   BUY  | نماد | قیمت | تعداد | دلیل
#   SELL | نماد | قیمت | تعداد | دلیل
# ------------------------------
"""
        INPUT_FILE.write_text(sample, encoding="utf-8")
        print("OK | فایل پاک شد")


if __name__ == "__main__":
    main()

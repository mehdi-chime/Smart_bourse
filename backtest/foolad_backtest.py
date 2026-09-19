"""
Project : Smart_Bourse
File    : backtest/foolad_backtest.py
Version : 2.0.0
Description :
    بک‌تست پیشرفته روی فولاد و نمادهای بزرگ
    - ۳ سال تاریخچه
    - ۱۵ استراتژی RSI
    - محاسبه‌ی سود تجمعی، شارپ، drawdown واقعی
"""

import sys
from datetime import datetime
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att
import numpy as np


# ======================================================================
# تنظیمات
# ======================================================================

# نمادهای هدف — فولاد اول، بعد ۲۰ نماد بزرگ
TARGET_SYMBOLS = [
    "فولاد",    # فولاد مبارکه — اصلی
    "فملی",     # ملی صنایع مس
    "خودرو",    # ایران خودرو
    "خساپا",    # سایپا
    "شستا",     # تأمین اجتماعی
    "وبملت",    # بانک ملت
    "وتجارت",   # بانک تجارت
    "وپارس",    # بانک پارسیان
    "شپنا",     # پالایش نفت اصفهان
    "خبهمن",    # بهمن
    "وکغدیر",   # توسعه معادن غدیر
    "نوری",     # پتروشیمی نوری
    "کگل",      # گل گهر
    "وبصادر",   # بانک صادرات
    "اخابر",    # مخابرات
    "فخوز",     # فولاد خوزستان
    "ذوب",      # ذوب آهن اصفهان
    "شتران",    # پالایش نفت تهران
    "کچاد",     # چادرملو
    "همراه",    # همراه اول
    "وغدیر",    # سرمایه‌گذاری غدیر
]

RSI_THRESHOLDS = [20, 25, 30, 35, 40, 50]
HOLD_PERIODS = [7, 14, 30, 60, 90]

DATA_DIR = PROJECT_ROOT / "data" / "backtest"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ======================================================================
# محاسبه RSI
# ======================================================================

def calculate_rsi_series(prices, period=14):
    if len(prices) < period + 1:
        return []
    prices = np.array(prices, dtype=float)
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gains = np.zeros(len(deltas))
    avg_losses = np.zeros(len(deltas))
    avg_gains[period - 1] = gains[:period].mean()
    avg_losses[period - 1] = losses[:period].mean()

    for i in range(period, len(deltas)):
        avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i]) / period
        avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i]) / period

    rsi = np.zeros(len(deltas))
    for i in range(period - 1, len(deltas)):
        if avg_losses[i] == 0:
            rsi[i] = 100
        else:
            rs = avg_gains[i] / avg_losses[i]
            rsi[i] = 100 - (100 / (1 + rs))

    return [None] * (period) + rsi[period-1:].tolist()


# ======================================================================
# بک‌تست یه نماد
# ======================================================================

def backtest_symbol(symbol, rsi_threshold, hold_days):
    try:
        df = att.get_history(symbol)
    except Exception:
        return None

    if df is None or df.empty or "Close" not in df.columns:
        return None

    prices = df["Close"].tolist()
    if len(prices) < 60:
        return None

    rsi_series = calculate_rsi_series(prices, period=14)

    trades = []
    i = 20
    while i < len(prices) - hold_days:
        rsi = rsi_series[i] if i < len(rsi_series) else None
        if rsi is not None and rsi < rsi_threshold:
            buy_price = prices[i]
            sell_idx = i + hold_days
            if sell_idx < len(prices):
                sell_price = prices[sell_idx]
                profit_pct = (sell_price - buy_price) / buy_price * 100
                trades.append({
                    "buy_day": i,
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "profit_pct": profit_pct,
                    "date": str(df.index[i]) if i < len(df.index) else "",
                })
                i = sell_idx + 1
                continue
        i += 1

    return trades


# ======================================================================
# بک‌تست کامل
# ======================================================================

class FocusedBacktest:

    def __init__(self, symbols=None):
        self.symbols = symbols or TARGET_SYMBOLS
        self.results = {}
        self.per_symbol = {}

    def run(self):
        print()
        print("=" * 80)
        print("  بک‌تست پیشرفته — فولاد و نمادهای بزرگ")
        print("=" * 80)
        print()
        print("  نمادها: " + str(len(self.symbols)))
        for s in self.symbols:
            print("     - " + s)
        print()

        for threshold in RSI_THRESHOLDS:
            for hold in HOLD_PERIODS:
                key = "RSI<" + str(threshold) + " h=" + str(hold) + "d"
                all_trades = []
                per_symbol_trades = {}

                for symbol in self.symbols:
                    trades = backtest_symbol(symbol, threshold, hold)
                    if trades:
                        all_trades.extend(trades)
                        per_symbol_trades[symbol] = trades

                if not all_trades:
                    continue

                profits = [t["profit_pct"] for t in all_trades]
                wins = [p for p in profits if p > 0]
                losses = [p for p in profits if p <= 0]

                total = len(all_trades)
                win_rate = len(wins) / total * 100 if total > 0 else 0
                avg_profit = sum(profits) / total if total > 0 else 0

                # محاسبه‌ی drawdown واقعی (compound)
                balance = 100.0
                peak = 100.0
                max_dd = 0.0
                for p in profits:
                    balance *= (1 + p / 100)
                    if balance > peak:
                        peak = balance
                    dd = (peak - balance) / peak * 100
                    if dd > max_dd:
                        max_dd = dd

                # شارپ (تقریبی)
                if len(profits) > 1:
                    std = np.std(profits)
                    sharpe = (avg_profit / std) if std > 0 else 0
                else:
                    sharpe = 0

                self.results[key] = {
                    "threshold": threshold,
                    "hold": hold,
                    "total_trades": total,
                    "wins": len(wins),
                    "losses": len(losses),
                    "win_rate": round(win_rate, 2),
                    "avg_profit": round(avg_profit, 2),
                    "total_return": round(balance - 100, 2),
                    "max_drawdown": round(max_dd, 2),
                    "sharpe": round(sharpe, 3),
                }

                self.per_symbol[key] = per_symbol_trades

        return self.results

    def print_report(self):
        if not self.results:
            print("نتیجه‌ای نیست")
            return

        print()
        print("=" * 110)
        print("  نتایج بک‌تست — مرتب‌شده بر اساس بازده کل")
        print("=" * 110)
        print()
        print("   استراتژی            | معاملات | برد% | میانگین | بازده کل | افت | شارپ")
        print("   " + "-" * 106)

        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]["total_return"],
            reverse=True,
        )

        for key, r in sorted_results:
            print(
                "   " + key.ljust(20)
                + " | " + str(r["total_trades"]).rjust(7)
                + " | " + "{:>5.1f}%".format(r["win_rate"])
                + " | " + "{:>+7.2f}%".format(r["avg_profit"]).rjust(9)
                + " | " + "{:>+8.1f}%".format(r["total_return"]).rjust(9)
                + " | " + "{:>5.1f}%".format(r["max_drawdown"]).rjust(6)
                + " | " + "{:>6.2f}".format(r["sharpe"]).rjust(6)
            )

        print("=" * 110)

        best = sorted_results[0]
        print()
        print("  🏆 بهترین استراتژی: " + best[0])
        print("     - بازده کل: " + str(best[1]["total_return"]) + "%")
        print("     - نرخ برد: " + str(best[1]["win_rate"]) + "%")
        print("     - میانگین سود: " + str(best[1]["avg_profit"]) + "%")
        print("     - افت حداکثر: " + str(best[1]["max_drawdown"]) + "%")
        print()

    def print_foolad_detail(self, strategy_key):
        """جزئیات استراتژی برتر برای فولاد"""
        if strategy_key not in self.per_symbol:
            return

        trades_by_symbol = self.per_symbol[strategy_key]

        print()
        print("=" * 80)
        print("  جزئیات استراتژی برتر — به تفکیک نماد")
        print("=" * 80)
        print()
        print("   نماد        | معاملات | نرخ برد | میانگین سود | بازده کل")
        print("   " + "-" * 76)

        symbol_stats = []
        for symbol, trades in trades_by_symbol.items():
            profits = [t["profit_pct"] for t in trades]
            wins = [p for p in profits if p > 0]
            win_rate = len(wins) / len(trades) * 100 if trades else 0
            avg = sum(profits) / len(trades) if trades else 0

            balance = 100.0
            for p in profits:
                balance *= (1 + p / 100)
            total_ret = balance - 100

            symbol_stats.append({
                "symbol": symbol,
                "trades": len(trades),
                "win_rate": win_rate,
                "avg": avg,
                "total_ret": total_ret,
            })

        symbol_stats.sort(key=lambda x: x["total_ret"], reverse=True)

        for s in symbol_stats:
            marker = " ⭐" if s["symbol"] == "فولاد" else ""
            print(
                "   " + s["symbol"].ljust(10)
                + " | " + str(s["trades"]).rjust(7)
                + " | " + "{:>6.1f}%".format(s["win_rate"])
                + " | " + "{:>+7.2f}%".format(s["avg"]).rjust(9)
                + " | " + "{:>+8.1f}%".format(s["total_ret"]).rjust(9)
                + marker
            )

        print("=" * 80)

    def save(self):
        date = datetime.now().strftime("%Y-%m-%d")
        out_file = DATA_DIR / ("foolad_backtest_" + date + ".json")

        # پاک‌سازی per_symbol (تبدیل به خلاصه)
        summary = {}
        for key, r in self.results.items():
            summary[key] = r

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({
                "date": date,
                "symbols": self.symbols,
                "strategies": summary,
            }, f, ensure_ascii=False, indent=2)

        print("ذخیره شد: " + str(out_file))
        return out_file


# ======================================================================
# اجرا
# ======================================================================

if __name__ == "__main__":
    print()
    print("🚀 شروع بک‌تست پیشرفته")
    print("   نمادهای هدف: " + str(len(TARGET_SYMBOLS)))
    print("   استراتژی‌ها: " + str(len(RSI_THRESHOLDS) * len(HOLD_PERIODS)))
    print()

    bt = FocusedBacktest()
    bt.run()
    bt.print_report()

    # جزئیات استراتژی برتر
    if bt.results:
        best = max(bt.results.items(), key=lambda x: x[1]["total_return"])
        bt.print_foolad_detail(best[0])

    bt.save()
    print()
    print("تمام!")

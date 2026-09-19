"""
Project : Smart_Bourse
File    : backtest/strategy_backtest.py
Version : 1.0.0
Description :
    بک‌تست استراتژی RSI روی تاریخچه ۱ ساله
    - تست RSI thresholds: 20, 30, 40, 50
    - تست hold periods: 3, 7, 14, 30 روز
    - محاسبه win rate, average return, max drawdown
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

RSI_THRESHOLDS = [20, 25, 30, 35, 40, 50]
HOLD_PERIODS = [3, 5, 7, 14, 30]
DATA_DIR = PROJECT_ROOT / "data" / "backtest"
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ======================================================================
# محاسبه RSI
# ======================================================================

def calculate_rsi_series(prices, period=14):
    """محاسبه RSI برای کل سری قیمت"""
    if len(prices) < period + 1:
        return []

    prices = np.array(prices, dtype=float)
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gains = np.zeros(len(deltas))
    avg_losses = np.zeros(len(deltas))

    # میانگین اولیه
    avg_gains[period - 1] = gains[:period].mean()
    avg_losses[period - 1] = losses[:period].mean()

    # Wilder smoothing
    for i in range(period, len(deltas)):
        avg_gains[i] = (avg_gains[i - 1] * (period - 1) + gains[i]) / period
        avg_losses[i] = (avg_losses[i - 1] * (period - 1) + losses[i]) / period

    rsi = np.zeros(len(deltas))
    for i in range(period - 1, len(deltas)):
        if avg_losses[i] == 0:
            rsi[i] = 100
        else:
            rs = avg_gains[i] / avg_losses[i]
            rsi[i] = 100 - (100 / (1 + rs))

    # padding اول
    return [None] * (period) + rsi[period - 1:].tolist()


# ======================================================================
# بک‌تست یه نماد
# ======================================================================

def backtest_symbol(symbol, rsi_threshold, hold_days):
    """بک‌تست یه نماد با یه threshold و hold"""
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
    i = 20  # از روز ۲۰ شروع کن
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
                })
                i = sell_idx + 1
                continue
        i += 1

    return trades


# ======================================================================
# بک‌تست کامل
# ======================================================================

class StrategyBacktest:

    def __init__(self, symbols=None):
        if symbols is None:
            # نمادهای پرمعامله
            symbols = [
                "فولاد", "فملی", "خودرو", "خساپا", "شستا",
                "وبملت", "وتجارت", "وپارس", "شپنا", "خبهمن",
                "وکغدیر", "نوری", "کگل", "وبصادر", "اخابر",
            ]
        self.symbols = symbols
        self.results = {}

    def run(self):
        print()
        print("=" * 70)
        print("  بک‌تست استراتژی RSI — ۱ سال تاریخچه")
        print("=" * 70)
        print()
        print("  نمادها: " + str(len(self.symbols)))
        print("  RSI thresholds: " + str(RSI_THRESHOLDS))
        print("  Hold periods: " + str(HOLD_PERIODS))
        print()

        for threshold in RSI_THRESHOLDS:
            for hold in HOLD_PERIODS:
                key = "RSI<" + str(threshold) + " hold=" + str(hold) + "d"
                all_trades = []
                symbol_count = 0

                for symbol in self.symbols:
                    trades = backtest_symbol(symbol, threshold, hold)
                    if trades:
                        all_trades.extend(trades)
                        symbol_count += 1

                if not all_trades:
                    continue

                profits = [t["profit_pct"] for t in all_trades]
                wins = [p for p in profits if p > 0]
                losses = [p for p in profits if p <= 0]

                total_trades = len(all_trades)
                win_rate = len(wins) / total_trades * 100 if total_trades > 0 else 0
                avg_profit = sum(profits) / total_trades if total_trades > 0 else 0
                avg_win = sum(wins) / len(wins) if wins else 0
                avg_loss = sum(losses) / len(losses) if losses else 0

                # Max drawdown (تقریبی)
                cumulative = 0
                peak = 0
                max_dd = 0
                for p in profits:
                    cumulative += p
                    if cumulative > peak:
                        peak = cumulative
                    dd = peak - cumulative
                    if dd > max_dd:
                        max_dd = dd

                self.results[key] = {
                    "threshold": threshold,
                    "hold": hold,
                    "total_trades": total_trades,
                    "symbols_count": symbol_count,
                    "wins": len(wins),
                    "losses": len(losses),
                    "win_rate": round(win_rate, 2),
                    "avg_profit": round(avg_profit, 2),
                    "avg_win": round(avg_win, 2),
                    "avg_loss": round(avg_loss, 2),
                    "max_drawdown": round(max_dd, 2),
                    "total_return": round(sum(profits), 2),
                }

        return self.results

    def print_report(self):
        if not self.results:
            print("نتیجه‌ای نیست")
            return

        print()
        print("=" * 100)
        print("  نتایج بک‌تست")
        print("=" * 100)
        print()
        print("   استراتژی               | معاملات | نرخ برد | میانگین سود | میانگین برد | میانگین باخت | افت حداکثر")
        print("   " + "-" * 96)

        # مرتب‌سازی بر اساس نرخ برد
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]["win_rate"],
            reverse=True,
        )

        for key, r in sorted_results:
            print(
                "   " + key.ljust(22)
                + " | " + str(r["total_trades"]).rjust(7)
                + " | " + "{:>6.1f}%".format(r["win_rate"])
                + " | " + "{:>+7.2f}%".format(r["avg_profit"]).rjust(11)
                + " | " + "{:>+7.2f}%".format(r["avg_win"]).rjust(11)
                + " | " + "{:>+7.2f}%".format(r["avg_loss"]).rjust(12)
                + " | " + "{:>7.2f}%".format(r["max_drawdown"]).rjust(10)
            )

        print("=" * 100)

        # بهترین استراتژی
        best = sorted_results[0]
        print()
        print("  بهترین استراتژی: " + best[0])
        print("     - نرخ برد: " + str(best[1]["win_rate"]) + "%")
        print("     - میانگین سود هر معامله: " + str(best[1]["avg_profit"]) + "%")
        print("     - تعداد معاملات: " + str(best[1]["total_trades"]))
        print()

    def save(self):
        date = datetime.now().strftime("%Y-%m-%d")
        out_file = DATA_DIR / ("backtest_" + date + ".json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print("ذخیره شد: " + str(out_file))
        return out_file


# ======================================================================
# اجرا
# ======================================================================

if __name__ == "__main__":
    bt = StrategyBacktest()
    bt.run()
    bt.print_report()
    bt.save()
    print()
    print("تمام!")

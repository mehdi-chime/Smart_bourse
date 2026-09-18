"""
ai/backtest_optimizer.py
بهینه‌ساز بک‌تست - شبیه‌سازی استراتژی‌ها روی داده‌های تاریخی
نسخه ۲.۰ - با مدیریت سرمایه و کارمزد
"""

import sys
import os
from pathlib import Path

# ========== تنظیم مسیر ==========
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd
import numpy as np
from datetime import datetime
from history.history_database import HistoryDatabase
from database.database import Database


class BacktestOptimizer:
    def __init__(self, symbol, initial_cash=100_000_000, trade_fee=0.0125):
        """
        پارامترها:
        - symbol: نماد مورد نظر (مثل 'خگستر')
        - initial_cash: سرمایه اولیه (پیش‌فرض ۱۰۰ میلیون تومان)
        - trade_fee: کارمزد معاملات (پیش‌فرض ۱.۲۵٪)
        """
        self.symbol = symbol
        self.initial_cash = initial_cash
        self.trade_fee = trade_fee
        self.data = None
        self.results = {}

    def load_data(self, days=None):
        """بارگذاری داده‌های تاریخی از دیتابیس"""
        history_db = HistoryDatabase()
        history_db.connect()
        
        if days:
            stocks = history_db.get_history(self.symbol, days)
        else:
            stocks = history_db.get_history(self.symbol, 9999)  # همه داده‌ها
        
        history_db.close()

        if not stocks:
            print(f"❌ داده‌ای برای {self.symbol} پیدا نشد.")
            return False

        # تبدیل به DataFrame
        self.data = pd.DataFrame([{
            'date': s.trade_date,
            'open': s.open_price,
            'high': s.high_price,
            'low': s.low_price,
            'close': s.close_price,
            'volume': s.volume
        } for s in stocks])

        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.sort_values('date').reset_index(drop=True)
        print(f"✅ {len(self.data)} روز داده برای {self.symbol} بارگذاری شد.")
        return True

    def run_strategy(self, buy_threshold=-3, sell_threshold=3, risk_percent=0.2):
        """
        اجرای استراتژی با آستانه‌های مشخص و مدیریت سرمایه
        - buy_threshold: درصد منفی برای خرید (مثلاً -۳)
        - sell_threshold: درصد مثبت برای فروش (مثلاً +۳)
        - risk_percent: درصد سرمایه‌ای که در هر معامله ریسک می‌کنیم (پیش‌فرض ۲۰٪)
        """
        if self.data is None or len(self.data) < 60:
            return None

        cash = self.initial_cash
        position = 0
        trades = []
        total_profit = 0

        self.data['change'] = self.data['close'].pct_change() * 100

        for i in range(60, len(self.data)):
            close_price = self.data.loc[i, 'close']
            change = self.data.loc[i, 'change']

            if change <= buy_threshold and position == 0:
                # محاسبه حجم بر اساس درصد ریسک
                risk_amount = cash * risk_percent
                max_volume = risk_amount / (close_price * (1 + self.trade_fee))
                volume = int(max_volume)
                if volume > 0:
                    cost = volume * close_price * (1 + self.trade_fee)
                    cash -= cost
                    position += volume
                    trades.append({
                        'date': self.data.loc[i, 'date'],
                        'type': 'BUY',
                        'price': close_price,
                        'volume': volume,
                        'cost': cost
                    })

            elif change >= sell_threshold and position > 0:
                revenue = position * close_price * (1 - self.trade_fee)
                profit = revenue - (position * self.data.loc[i-1, 'close'])
                cash += revenue
                trades.append({
                    'date': self.data.loc[i, 'date'],
                    'type': 'SELL',
                    'price': close_price,
                    'volume': position,
                    'revenue': revenue,
                    'profit': profit
                })
                total_profit += profit
                position = 0

        final_value = cash + (position * self.data.iloc[-1]['close'] if position > 0 else 0)

        win_trades = [t for t in trades if t.get('profit', 0) > 0]
        loss_trades = [t for t in trades if t.get('profit', 0) < 0]

        return {
            'total_trades': len(trades),
            'win_trades': len(win_trades),
            'loss_trades': len(loss_trades),
            'win_rate': len(win_trades) / len(trades) * 100 if trades else 0,
            'total_profit': total_profit,
            'final_value': final_value,
            'return_percent': ((final_value - self.initial_cash) / self.initial_cash) * 100,
            'trades': trades,
            'buy_threshold': buy_threshold,
            'sell_threshold': sell_threshold,
            'risk_percent': risk_percent
        }

    def optimize(self, buy_range=(-5, 0), sell_range=(1, 6), step=0.5, risk_percent=0.2):
        """بهینه‌سازی آستانه‌ها با مدیریت سرمایه"""
        best_result = None
        best_score = -999999

        print(f"🔍 بهینه‌سازی آستانه‌ها برای {self.symbol}...")
        print(f"   محدوده خرید: {buy_range[0]} تا {buy_range[1]}")
        print(f"   محدوده فروش: {sell_range[0]} تا {sell_range[1]}")
        print(f"   درصد ریسک در هر معامله: {risk_percent * 100:.0f}٪")

        buy_values = np.arange(buy_range[0], buy_range[1] + step, step)
        sell_values = np.arange(sell_range[0], sell_range[1] + step, step)

        total_tests = len(buy_values) * len(sell_values)
        test_count = 0

        for buy in buy_values:
            for sell in sell_values:
                test_count += 1
                result = self.run_strategy(buy_threshold=buy, sell_threshold=sell, risk_percent=risk_percent)
                if result:
                    # امتیاز: ترکیبی از سود و درصد برد
                    score = (result['return_percent'] * 0.6) + (result['win_rate'] * 0.4)
                    if score > best_score:
                        best_score = score
                        best_result = result
                        best_result['score'] = score

        print(f"✅ {total_tests} حالت تست شد.")
        return best_result

    def report(self, result):
        """گزارش خروجی"""
        if not result:
            return "❌ نتیجه‌ای برای گزارش وجود ندارد."

        lines = [
            "=" * 60,
            f"📊 گزارش بک‌تست - {self.symbol}",
            "=" * 60,
            f"سرمایه اولیه: {self.initial_cash:,.0f} تومان",
            f"آستانه خرید: {result.get('buy_threshold', 'N/A')}٪",
            f"آستانه فروش: {result.get('sell_threshold', 'N/A')}٪",
            f"درصد ریسک در هر معامله: {result.get('risk_percent', 0) * 100:.0f}٪",
            "",
            "📈 آمار معاملات:",
            f"   تعداد کل معاملات: {result.get('total_trades', 0)}",
            f"   معاملات برنده: {result.get('win_trades', 0)}",
            f"   معاملات بازنده: {result.get('loss_trades', 0)}",
            f"   درصد برد: {result.get('win_rate', 0):.1f}٪",
            "",
            "💰 عملکرد مالی:",
            f"   سود کل: {result.get('total_profit', 0):,.0f} تومان",
            f"   ارزش نهایی: {result.get('final_value', 0):,.0f} تومان",
            f"   بازده کل: {result.get('return_percent', 0):.2f}٪",
            ""
        ]

        if result.get('trades'):
            lines.append("📝 تاریخچه معاملات (۱۰ مورد آخر):")
            for t in result['trades'][-10:]:
                if t['type'] == 'BUY':
                    lines.append(f"   🟢 خرید {t['volume']} سهم در {t['price']:,.0f} ریال")
                else:
                    profit = t.get('profit', 0)
                    emoji = "🟢" if profit > 0 else "🔴"
                    lines.append(f"   {emoji} فروش {t['volume']} سهم در {t['price']:,.0f} | سود: {profit:,.0f}")

        lines.append("=" * 60)
        return "\n".join(lines)


# ========== بخش تست ==========
if __name__ == "__main__":
    optimizer = BacktestOptimizer("خگستر", initial_cash=100_000_000)

    if optimizer.load_data():
        # استراتژی پیش‌فرض با ۲۰٪ ریسک
        result = optimizer.run_strategy(buy_threshold=-3, sell_threshold=3, risk_percent=0.2)
        if result:
            print(optimizer.report(result))

        # بهینه‌سازی با ۲۰٪ ریسک
        print("\n" + "=" * 60)
        print("🚀 شروع بهینه‌سازی...")
        print("=" * 60)
        best = optimizer.optimize(buy_range=(-5, -1), sell_range=(1, 5), step=0.5, risk_percent=0.2)
        if best:
            print("\n🏆 بهترین نتیجه:")
            print(optimizer.report(best))

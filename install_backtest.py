# install_backtest.py
# فاز ۱۱: بک‌تست کامل
# اجرا: python install_backtest.py

import os
import sys
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
sys.path.insert(0, str(PROJECT_ROOT))


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


# ═══════════════════════════════════════════════════════════
# backtest_v2.py
# ═══════════════════════════════════════════════════════════

BACKTEST_V2 = '''"""
Project : Smart_Bourse
File    : backtest_v2.py
Version : 1.0.0

Description :
    بک‌تست استراتژی -3/+3 با داده‌های تاریخی
"""

import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

DB_FILE = PROJECT_ROOT / "data" / "smart_bourse_v2.db"


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


class Backtest:

    def __init__(self, initial_cash=100_000_000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = []
        self.trades = []
        self.conn = sqlite3.connect(str(DB_FILE))
        self.cursor = self.conn.cursor()

    def get_stock_data(self, symbol, days=90):
        """دریافت داده‌ی تاریخی"""
        self.cursor.execute("""
            SELECT date, open, high, low, close, volume
            FROM price_history
            WHERE symbol = ?
            ORDER BY date DESC
            LIMIT ?
        """, (symbol, days))
        
        rows = self.cursor.fetchall()
        rows.reverse()
        
        return [
            {
                "date": r[0],
                "open": r[1],
                "high": r[2],
                "low": r[3],
                "close": r[4],
                "volume": r[5],
            }
            for r in rows
        ]

    def run_strategy(self, symbol, buy_threshold=-3, sell_threshold=3):
        """اجرای استراتژی -3/+3"""
        data = self.get_stock_data(symbol, days=90)
        
        if len(data) < 30:
            return None
        
        for i in range(len(data) - 1):
            today = data[i]
            tomorrow = data[i + 1]
            
            current_price = today["close"]
            next_price = tomorrow["close"]
            
            change_pct = (next_price - current_price) / current_price * 100
            
            # سیگنال خرید
            if change_pct <= buy_threshold:
                # خرید
                qty = int(self.cash * 0.1 / current_price)  # 10% از سرمایه
                if qty > 0:
                    cost = qty * current_price
                    self.cash -= cost
                    self.positions.append({
                        "symbol": symbol,
                        "buy_price": current_price,
                        "qty": qty,
                        "buy_date": today["date"],
                    })
            
            # سیگنال فروش
            for pos in self.positions[:]:
                if pos["symbol"] != symbol:
                    continue
                
                profit_pct = (current_price - pos["buy_price"]) / pos["buy_price"] * 100
                
                if profit_pct >= sell_threshold:
                    # فروش
                    revenue = pos["qty"] * current_price
                    self.cash += revenue
                    
                    profit = revenue - (pos["qty"] * pos["buy_price"])
                    
                    self.trades.append({
                        "symbol": symbol,
                        "buy_price": pos["buy_price"],
                        "sell_price": current_price,
                        "qty": pos["qty"],
                        "profit": profit,
                        "profit_pct": profit_pct,
                        "buy_date": pos["buy_date"],
                        "sell_date": today["date"],
                    })
                    
                    self.positions.remove(pos)
        
        return {
            "symbol": symbol,
            "trades": len(self.trades),
            "cash": self.cash,
        }

    def report(self):
        """گزارش بک‌تست"""
        total_profit = sum(t["profit"] for t in self.trades)
        win_trades = [t for t in self.trades if t["profit"] > 0]
        loss_trades = [t for t in self.trades if t["profit"] <= 0]
        
        safe_print("")
        safe_print("=" * 70)
        safe_print("  📊 بک‌تست - استراتژی -3/+3")
        safe_print("=" * 70)
        safe_print("")
        safe_print(f"  سرمایه اولیه: {self.initial_cash:,}")
        safe_print(f"  سرمایه فعلی:  {int(self.cash):,}")
        safe_print(f"  سود/ضرر:      {int(total_profit):,}")
        safe_print(f"  بازدهی:       {total_profit / self.initial_cash * 100:.2f}%")
        safe_print("")
        safe_print(f"  تعداد معاملات: {len(self.trades)}")
        safe_print(f"  موفق:          {len(win_trades)}")
        safe_print(f"  ناموفق:        {len(loss_trades)}")
        
        if self.trades:
            win_rate = len(win_trades) / len(self.trades) * 100
            safe_print(f"  نرخ برد:       {win_rate:.1f}%")
        
        safe_print("")
        safe_print("=" * 70)
        safe_print("")


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 فاز ۱۱: بک‌تست کامل")
    safe_print("=" * 80)
    safe_print("")

    # چک دیتابیس
    if not DB_FILE.exists():
        safe_print(f"  ❌ دیتابیس پیدا نشد: {DB_FILE}")
        return

    # نمادها
    symbols = ["foolad", "khodro", "khegostar", "femeli", "khepars"]
    
    safe_print("  🔍 نمادها:")
    for s in symbols:
        safe_print(f"     - {s}")
    safe_print("")

    # بک‌تست
    safe_print("  🧪 اجرای بک‌تست...")
    safe_print("")

    bt = Backtest(initial_cash=100_000_000)
    
    for symbol in symbols:
        result = bt.run_strategy(symbol)
        if result:
            safe_print(f"     {symbol}: {result['trades']} معامله")

    # گزارش
    bt.report()

    # ذخیره
    output = PROJECT_ROOT / "reports" / "backtest_v2.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    
    report = {
        "date": datetime.now().isoformat(),
        "initial_cash": bt.initial_cash,
        "final_cash": bt.cash,
        "total_trades": len(bt.trades),
        "trades": bt.trades[-50:],
    }
    
    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    safe_print(f"  💾 گزارش: {output}")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()
'''


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return len(content)


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  📊 فاز ۱۱: بک‌تست کامل")
    safe_print("=" * 80)
    safe_print("")

    # ۱. ساخت backtest_v2.py
    safe_print("  📄 ساخت backtest_v2.py...")
    size = write_file(PROJECT_ROOT / "backtest_v2.py", BACKTEST_V2)
    safe_print(f"     ✅ {size:,} b")
    safe_print("")

    # ۲. تست
    safe_print("  🧪 تست بک‌تست...")
    import subprocess
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "backtest_v2.py")],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
        errors="ignore",
    )
    
    for line in result.stdout.split("\\n"):
        if line.strip():
            safe_print(f"     {line}")
    safe_print("")

    # ۳. خلاصه
    safe_print("=" * 80)
    safe_print("  📊 خلاصه:")
    safe_print("=" * 80)
    safe_print("")
    safe_print("  ✅ backtest_v2.py")
    safe_print("  ✅ reports/backtest_v2.json")
    safe_print("")
    safe_print("  🎯 دستور:")
    safe_print("     python backtest_v2.py")
    safe_print("")
    safe_print("=" * 80)
    safe_print("  ✅ تمام!")
    safe_print("=" * 80)
    safe_print("")


if __name__ == "__main__":
    main()

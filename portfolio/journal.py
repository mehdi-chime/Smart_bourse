"""
Project : Smart_Bourse
File    : portfolio/journal.py
Version : 1.1.0
Description :
    ژورنال معاملاتی — با نرمال‌سازی حروف فارسی/عربی
"""

import json
from datetime import datetime
from pathlib import Path


def normalize_symbol(s):
    """نرمال‌سازی حروف فارسی/عربی"""
    if not s:
        return s
    # عربی → فارسی
    replacements = {
        "\u0643": "\u06a9",  # ك → ک
        "\u064a": "\u06cc",  # ي → ی
        "\u0649": "\u06cc",  # ى → ی
        "\u0629": "\u0647",  # ة → ه
        "\u06c0": "\u0647",  # ۀ → ه
        "\u0640": "",         # ـ (کشیدگی) حذف
    }
    result = s
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result.strip()


class TradeJournal:

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data" / "portfolio"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.trades_file = self.data_dir / "trades.jsonl"
        self.open_file = self.data_dir / "open_positions.json"
        self.closed_file = self.data_dir / "closed_positions.json"

        self.open_positions = self._load_json(self.open_file)
        self.closed_positions = self._load_json(self.closed_file)

    def _load_json(self, path):
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _save_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _append_trade(self, trade):
        with open(self.trades_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(trade, ensure_ascii=False) + "\n")

    def buy(self, symbol, price, quantity, reason="", date=None):
        symbol = normalize_symbol(symbol)
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        position = {
            "symbol": symbol,
            "buy_date": date,
            "buy_price": float(price),
            "quantity": int(quantity),
            "invested": float(price) * int(quantity),
            "reason": reason,
            "status": "OPEN",
            "created_at": datetime.now().isoformat(),
        }

        self.open_positions.append(position)
        self._save_json(self.open_file, self.open_positions)

        trade = {"action": "BUY", **position}
        self._append_trade(trade)

        print("OK | خرید ثبت شد: " + symbol + " | " + str(quantity) + " × " + "{:,}".format(int(price)))
        return position

    def sell(self, symbol, price, quantity=None, reason="", date=None):
        symbol = normalize_symbol(symbol)
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        idx = None
        for i, p in enumerate(self.open_positions):
            if normalize_symbol(p["symbol"]) == symbol and p["status"] == "OPEN":
                idx = i
                break

        if idx is None:
            print("X | پوزیشن باز برای " + symbol + " پیدا نشد")
            print("   پوزیشن‌های باز:")
            for p in self.open_positions:
                print("     - " + str(p["symbol"]))
            return None

        position = self.open_positions[idx]
        sell_qty = int(quantity) if quantity else position["quantity"]

        if sell_qty > position["quantity"]:
            print("X | تعداد فروش بیشتر از تعداد خرید است")
            return None

        sell_price = float(price)
        buy_price = float(position["buy_price"])
        invested = buy_price * sell_qty
        proceeds = sell_price * sell_qty
        profit = proceeds - invested
        profit_pct = (profit / invested * 100) if invested > 0 else 0

        closed = {
            "symbol": symbol,
            "buy_date": position["buy_date"],
            "sell_date": date,
            "buy_price": buy_price,
            "sell_price": sell_price,
            "quantity": sell_qty,
            "invested": invested,
            "proceeds": proceeds,
            "profit": profit,
            "profit_pct": round(profit_pct, 2),
            "buy_reason": position.get("reason", ""),
            "sell_reason": reason,
            "hold_days": self._days_between(position["buy_date"], date),
            "closed_at": datetime.now().isoformat(),
        }

        self.closed_positions.append(closed)
        self._save_json(self.closed_file, self.closed_positions)

        trade = {"action": "SELL", **closed}
        self._append_trade(trade)

        position["quantity"] -= sell_qty
        if position["quantity"] <= 0:
            position["status"] = "CLOSED"
            self.open_positions.pop(idx)
        else:
            position["invested"] = position["buy_price"] * position["quantity"]

        self._save_json(self.open_file, self.open_positions)

        emoji = "سود" if profit > 0 else "ضرر"
        print("OK | فروش ثبت شد: " + symbol + " | " + emoji + ": " + "{:,.0f}".format(profit) + " (" + "{:.2f}%".format(profit_pct) + ")")
        return closed

    @staticmethod
    def _days_between(d1, d2):
        try:
            from datetime import datetime as dt
            a = dt.strptime(d1, "%Y-%m-%d")
            b = dt.strptime(d2, "%Y-%m-%d")
            return (b - a).days
        except Exception:
            return 0

    def show_open(self):
        if not self.open_positions:
            print("هیچ پوزیشن بازی نداری")
            return

        print()
        print("=" * 80)
        print("  پوزیشن‌های باز (" + str(len(self.open_positions)) + ")")
        print("=" * 80)
        print("   نماد       | تعداد    | قیمت خرید | سرمایه    | تاریخ")
        print("   " + "-" * 76)

        for p in self.open_positions:
            print(
                "   " + str(p["symbol"])[:10].ljust(10)
                + " | " + str(p["quantity"]).rjust(8)
                + " | " + "{:,}".format(int(p["buy_price"])).rjust(9)
                + " | " + "{:,}".format(int(p["invested"])).rjust(9)
                + " | " + str(p["buy_date"])
            )

    def show_closed(self, last=20):
        if not self.closed_positions:
            print("هیچ معامله‌ی بسته‌شده‌ای نداری")
            return

        print()
        print("=" * 100)
        print("  معاملات بسته‌شده (آخرین " + str(last) + ")")
        print("=" * 100)
        print("   نماد       | خرید    | فروش    | تعداد  | سود       | درصد  | روز")
        print("   " + "-" * 96)

        items = self.closed_positions[-last:]
        for c in items:
            status = "+" if c["profit"] > 0 else "-"
            print(
                "   " + str(c["symbol"])[:10].ljust(10)
                + " | " + "{:,}".format(int(c["buy_price"])).rjust(7)
                + " | " + "{:,}".format(int(c["sell_price"])).rjust(7)
                + " | " + str(c["quantity"]).rjust(6)
                + " | " + status + " " + "{:,.0f}".format(abs(c["profit"])).rjust(10)
                + " | " + "{:>6.2f}%".format(c["profit_pct"])
                + " | " + str(c["hold_days"]).rjust(4)
            )

    def stats(self):
        closed = self.closed_positions
        if not closed:
            return {
                "total_trades": 0,
                "open_positions": len(self.open_positions),
                "closed_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "total_profit": 0,
                "total_invested": 0,
                "return_pct": 0,
                "best_trade": None,
                "worst_trade": None,
            }

        wins = [c for c in closed if c["profit"] > 0]
        losses = [c for c in closed if c["profit"] < 0]
        total_profit = sum(c["profit"] for c in closed)
        total_invested = sum(c["invested"] for c in closed)

        best = max(closed, key=lambda x: x["profit"])
        worst = min(closed, key=lambda x: x["profit"])

        return {
            "total_trades": len(closed),
            "open_positions": len(self.open_positions),
            "closed_trades": len(closed),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": round(len(wins) / len(closed) * 100, 1) if closed else 0,
            "total_profit": total_profit,
            "total_invested": total_invested,
            "return_pct": round(total_profit / total_invested * 100, 2) if total_invested > 0 else 0,
            "best_trade": best,
            "worst_trade": worst,
        }

    def report(self):
        s = self.stats()

        print()
        print("=" * 70)
        print("  گزارش پرتفوی Smart_Bourse")
        print("=" * 70)
        print()
        print("پوزیشن‌های باز      : " + str(s["open_positions"]))
        print("معاملات بسته‌شده    : " + str(s["closed_trades"]))
        print("نرخ موفقیت         : " + str(s["win_rate"]) + "%  (" + str(s["wins"]) + " برد / " + str(s["losses"]) + " باخت)")
        print()

        if s["closed_trades"] > 0:
            status = "سود" if s["total_profit"] > 0 else "ضرر"
            print("سود کل              : " + status + " " + "{:,.0f}".format(s["total_profit"]) + " تومان")
            print("بازدهی کل           : " + "{:.2f}%".format(s["return_pct"]))
            print()

            if s["best_trade"]:
                b = s["best_trade"]
                print("بهترین معامله      : " + str(b["symbol"]) + "  " + "{:+,.0f}".format(b["profit"]) + "  (" + "{:.1f}%".format(b["profit_pct"]) + ")")

            if s["worst_trade"]:
                w = s["worst_trade"]
                print("بدترین معامله      : " + str(w["symbol"]) + "  " + "{:+,.0f}".format(w["profit"]) + "  (" + "{:.1f}%".format(w["profit_pct"]) + ")")

        print("=" * 70)
        print()


if __name__ == "__main__":
    import sys

    journal = TradeJournal()

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "open":
            journal.show_open()
        elif cmd == "closed":
            journal.show_closed()
        elif cmd == "report":
            journal.report()
        elif cmd == "buy" and len(sys.argv) >= 5:
            journal.buy(
                symbol=sys.argv[2],
                price=float(sys.argv[3]),
                quantity=int(sys.argv[4]),
                reason=sys.argv[5] if len(sys.argv) > 5 else "",
            )
        elif cmd == "sell" and len(sys.argv) >= 4:
            journal.sell(
                symbol=sys.argv[2],
                price=float(sys.argv[3]),
                quantity=int(sys.argv[4]) if len(sys.argv) > 4 else None,
                reason=sys.argv[5] if len(sys.argv) > 5 else "",
            )
        else:
            print("دستور نامعتبر")
    else:
        journal.report()
        journal.show_open()
        journal.show_closed()

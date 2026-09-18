"""
Project : Smart_Bourse
File    : real_flow_filter.py
Version : 7.0.0
Author  : Mehdi Jalali + Assistant

Description :
    فیلتر جریان پول حقیقی + ذخیره‌ی تاریخچه
"""

import json
from datetime import datetime
from pathlib import Path

import algotik_tse as att
import pandas as pd


# ======================================================================
# تنظیمات
# ======================================================================

SAFE_BUY_THRESHOLD = 5.0
SAFE_SELL_THRESHOLD = 0.2
MIN_REAL_VOLUME = 50_000
EXPORT_EXCEL = True

COL_BUY_REAL = "Vol_buy_retail"
COL_SELL_REAL = "Vol_sell_retail"
COL_BUY_REAL_COUNT = "N_buy_retail"
COL_SELL_REAL_COUNT = "N_sell_retail"

KEEP_COLUMNS = [
    "Symbol", "Name", "Last", "Close", "Yesterday",
    "Value", "Volume", "TradeCount",
    "Vol_buy_retail", "Vol_sell_retail",
    "N_buy_retail", "N_sell_retail",
    "NetIndividualVolume", "NetLegalVolume",
    "SectorCode", "trade_date",
    "ratio", "category",
]


# ======================================================================
# کلاس اصلی
# ======================================================================

class RealFlowFilter:

    def __init__(
        self,
        safe_buy_threshold: float = SAFE_BUY_THRESHOLD,
        safe_sell_threshold: float = SAFE_SELL_THRESHOLD,
        min_real_volume: int = MIN_REAL_VOLUME,
        data_dir: str = None,
    ):
        self.safe_buy_threshold = safe_buy_threshold
        self.safe_sell_threshold = safe_sell_threshold
        self.min_real_volume = min_real_volume

        # مسیر مطلق: همیشه data/ تو ریشه پروژه
        if data_dir is None:
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 مسیر داده: {self.data_dir}")

        self.df = None
        self.safe_buy = []
        self.safe_sell = []
        self.queue_buy = []
        self.normal = []

    # ------------------------------------------------------------------
    # دریافت داده
    # ------------------------------------------------------------------

    def fetch_data(self):
        print("📡 دریافت داده‌ی زنده‌ی کل بازار ...")
        df = att.get_live_market()
        print(f"✅ {len(df)} ردیف دریافت شد")

        if "InstrumentType" in df.columns:
            stocks = df[df["InstrumentType"] == 300].copy()
            print(f"✅ {len(stocks)} سهم عادی جدا شد")
            df = stocks

        # حذف حق تقدم‌ها
        before = len(df)
        df = df[~df["Symbol"].astype(str).str.endswith("3")]
        df = df[~df["Symbol"].astype(str).str.endswith("ح")]
        removed = before - len(df)
        if removed > 0:
            print(f"✅ {removed} حق تقدم حذف شد")

        if "is_today_trade_date" in df.columns:
            today_df = df[df["is_today_trade_date"] == True].copy()
            if len(today_df) > 0:
                print(f"✅ {len(today_df)} نماد امروز معامله شدن")
                df = today_df
            else:
                print("⚠️  امروز معامله‌ای ثبت نشده — از آخرین روز معاملاتی استفاده می‌شود")

        self.df = df
        return df

    # ------------------------------------------------------------------
    # محاسبه نسبت
    # ------------------------------------------------------------------

    @staticmethod
    def compute_ratio(buy_vol, sell_vol):
        buy_vol = float(buy_vol or 0)
        sell_vol = float(sell_vol or 0)
        if sell_vol > 0:
            return buy_vol / sell_vol
        if buy_vol > 0:
            return float("inf")
        return 0.0

    def add_ratio_column(self):
        self.df["ratio"] = self.df.apply(
            lambda r: self.compute_ratio(r[COL_BUY_REAL], r[COL_SELL_REAL]),
            axis=1,
        )
        self.df["ratio"] = self.df["ratio"].replace(float("inf"), 9999.0)

    # ------------------------------------------------------------------
    # دسته‌بندی
    # ------------------------------------------------------------------

    def classify_all(self):
        df = self.df

        df = df[
            (df[COL_BUY_REAL] >= self.min_real_volume)
            | (df[COL_SELL_REAL] >= self.min_real_volume)
        ].copy()
        print(f"📊 بعد از فیلتر حجم ({self.min_real_volume:,}): {len(df)} نماد")

        queue_mask = (df[COL_SELL_REAL] == 0) & (df[COL_BUY_REAL] > 0)
        self.queue_buy = df[queue_mask].to_dict("records")

        rest = df[~queue_mask]

        self.safe_buy = rest[rest["ratio"] >= self.safe_buy_threshold].to_dict("records")
        self.safe_sell = rest[rest["ratio"] <= self.safe_sell_threshold].to_dict("records")
        self.normal = rest[
            (rest["ratio"] > self.safe_sell_threshold)
            & (rest["ratio"] < self.safe_buy_threshold)
        ].to_dict("records")

    # ------------------------------------------------------------------
    # گزارش
    # ------------------------------------------------------------------

    def _print_section(self, title, items, icon):
        print()
        print("=" * 110)
        print(f"{icon}  {title}  ({len(items)} نماد)")
        print("=" * 110)
        if not items:
            print("   (خالی)")
            return

        items_sorted = sorted(items, key=lambda x: x["ratio"], reverse=True)

        print(
            f"   {'نماد':<12} | {'قیمت':>10} | {'نسبت':>8} | "
            f"{'خرید حقیقی':>15} | {'فروش حقیقی':>15} | {'ارزش (میلیارد)':>15}"
        )
        print("   " + "-" * 106)

        for it in items_sorted:
            symbol = str(it.get("Symbol", "?"))[:12]
            last = it.get("Last", 0) or 0
            value = it.get("Value", 0) or 0
            value_b = value / 1_000_000_000 if value else 0

            print(
                f"   {symbol:<12} | "
                f"{int(last):>10,} | "
                f"{it['ratio']:>8.2f} | "
                f"{int(it[COL_BUY_REAL]):>15,} | "
                f"{int(it[COL_SELL_REAL]):>15,} | "
                f"{value_b:>15.2f}"
            )

    def report(self):
        print()
        print("█" * 110)
        print("█" + "  گزارش فیلتر جریان پول حقیقی (Real Flow Filter)  ".center(108) + "█")
        print("█" * 110)
        print(f"📅 تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"📊 آستانه‌ها: SAFE_BUY >= {self.safe_buy_threshold} | "
              f"SAFE_SELL <= {self.safe_sell_threshold} | "
              f"حداقل حجم: {self.min_real_volume:,}")

        self._print_section("SAFE_BUY — سهام امن برای خرید", self.safe_buy, "🟢")
        self._print_section("SAFE_SELL — سهام امن برای فروش", self.safe_sell, "🔴")
        self._print_section("QUEUE_BUY — صف خرید (فروش حقیقی صفر)", self.queue_buy, "🟡")

        print()
        print("=" * 110)
        print("📊 خلاصه:")
        print(f"   🟢 SAFE_BUY  : {len(self.safe_buy)}")
        print(f"   🔴 SAFE_SELL : {len(self.safe_sell)}")
        print(f"   🟡 QUEUE_BUY : {len(self.queue_buy)}")
        print(f"   ⚪ NORMAL    : {len(self.normal)}")
        print("=" * 110)

    # ------------------------------------------------------------------
    # ابزارهای کمکی
    # ------------------------------------------------------------------

    def _clean_records(self, records):
        out = []
        for r in records:
            d = {}
            for k, v in r.items():
                try:
                    if pd.isna(v):
                        d[k] = None
                    elif hasattr(v, "item"):
                        d[k] = v.item()
                    elif isinstance(v, (int, float, str, bool)) or v is None:
                        d[k] = v
                    else:
                        d[k] = str(v)
                except Exception:
                    d[k] = str(v)
            out.append(d)
        return out

    def _to_clean_df(self, records):
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)

        cols = [c for c in KEEP_COLUMNS if c in df.columns]
        if cols:
            df = df[cols]

        for col in df.columns:
            if df[col].dtype == "object" and len(df) > 0:
                try:
                    first = df[col].iloc[0]
                    if hasattr(first, "tzinfo") and first.tzinfo is not None:
                        df[col] = df[col].astype(str)
                except Exception:
                    pass

        return df

    # ------------------------------------------------------------------
    # ذخیره
    # ------------------------------------------------------------------

    def _get_trade_date(self):
        """تاریخ معاملاتی رو از داده استخراج کن"""
        if self.df is not None and "trade_date" in self.df.columns:
            dates = self.df["trade_date"].dropna().unique()
            if len(dates) > 0:
                return str(dates[0])
        return datetime.now().strftime("%Y-%m-%d")

    def save(self):
        trade_date = self._get_trade_date()
        out_dir = self.data_dir / "real_flow"
        out_dir.mkdir(parents=True, exist_ok=True)

        # ---------- JSON روزانه ----------
        json_file = out_dir / f"real_flow_{trade_date}.json"
        payload = {
            "date": trade_date,
            "generated_at": datetime.now().isoformat(),
            "thresholds": {
                "safe_buy": self.safe_buy_threshold,
                "safe_sell": self.safe_sell_threshold,
                "min_real_volume": self.min_real_volume,
            },
            "summary": {
                "safe_buy": len(self.safe_buy),
                "safe_sell": len(self.safe_sell),
                "queue_buy": len(self.queue_buy),
                "normal": len(self.normal),
            },
            "safe_buy": self._clean_records(self.safe_buy),
            "safe_sell": self._clean_records(self.safe_sell),
            "queue_buy": self._clean_records(self.queue_buy),
            "normal": self._clean_records(self.normal),
        }
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n💾 JSON ذخیره شد: {json_file}")

        # ---------- Excel ----------
        if EXPORT_EXCEL:
            excel_file = out_dir / f"real_flow_{trade_date}.xlsx"
            try:
                with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                    self._to_clean_df(self.safe_buy).to_excel(
                        writer, sheet_name="SAFE_BUY", index=False)
                    self._to_clean_df(self.safe_sell).to_excel(
                        writer, sheet_name="SAFE_SELL", index=False)
                    self._to_clean_df(self.queue_buy).to_excel(
                        writer, sheet_name="QUEUE_BUY", index=False)
                    self._to_clean_df(self.normal).to_excel(
                        writer, sheet_name="NORMAL", index=False)
                print(f"💾 Excel ذخیره شد: {excel_file}")
            except Exception as e:
                print(f"⚠️  خطا در Excel: {e}")

        # ---------- تاریخچه (JSONL) ----------
        self.save_history(trade_date)

    def save_history(self, trade_date):
        """ذخیره‌ی تاریخچه — هر روز یه خط اضافه می‌شه"""
        history_dir = self.data_dir / "real_flow" / "history"
        history_dir.mkdir(parents=True, exist_ok=True)

        history_file = history_dir / "history.jsonl"

        # یه خط خلاصه برای هر روز
        summary_line = {
            "date": trade_date,
            "generated_at": datetime.now().isoformat(),
            "total_safe_buy": len(self.safe_buy),
            "total_safe_sell": len(self.safe_sell),
            "total_queue_buy": len(self.queue_buy),
            "safe_buy_symbols": [r.get("Symbol") for r in self.safe_buy],
            "safe_sell_symbols": [r.get("Symbol") for r in self.safe_sell],
        }

        # چک کن این تاریخ قبلاً ذخیره شده یا نه
        existing_dates = set()
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        existing_dates.add(d.get("date"))
                    except Exception:
                        pass

        if trade_date in existing_dates:
            # بازنویسی کن (بروزرسانی)
            lines = []
            with open(history_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        d = json.loads(line)
                        if d.get("date") == trade_date:
                            lines.append(json.dumps(summary_line, ensure_ascii=False))
                        else:
                            lines.append(line.strip())
                    except Exception:
                        lines.append(line.strip())
            with open(history_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            print(f"💾 تاریخچه بروزرسانی شد: {history_file}")
        else:
            # اضافه کن
            with open(history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(summary_line, ensure_ascii=False) + "\n")
            print(f"💾 تاریخچه اضافه شد: {history_file}")

        # ---------- فایل جدا برای هر نماد ----------
        symbols_dir = history_dir / "symbols"
        symbols_dir.mkdir(parents=True, exist_ok=True)

        # همه‌ی نمادهایی که SAFE_BUY یا SAFE_SELL یا QUEUE هستن
        all_signals = (
            [(r, "SAFE_BUY") for r in self.safe_buy]
            + [(r, "SAFE_SELL") for r in self.safe_sell]
            + [(r, "QUEUE_BUY") for r in self.queue_buy]
        )

        for record, category in all_signals:
            symbol = str(record.get("Symbol", "unknown"))
            if symbol == "unknown":
                continue

            symbol_file = symbols_dir / f"{symbol}.jsonl"

            entry = {
                "date": trade_date,
                "category": category,
                "ratio": record.get("ratio"),
                "buy_real_volume": record.get(COL_BUY_REAL),
                "sell_real_volume": record.get(COL_SELL_REAL),
                "last_price": record.get("Last"),
                "value": record.get("Value"),
            }

            # چک کن قبلاً ذخیره شده یا نه
            lines = []
            if symbol_file.exists():
                with open(symbol_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            d = json.loads(line)
                            if d.get("date") != trade_date:
                                lines.append(line.strip())
                        except Exception:
                            lines.append(line.strip())

            lines.append(json.dumps(entry, ensure_ascii=False))
            with open(symbol_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

        print(f"💾 تاریخچه‌ی {len(all_signals)} نماد ذخیره شد: {symbols_dir}")

    # ------------------------------------------------------------------
    # اجرا
    # ------------------------------------------------------------------

    def run(self):
        self.fetch_data()
        self.add_ratio_column()
        self.classify_all()
        self.report()
        self.save()


# ======================================================================
# اجرای مستقیم
# ======================================================================

if __name__ == "__main__":
    print("🚀 شروع فیلتر جریان پول حقیقی\n")
    f = RealFlowFilter()
    f.run()
    print("\n🎉 تمام!")

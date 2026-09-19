"""
Project : Smart_Bourse
File    : scanner/market_context.py
Version : 1.2.0
Description :
    بافت بازار — بهینه‌شده (get_live_market فقط ۱ بار)
"""

import json
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


DATA_DIR = PROJECT_ROOT / "data" / "market_context"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class MarketContext:

    def __init__(self):
        self.data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "index": None,
            "breadth": None,
            "currency": None,
            "sectors": [],
            "interpretation": {},
        }
        self._live_market = None

    # ------------------------------------------------------------------

    def _get_live_market(self):
        """get_live_market رو فقط یه بار بگیر و cache کن"""
        if self._live_market is None:
            try:
                self._live_market = att.get_live_market()
            except Exception:
                self._live_market = None
        return self._live_market

    # ------------------------------------------------------------------

    def fetch_index(self):
        """شاخص کل — از get_market_overview"""
        print("   شاخص کل ...", end=" ", flush=True)
        try:
            df = att.get_market_overview()
            if df is None or df.empty:
                print("خالی")
                return
            row = df.iloc[-1]
            total = float(row.get("indexLastValue") or 0)
            total_chg = float(row.get("indexChange") or 0)
            eq = float(row.get("indexEqualWeightedLastValue") or 0)
            state = str(row.get("marketStateTitle") or "")
            prev_total = total - total_chg
            chg_pct = (total_chg / prev_total * 100) if prev_total > 0 else 0

            self.data["index"] = {
                "total": total,
                "total_change": total_chg,
                "total_change_pct": round(chg_pct, 2),
                "equal_weight": eq,
                "state": state,
            }
            print("OK")
        except Exception as e:
            print("خطا: " + str(e)[:60])

    # ------------------------------------------------------------------

    def fetch_breadth(self):
        """عرضه/تقاضا — از live_market cache"""
        print("   عرضه/تقاضا ...", end=" ", flush=True)
        try:
            df = self._get_live_market()
            if df is None or df.empty:
                print("خالی")
                return

            if "InstrumentType" in df.columns:
                df = df[df["InstrumentType"] == 300]

            if "ChangePct" not in df.columns:
                print("ستون نیست")
                return

            changes = df["ChangePct"].dropna()
            adv = int((changes > 0).sum())
            dec = int((changes < 0).sum())
            unch = int((changes == 0).sum())

            self.data["breadth"] = {
                "advancers": adv,
                "decliners": dec,
                "unchanged": unch,
            }
            print("OK (" + str(adv) + "/" + str(dec) + ")")
        except Exception as e:
            print("خطا: " + str(e)[:60])

    # ------------------------------------------------------------------

    def fetch_sectors(self):
        """صنایع — از live_market cache"""
        print("   صنایع برتر ...", end=" ", flush=True)
        try:
            df = self._get_live_market()
            if df is None or df.empty:
                print("خالی")
                return

            if "InstrumentType" in df.columns:
                df = df[df["InstrumentType"] == 300]

            if "SectorCode" not in df.columns or "ChangePct" not in df.columns:
                print("ستون‌ها نیستن")
                return

            df = df[["SectorCode", "ChangePct"]].dropna()
            grouped = df.groupby("SectorCode")["ChangePct"].mean().reset_index()
            grouped = grouped.rename(columns={"ChangePct": "avg_change"})
            grouped = grouped.sort_values("avg_change", ascending=False)

            sectors = []
            for _, r in grouped.head(5).iterrows():
                sectors.append({
                    "name": "صنعت " + str(int(r["SectorCode"])),
                    "change": round(float(r["avg_change"]), 2),
                    "type": "top",
                })
            for _, r in grouped.tail(5).iterrows():
                sectors.append({
                    "name": "صنعت " + str(int(r["SectorCode"])),
                    "change": round(float(r["avg_change"]), 2),
                    "type": "bottom",
                })

            self.data["sectors"] = sectors
            print("OK (" + str(len(grouped)) + " صنعت)")
        except Exception as e:
            print("خطا: " + str(e)[:60])

    # ------------------------------------------------------------------

    def fetch_currency(self):
        """نرخ دلار — با skip اگه کند بود"""
        print("   نرخ دلار ...", end=" ", flush=True)
        try:
            df = att.get_currency()
            if df is None or df.empty:
                print("خالی")
                return
            row = df.iloc[-1]
            usd = None
            for col in ["Close", "close", "Price", "price", "Last", "last"]:
                if col in df.columns:
                    try:
                        usd = float(row[col])
                        break
                    except Exception:
                        pass
            if usd:
                self.data["currency"] = {"usd": usd}
                print("OK")
            else:
                print("ستون نیست")
        except Exception as e:
            print("رد شد: " + str(e)[:40])

    # ------------------------------------------------------------------

    def interpret(self):
        interp = {}

        idx = self.data.get("index") or {}
        chg = idx.get("total_change_pct")
        if chg is not None:
            if chg > 1:
                interp["index"] = "🟢 صعودی قوی"
            elif chg > 0.3:
                interp["index"] = "🟢 صعودی"
            elif chg > -0.3:
                interp["index"] = "🟡 خنثی"
            elif chg > -1:
                interp["index"] = "🔴 نزولی"
            else:
                interp["index"] = "🔴 نزولی شدید"

        b = self.data.get("breadth") or {}
        adv = b.get("advancers") or 0
        dec = b.get("decliners") or 0
        if adv + dec > 0:
            ratio = adv / (adv + dec)
            if ratio > 0.6:
                interp["breadth"] = "🟢 تقاضا قوی"
            elif ratio > 0.4:
                interp["breadth"] = "🟡 متعادل"
            else:
                interp["breadth"] = "🔴 عرضه قوی"

        curr = self.data.get("currency") or {}
        if curr.get("usd"):
            interp["currency"] = "💵 دلار: " + "{:,.0f}".format(curr["usd"])

        score = 0
        if chg is not None:
            if chg > 0.3:
                score += 1
            elif chg < -0.3:
                score -= 1
        if adv > dec * 1.3:
            score += 1
        elif dec > adv * 1.3:
            score -= 1

        if score >= 1:
            interp["overall"] = "🟢 بازار مثبت"
        elif score <= -1:
            interp["overall"] = "🔴 بازار منفی — احتیاط"
        else:
            interp["overall"] = "🟡 بازار خنثی"
        self.data["interpretation"] = interp

    # ------------------------------------------------------------------

    def fetch_all(self):
        print()
        print("دریافت بافت بازار ...")
        self.fetch_index()
        self.fetch_breadth()
        self.fetch_sectors()
        self.fetch_currency()
        self.interpret()

    # ------------------------------------------------------------------

    def report(self):
        print()
        print("=" * 70)
        print("  بافت بازار — Smart_Bourse")
        print("=" * 70)
        print()

        interp = self.data.get("interpretation") or {}
        idx = self.data.get("index") or {}

        if idx.get("total"):
            print("   شاخص کل          : " + "{:,.0f}".format(idx["total"]))
            print("   تغییر            : " + "{:+,.0f}".format(idx["total_change"]) + "  ({:+.2f}%)".format(idx["total_change_pct"]) + "  " + interp.get("index", ""))
            if idx.get("equal_weight"):
                print("   شاخص هم‌وزن      : " + "{:,.0f}".format(idx["equal_weight"]))
            if idx.get("state"):
                print("   وضعیت بازار      : " + idx["state"])

        b = self.data.get("breadth") or {}
        if b.get("advancers") is not None:
            print("   عرضه/تقاضا       : " + str(b.get("advancers", 0)) + " صعودی / " + str(b.get("decliners", 0)) + " نزولی  " + interp.get("breadth", ""))

        if interp.get("currency"):
            print("   " + interp["currency"])

        sectors = self.data.get("sectors") or []
        if sectors:
            tops = [s for s in sectors if s.get("type") == "top"]
            bots = [s for s in sectors if s.get("type") == "bottom"]
            if tops:
                print()
                print("   صنایع برتر:")
                for s in tops:
                    print("      🟢 " + s["name"].ljust(30) + "  " + "{:+.2f}".format(s["change"]))
            if bots:
                print()
                print("   صنایع ضعیف:")
                for s in bots:
                    print("      🔴 " + s["name"].ljust(30) + "  " + "{:+.2f}".format(s["change"]))

        print()
        print("=" * 70)
        print("   " + interp.get("overall", "?"))
        print("=" * 70)

    # ------------------------------------------------------------------

    def save(self):
        out_file = DATA_DIR / ("context_" + self.data["date"] + ".json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
        print()
        print("ذخیره شد: " + str(out_file))
        return out_file


# ======================================================================

if __name__ == "__main__":
    mc = MarketContext()
    mc.fetch_all()
    mc.report()
    mc.save()
    print()
    print("تمام!")


import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


def main():
    print()
    print("=" * 90)
    print("  Find Missing Symbols")
    print("=" * 90)
    print()

    # 1. جستجو تو لیست نمادها
    print("Method 1: Search in get_symbols()")
    print("-" * 90)
    try:
        syms_df = att.get_symbols()
        print("Columns:", syms_df.columns.tolist())
        print("Total:", len(syms_df))
        print()

        # جستجو برای خپارس
        print("Search 'خپارس':")
        for kw in ["خپارس", "خپارس", "خ پارس", "ایران خودرو دیزل"]:
            found = syms_df[syms_df["name"].astype(str).str.contains(kw, na=False, regex=False)]
            if not found.empty:
                for _, r in found.head(5).iterrows():
                    print("   name:", r.get("name"), "| symbol:", r.name, "| id:", r.get("instrument_id"))
        print()

        # جستجو برای احیا
        print("Search 'احیا':")
        for kw in ["احیا", "استیل", "فولاد"]:
            found = syms_df[syms_df["name"].astype(str).str.contains(kw, na=False, regex=False)]
            if not found.empty:
                for _, r in found.head(5).iterrows():
                    print("   name:", r.get("name"), "| symbol:", r.name, "| id:", r.get("instrument_id"))
        print()

        # جستجو برای پیزد
        print("Search 'پیزد':")
        for kw in ["پیزد", "لاستیک یزد", "یزد"]:
            found = syms_df[syms_df["name"].astype(str).str.contains(kw, na=False, regex=False)]
            if not found.empty:
                for _, r in found.head(5).iterrows():
                    print("   name:", r.get("name"), "| symbol:", r.name, "| id:", r.get("instrument_id"))
        print()
    except Exception as e:
        print("   error:", str(e)[:80])

    # 2. جستجو تو market
    print()
    print("Method 2: Search in live market")
    print("-" * 90)
    try:
        df = att.get_live_market()
        if "InstrumentType" in df.columns:
            df = df[df["InstrumentType"] == 300]

        # جستجو برای 'احیا' با 'Name'
        if "Name" in df.columns:
            print("Search in 'Name' column for 'احیا':")
            for kw in ["احیا", "استیل"]:
                found = df[df["Name"].astype(str).str.contains(kw, na=False, regex=False)]
                if not found.empty:
                    for _, r in found.head(5).iterrows():
                        print("   Name:", r.get("Name"), "| Symbol:", r.get("Symbol"))
            print()

            print("Search in 'Name' column for 'پیزد' / 'یزد':")
            for kw in ["پیزد", "لاستیک"]:
                found = df[df["Name"].astype(str).str.contains(kw, na=False, regex=False)]
                if not found.empty:
                    for _, r in found.head(5).iterrows():
                        print("   Name:", r.get("Name"), "| Symbol:", r.get("Symbol"))
            print()

            print("Search in 'Name' column for 'خپارس':")
            for kw in ["خپارس", "پارس خودرو", "ایران خودرو"]:
                found = df[df["Name"].astype(str).str.contains(kw, na=False, regex=False)]
                if not found.empty:
                    for _, r in found.head(5).iterrows():
                        print("   Name:", r.get("Name"), "| Symbol:", r.get("Symbol"))
    except Exception as e:
        print("   error:", str(e)[:80])

    print()
    print("=" * 90)
    print("Send all the above output to me.")
    print("=" * 90)


if __name__ == "__main__":
    main()

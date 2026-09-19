
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


def main():
    print()
    print("=" * 80)
    print("  Symbol Detector - Smart_Bourse")
    print("=" * 80)
    print()

    df = att.get_live_market()
    if df is None or df.empty:
        print("no data")
        return

    if "InstrumentType" in df.columns:
        df = df[df["InstrumentType"] == 300]

    syms = sorted([str(x) for x in df["Symbol"].tolist()])
    print("Total symbols: " + str(len(syms)))
    print()

    # جستجو با کلمات کلیدی
    keywords = {
        "تابان": ["تابان", "تابان"],
        "پکویر": ["پكوير", "پکویر"],
        "سمهریز": ["سمهریز", "سهرمز", "سیمان هرمز"],
        "احیا": ["احیا", "استیل", "احياء"],
        "پیزد": ["پیزد", "لاستیک یزد", "لیزد", "یزد"],
        "خپارس": ["خپارس", "پارس", "پارس خودرو"],
        "فولاد": ["فولاد", "فولاد مبارکه"],
    }

    print("Search results:")
    print("-" * 80)

    for name, terms in keywords.items():
        found = []
        for term in terms:
            matches = [s for s in syms if term in str(s)]
            for m in matches:
                if m not in found:
                    found.append(m)

        if found:
            print("  " + name.ljust(12) + " -> " + ", ".join(found[:10]))
        else:
            print("  " + name.ljust(12) + " -> NOT FOUND")

    print("-" * 80)
    print()
    print("Extra search - startswith:")
    print()

    # جستجو با حرف اول
    for letter in ["ا", "پ", "خ", "س", "ل", "ی", "ح"]:
        matches = [s for s in syms if s.startswith(letter)]
        if matches:
            print("  [" + letter + "] " + ", ".join(matches[:15]))
            print()


if __name__ == "__main__":
    main()

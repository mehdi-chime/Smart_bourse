
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import algotik_tse as att


print()
print("=" * 80)
print("  Search for خپارس (پارس خودرو)")
print("=" * 80)
print()

syms_df = att.get_symbols()
print("Search for 'پارس خودرو':")
found = syms_df[syms_df["name"].astype(str).str.contains("پارس خودرو", na=False, regex=False)]
print(found.to_string() if not found.empty else "  NOT FOUND by name")
print()

print("Search for 'پارس' with symbol starting 'خ':")
for idx, row in syms_df.iterrows():
    sym = str(idx)
    name = str(row.get("name", ""))
    if sym.startswith("خ") and "پارس" in name:
        print("   symbol:", sym, "| name:", name, "| id:", row.get("instrument_id"))
print()

print("All symbols starting with خ:")
df = att.get_live_market()
if "InstrumentType" in df.columns:
    df = df[df["InstrumentType"] == 300]
x_syms = sorted([str(s) for s in df["Symbol"].tolist() if str(s).startswith("خ")])
print("  ", x_syms)
print()

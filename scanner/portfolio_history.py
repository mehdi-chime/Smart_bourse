
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "data" / "portfolio_history"


def main():
    print()
    print("=" * 90)
    print("  Portfolio History Report")
    print("=" * 90)
    print()

    if not DATA_DIR.exists():
        print("  No history yet.")
        return

    files = sorted(DATA_DIR.glob("*.jsonl"))

    if not files:
        print("  No history files.")
        return

    print("  " + "date".ljust(12) + " | " + "time".rjust(8) + " | " + "value (M rials)".rjust(16) + " | " + "change vs previous")
    print("  " + "-" * 86)

    prev_value = None
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            lines = [l.strip() for l in fp if l.strip()]

        # آخرین رکورد هر روز
        if not lines:
            continue

        try:
            last = json.loads(lines[-1])
        except Exception:
            continue

        value = last.get("total_value_m_rials", 0)
        change_str = ""
        if prev_value is not None and prev_value > 0:
            change_pct = (value - prev_value) / prev_value * 100
            sign = "+" if change_pct > 0 else ""
            change_str = sign + "{:.2f}%".format(change_pct)

        print(
            "  " + last["date"].ljust(12)
            + " | " + last["time"].rjust(8)
            + " | " + "{:,.1f}".format(value).rjust(16)
            + " | " + change_str
        )

        prev_value = value

    print("  " + "-" * 86)
    print()
    print("  Total history days: " + str(len(files)))
    print()
    print("=" * 90)


if __name__ == "__main__":
    main()

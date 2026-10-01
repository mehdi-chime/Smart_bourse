from pathlib import Path
from datetime import datetime

# مسیر پروژه
PROJECT_PATH = Path(__file__).resolve().parent

print("=" * 70)
print("       SMART BOURSE - PROJECT DIAGNOSTIC")
print("=" * 70)

print(f"\nProject path:")
print(PROJECT_PATH)

print(f"\nCheck time:")
print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

print("\n" + "=" * 70)
print("PROJECT STRUCTURE")
print("=" * 70)

# پوشه‌ها و فایل‌ها
all_items = sorted(
    PROJECT_PATH.rglob("*"),
    key=lambda x: str(x).lower()
)

for item in all_items:
    # فایل‌ها و پوشه‌های غیرضروری را نشان نده
    if any(part in {".git", "__pycache__", ".venv", "venv"} for part in item.parts):
        continue

    relative = item.relative_to(PROJECT_PATH)

    if item.is_dir():
        print(f"[DIR ] {relative}")
    else:
        size = item.stat().st_size
        print(f"[FILE] {relative}  ({size:,} bytes)")

print("\n" + "=" * 70)
print("PYTHON FILES")
print("=" * 70)

python_files = sorted(PROJECT_PATH.rglob("*.py"))

if not python_files:
    print("No Python files found.")

else:
    for file in python_files:
        if any(part in {".git", "__pycache__", ".venv", "venv"} for part in file.parts):
            continue

        relative = file.relative_to(PROJECT_PATH)

        try:
            lines = file.read_text(encoding="utf-8").splitlines()
            print(f"\n--- {relative} ---")
            print(f"Lines: {len(lines)}")

            # فقط importها و تعریف کلاس/تابع‌ها
            for line in lines:
                stripped = line.strip()

                if (
                    stripped.startswith("import ")
                    or stripped.startswith("from ")
                    or stripped.startswith("class ")
                    or stripped.startswith("def ")
                    or stripped.startswith("async def ")
                ):
                    print("  " + stripped)

        except Exception as e:
            print(f"ERROR reading {relative}: {e}")

print("\n" + "=" * 70)
print("IMPORTANT FILES")
print("=" * 70)

important_files = [
    "main.py",
    "daily_runner.py",
    "project_config.py",
    "README.md",
]

for name in important_files:
    file = PROJECT_PATH / name

    if file.exists():
        print(f"[FOUND] {name}")
    else:
        print(f"[---- ] {name} not found")

print("\n" + "=" * 70)
print("DIAGNOSTIC FINISHED")
print("=" * 70)

input("\nPress Enter to close...")

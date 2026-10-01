# scan_project.py
# این فایل رو تو ریشه smart_bours بذار: F:\python\har roz ba python\smart_bours\scan_project.py
# بعد تو CMD بزن: python scan_project.py
# خروجی: project_report.txt

import os
from pathlib import Path

ROOT = Path(r"F:\python\har roz ba python\smart_bours")
OUTPUT = ROOT / "project_report.txt"

SKIP_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'env', 'node_modules', '.idea', '.vscode'}

def get_docstring(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i > 30:
                    break
                lines.append(line.rstrip())
        return " | ".join([l.strip() for l in lines[:5] if l.strip()])[:200]
    except:
        return ""

def count_lines(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def main():
    report = []
    report.append("=" * 100)
    report.append("SMART_BOURSE PROJECT REPORT")
    report.append("=" * 100)
    report.append("")

    # ۱. ساختار پوشه‌ها
    report.append("## ساختار پوشه‌ها\n")
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel = os.path.relpath(dirpath, ROOT)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        indent = "  " * depth
        name = os.path.basename(dirpath) if rel != "." else "smart_bours"
        report.append(f"{indent}📁 {name}/")
    report.append("")

    # ۲. فایل‌های پایتون
    report.append("## فایل‌های پایتون (Python Files)\n")
    report.append(f"{'مسیر':<60} {'خطوط':>8} {'حجم':>10}  توضیح")
    report.append("-" * 130)

    py_files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith('.py'):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, ROOT)
                py_files.append((rel, full))

    py_files.sort()

    total_lines = 0
    for rel, full in py_files:
        lines = count_lines(full)
        size = os.path.getsize(full)
        doc = get_docstring(full)[:100]
        total_lines += lines
        report.append(f"{rel:<60} {lines:>8} {size:>10}  {doc}")

    report.append("")
    report.append(f"### جمع کل: {len(py_files)} فایل پایتون، {total_lines} خط کد\n")

    # ۳. فایل‌های غیر پایتون مهم
    report.append("## فایل‌های مهم غیرپایتون\n")
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith(('.md', '.txt', '.json', '.csv', '.bat', '.cfg', '.ini', '.toml', '.yaml', '.yml')):
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, ROOT)
                size = os.path.getsize(full)
                report.append(f"  {rel:<70} {size:>10} bytes")

    report.append("")
    report.append("=" * 100)
    report.append("END OF REPORT")
    report.append("=" * 100)

    text = "\n".join(report)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"✅ گزارش ساخته شد: {OUTPUT}")
    print(f"📊 {len(py_files)} فایل پایتون، {total_lines} خط کد")

if __name__ == "__main__":
    main()

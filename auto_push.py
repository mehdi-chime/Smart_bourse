"""
Project : Smart_Bourse
File    : auto_push.py
Version : 3.0.0
Description :
    آپلود خودکار — با فیلتر فایل‌های زائد
"""

import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

EXCLUDE_PATTERNS = [
    "__pycache__", ".pyc", ".pyo", ".bak", ".backup",
    "_OLD.txt", "_old.txt", "smart_bourse.db", "db-journal",
    "smart_bourse.log", "New Text Document",
    "data/history/", "data/real_flow/", "data/ai/",
    "data/market_today.json", "data/watchlist.json",
    "logs/", ".venv", "venv/", ".idea", ".vscode",
    "status.txt",
]


def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, cwd=ROOT,
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def is_excluded(path):
    p = path.replace("\\", "/")
    return any(pat in p for pat in EXCLUDE_PATTERNS)


def main():
    print()
    print("=" * 60)
    print("  🚀 Smart_Bourse Auto Push (v3)")
    print("=" * 60)

    code, _, _ = run("git rev-parse --is-inside-work-tree")
    if code != 0:
        print("❌ مخزن گیت نیست")
        return

    code, out, _ = run("git status --porcelain")
    if not out:
        print()
        print("ℹ️  هیچ تغییری نیست.")
        return

    files, excluded = [], []
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        path = parts[1].strip().strip('"')
        (excluded if is_excluded(path) else files).append(path)

    if not files:
        print()
        print("ℹ️  فقط فایل زائد تغییر کرده.")
        return

    print()
    print("📋 فایل‌های مجاز (" + str(len(files)) + "):")
    for f in files[:15]:
        print("   " + f)
    if len(files) > 15:
        print("   ... و " + str(len(files) - 15) + " فایل دیگه")

    if excluded:
        print()
        print("🚫 نادیده گرفته شده: " + str(len(excluded)) + " فایل")

    print()
    ans = input("➡️  آپلود؟ (y/n): ").strip().lower()
    if ans != "y":
        return

    for f in files:
        run('git add "' + f.replace('"', '\\"') + '"')

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    code, out, err = run('git commit -m "Auto-update: ' + timestamp + '"')
    if code != 0:
        print("❌ خطا: " + err)
        return

    code, out, err = run("git push origin main")
    if code != 0:
        print("❌ خطا: " + err)
        return

    print()
    print("✅ پوش موفق")
    print()


if __name__ == "__main__":
    main()

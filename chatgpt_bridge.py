
from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path


# ============================================================
# SMART_BOURSE - ChatGPT Bridge
# ============================================================

PROJECT_PATH = Path(__file__).resolve().parent

REPORT_DIR = PROJECT_PATH / "reports" / "chatgpt_bridge"
LATEST_REPORT = REPORT_DIR / "latest_report.txt"

REMOTE = "origin"
BRANCH = "main"

EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
}


# ============================================================
# اجرای دستور Git
# ============================================================

def run_git(*args: str):
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_PATH,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )

    return (
        result.returncode,
        result.stdout.strip(),
        result.stderr.strip(),
    )


# ============================================================
# پیدا کردن فایل‌های Python پروژه
# ============================================================

def get_python_files():
    files = []

    for path in PROJECT_PATH.rglob("*.py"):

        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue

        files.append(path)

    return sorted(files)


# ============================================================
# ساخت گزارش
# ============================================================

def make_report():

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "SMART_BOURSE - CHATGPT BRIDGE REPORT",
        "=" * 60,
        f"Generated: {now}",
        f"Project: {PROJECT_PATH}",
        "",
    ]

    # --------------------------------------------------------
    # Branch
    # --------------------------------------------------------

    code, branch, err = run_git(
        "branch",
        "--show-current"
    )

    lines += [
        "CURRENT BRANCH",
        "-" * 60,
        branch if code == 0 else err,
        "",
    ]

    # --------------------------------------------------------
    # Git Status
    # --------------------------------------------------------

    code, status, err = run_git(
        "status",
        "--short"
    )

    lines += [
        "GIT STATUS",
        "-" * 60,
        status or "CLEAN",
        "",
    ]

    # --------------------------------------------------------
    # آخرین Commit
    # --------------------------------------------------------

    code, log, err = run_git(
        "log",
        "-1",
        "--oneline"
    )

    lines += [
        "LAST COMMIT",
        "-" * 60,
        log if code == 0 else err,
        "",
    ]

    # --------------------------------------------------------
    # لیست فایل‌های Python
    # --------------------------------------------------------

    python_files = get_python_files()

    lines += [
        "PYTHON FILES",
        "-" * 60,
        f"Count: {len(python_files)}",
    ]

    for path in python_files:

        relative_path = path.relative_to(PROJECT_PATH)

        lines.append(str(relative_path))

    lines.append("")

    # --------------------------------------------------------
    # فایل‌های Python که تغییر کرده‌اند
    # --------------------------------------------------------

    code, changed, err = run_git(
        "status",
        "--short",
        "--",
        "*.py"
    )

    changed_paths = []

    if code == 0 and changed:

        for row in changed.splitlines():

            if len(row) < 3:
                continue

            relative_path = row[3:].strip()

            if relative_path.endswith(".py"):
                changed_paths.append(relative_path)

    lines += [
        "LOCAL PYTHON CHANGES",
        "-" * 60,
        f"Count: {len(changed_paths)}",
    ]

    for relative_path in changed_paths:
        lines.append(relative_path)

    lines.append("")

    # --------------------------------------------------------
    # محتوای فایل‌های Python تغییرکرده
    # --------------------------------------------------------

    for relative_path in changed_paths:

        path = PROJECT_PATH / relative_path

        if not path.exists():
            continue

        try:

            content = path.read_text(
                encoding="utf-8"
            )

        except Exception as exc:

            content = (
                f"[Could not read file: {exc}]"
            )

        lines += [
            "=" * 60,
            f"FILE: {relative_path}",
            "=" * 60,
            content,
            "",
        ]

    return "\n".join(lines)


# ============================================================
# برنامه اصلی
# ============================================================

def main():

    print("=" * 60)
    print("SMART_BOURSE - ChatGPT Bridge")
    print("=" * 60)

    print(f"Project: {PROJECT_PATH}")
    print()

    # --------------------------------------------------------
    # مرحله 1
    # --------------------------------------------------------

    print("[1/4] دریافت آخرین تغییرات از GitHub ...")

    code, out, err = run_git(
        "pull",
        "--ff-only",
        REMOTE,
        BRANCH
    )

    if code != 0:

        print()
        print("خطا در git pull")
        print(err or out)
        print()
        print(
            "برای جلوگیری از مخلوط شدن "
            "تغییرات، برنامه متوقف شد."
        )

        input("Press Enter to exit...")
        return

    print(out or "Already up to date.")

    # --------------------------------------------------------
    # مرحله 2
    # --------------------------------------------------------

    print()
    print("[2/4] ساخت گزارش وضعیت پروژه ...")

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    report = make_report()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    archive_report = (
        REPORT_DIR /
        f"report_{timestamp}.txt"
    )

    archive_report.write_text(
        report,
        encoding="utf-8"
    )

    LATEST_REPORT.write_text(
        report,
        encoding="utf-8"
    )

    print(
        f"گزارش ساخته شد: "
        f"{archive_report.relative_to(PROJECT_PATH)}"
    )

    # --------------------------------------------------------
    # مرحله 3
    # --------------------------------------------------------

    print()
    print("[3/4] ارسال گزارش به GitHub ...")

    code, out, err = run_git(
        "add",
        str(archive_report),
        str(LATEST_REPORT)
    )

    if code != 0:

        print(err or out)

        input("Press Enter to exit...")
        return

    # --------------------------------------------------------
    # Commit
    # --------------------------------------------------------

    code, out, err = run_git(
        "commit",
        "-m",
        f"Update ChatGPT bridge report {timestamp}"
    )

    if code != 0:

        if "nothing to commit" not in (
            out + err
        ).lower():

            print(err or out)

            input("Press Enter to exit...")
            return

        print(
            "تغییر جدیدی برای گزارش وجود نداشت."
        )

    else:

        print(out)

    # --------------------------------------------------------
    # Push
    # --------------------------------------------------------

    code, out, err = run_git(
        "push",
        REMOTE,
        BRANCH
    )

    if code != 0:

        print("خطا در git push")
        print(err or out)

        input("Press Enter to exit...")
        return

    print(out or "Push successful.")

    # --------------------------------------------------------
    # مرحله 4
    # --------------------------------------------------------

    print()
    print("[4/4] پایان")
    print()

    print(
        "گزارش روی GitHub قرار گرفت."
    )

    print(
        "ChatGPT می‌تواند گزارش را بخواند."
    )

    print()
    print(
        "این برنامه هیچ Token یا Passwordی "
        "را داخل فایل ذخیره نمی‌کند."
    )

    print()

    input("Press Enter to exit...")


# ============================================================
# اجرای برنامه
# ============================================================

if __name__ == "__main__":
    main()


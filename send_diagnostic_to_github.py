from pathlib import Path
from datetime import datetime
import subprocess
import sys
import os


# =========================================================
# Smart Bourse - Diagnostic Reporter
# =========================================================

PROJECT_PATH = Path(__file__).resolve().parent

REPORT_DIR = PROJECT_PATH / "reports" / "diagnostics"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

report_file = REPORT_DIR / f"report_{timestamp}.txt"
latest_file = PROJECT_PATH / "reports" / "latest_report.txt"


def run_command(command, cwd=PROJECT_PATH):
    """Run a command and return stdout + stderr."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        output = result.stdout

        if result.stderr:
            output += "\n\n--- STDERR ---\n"
            output += result.stderr

        output += f"\n\n--- RETURN CODE: {result.returncode} ---\n"

        return output

    except Exception as e:
        return f"COMMAND ERROR: {e}"


def collect_python_files():
    """Collect Python project structure."""
    lines = []

    ignored = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env"
    }

    for path in sorted(PROJECT_PATH.rglob("*")):

        if not path.is_file():
            continue

        relative = path.relative_to(PROJECT_PATH)

        if any(part in ignored for part in relative.parts):
            continue

        if path.suffix.lower() == ".py":

            try:
                text = path.read_text(
                    encoding="utf-8",
                    errors="replace"
                )

                lines.append(
                    f"{relative} | {len(text.splitlines())} lines"
                )

            except Exception as e:
                lines.append(
                    f"{relative} | ERROR: {e}"
                )

    return "\n".join(lines)


def collect_project_files():
    """Collect project file names without dumping their contents."""
    lines = []

    ignored = {
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "env"
    }

    for path in sorted(PROJECT_PATH.rglob("*")):

        if not path.is_file():
            continue

        relative = path.relative_to(PROJECT_PATH)

        if any(part in ignored for part in relative.parts):
            continue

        try:
            size = path.stat().st_size
            lines.append(f"{relative} | {size:,} bytes")

        except Exception:
            lines.append(f"{relative} | size unavailable")

    return "\n".join(lines)


# =========================================================
# Create Report
# =========================================================

print()
print("=" * 70)
print("SMART BOURSE DIAGNOSTIC REPORTER")
print("=" * 70)
print()

report = []

report.append("=" * 70)
report.append("SMART BOURSE - DIAGNOSTIC REPORT")
report.append("=" * 70)
report.append(f"Date: {now}")
report.append(f"Python: {sys.version}")
report.append(f"Project: {PROJECT_PATH}")
report.append("")

# ---------------------------------------------------------
# Git information
# ---------------------------------------------------------

report.append("=" * 70)
report.append("GIT INFORMATION")
report.append("=" * 70)

report.append("\n--- Git Remote ---")
report.append(run_command(["git", "remote", "-v"]))

report.append("\n--- Current Branch ---")
report.append(run_command(["git", "branch", "--show-current"]))

report.append("\n--- Git Status ---")
report.append(run_command(["git", "status", "--short"]))

report.append("\n--- Last Commit ---")
report.append(
    run_command(
        ["git", "log", "-1", "--oneline"]
    )
)

# ---------------------------------------------------------
# Project structure
# ---------------------------------------------------------

report.append("=" * 70)
report.append("PROJECT FILES")
report.append("=" * 70)

report.append(collect_project_files())

# ---------------------------------------------------------
# Python files
# ---------------------------------------------------------

report.append("=" * 70)
report.append("PYTHON FILES")
report.append("=" * 70)

report.append(collect_python_files())

# ---------------------------------------------------------
# Important files
# ---------------------------------------------------------

important_files = [
    "main.py",
    "daily_runner.py",
    "project_config.py",
    "README.md"
]

report.append("=" * 70)
report.append("IMPORTANT FILE STATUS")
report.append("=" * 70)

for filename in important_files:

    path = PROJECT_PATH / filename

    if path.exists():
        report.append(f"{filename}: EXISTS")
    else:
        report.append(f"{filename}: NOT FOUND")

# ---------------------------------------------------------
# Run existing diagnostic program if available
# ---------------------------------------------------------

check_project = PROJECT_PATH / "check_project.py"

if check_project.exists():

    report.append("=" * 70)
    report.append("CHECK_PROJECT.PY OUTPUT")
    report.append("=" * 70)

    print("Running check_project.py ...")
    print()

    output = run_command(
        [sys.executable, str(check_project)]
    )

    report.append(output)

else:

    report.append("=" * 70)
    report.append("CHECK_PROJECT.PY")
    report.append("=" * 70)

    report.append("check_project.py was not found.")

# ---------------------------------------------------------
# Save report
# ---------------------------------------------------------

final_report = "\n".join(report)

report_file.write_text(
    final_report,
    encoding="utf-8"
)

latest_file.write_text(
    final_report,
    encoding="utf-8"
)

print()
print("Report created:")
print(report_file)

print()
print("Latest report:")
print(latest_file)

# =========================================================
# Git upload
# =========================================================

print()
print("=" * 70)
print("UPLOADING REPORT TO GITHUB")
print("=" * 70)
print()

# Only add the diagnostic reports.
run_command(
    [
        "git",
        "add",
        str(report_file.relative_to(PROJECT_PATH)),
        str(latest_file.relative_to(PROJECT_PATH))
    ]
)

commit_message = (
    f"Add diagnostic report {timestamp}"
)

commit_result = run_command(
    [
        "git",
        "commit",
        "-m",
        commit_message
    ]
)

print(commit_result)

# Push
print()
print("Pushing to GitHub ...")
print()

push_result = run_command(
    ["git", "push"]
)

print(push_result)

print()
print("=" * 70)
print("FINISHED")
print("=" * 70)
print()

print("اگر عبارت 'Everything up-to-date' یا push موفق دیدی،")
print("گزارش روی GitHub قرار گرفته است.")

input("\nPress Enter to exit...")

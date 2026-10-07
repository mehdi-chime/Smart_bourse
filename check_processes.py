# check_processes.py
# چک فرآیندهای Python
# اجرا: python check_processes.py

import os
import sys
import subprocess

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def main():
    safe_print("")
    safe_print("=" * 80)
    safe_print("  🔍 چک فرآیندهای Python")
    safe_print("=" * 80)
    safe_print("")

    result = subprocess.run(
        ["wmic", "process", "where", "name='python.exe'", "get", "ProcessId,CommandLine"],
        capture_output=True,
        text=True,
        shell=True,
    )

    lines = result.stdout.split("\n")
    for line in lines:
        line = line.strip()
        if "python.exe" in line or "school_mode" in line or "scanner" in line:
            safe_print(f"  {line[:200]}")

    safe_print("")
    safe_print("=" * 80)


if __name__ == "__main__":
    main()


import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
AUTO_RUNNER = ROOT / "scanner" / "auto_runner.py"
PYTHON = sys.executable


def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def create_task(name, schedule_type, start_time=None):
    python_path = str(PYTHON)
    script_path = str(AUTO_RUNNER)

    if schedule_type == "DAILY":
        cmd_create = (
            'schtasks /Create /TN "' + name + '" '
            '/TR "\\"' + python_path + '\\" \\"' + script_path + '\\"" '
            '/SC DAILY /ST ' + start_time + ' '
            '/RL HIGHEST /F'
        )
    elif schedule_type == "ONLOGON":
        cmd_create = (
            'schtasks /Create /TN "' + name + '" '
            '/TR "\\"' + python_path + '\\" \\"' + script_path + '\\"" '
            '/SC ONLOGON '
            '/RL HIGHEST /F'
        )
    else:
        return False, "unknown schedule type"

    result = run_cmd(cmd_create)
    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout)


def delete_task(name):
    run_cmd('schtasks /Delete /TN "' + name + '" /F')


def main():
    print()
    print("=" * 75)
    print("  Smart_Bourse Scheduler Setup")
    print("=" * 75)
    print()
    print("  Python : " + str(PYTHON))
    print("  Script : " + str(AUTO_RUNNER))
    print()

    daily_name = "Smart_Bourse_AutoRunner_Daily"
    logon_name = "Smart_Bourse_AutoRunner_Logon"

    # حذف تسک‌های قبلی
    print("  Removing old tasks...")
    delete_task("Smart_Bourse_AutoRunner")
    delete_task(daily_name)
    delete_task(logon_name)

    # تسک ۱: روزانه ساعت 8:45
    print()
    print("  [1/2] Creating DAILY task at 8:45...")
    ok, err = create_task(daily_name, "DAILY", "08:45")
    if ok:
        print("        [OK] " + daily_name)
    else:
        print("        [ERROR] " + err)

    # تسک ۲: هر بار Logon
    print()
    print("  [2/2] Creating ONLOGON task...")
    ok, err = create_task(logon_name, "ONLOGON")
    if ok:
        print("        [OK] " + logon_name)
    else:
        print("        [ERROR] " + err)

    print()
    print("=" * 75)
    print("  DONE!")
    print("=" * 75)
    print()
    print("  What happens now:")
    print()
    print("  1. Every day at 8:45 - auto recording starts")
    print("  2. Every time you log in - auto recording starts")
    print("  3. It runs until 12:30 then stops automatically")
    print()
    print("  IMPORTANT: Turn on your computer before 12:30 PM!")
    print()
    print("  Remove tasks:")
    print('     schtasks /Delete /TN "' + daily_name + '" /F')
    print('     schtasks /Delete /TN "' + logon_name + '" /F')
    print()


if __name__ == "__main__":
    main()

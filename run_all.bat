@echo off
cd /d "F:\python\har roz ba python\smart_bours"
start "" /min cmd /c "python scanner\auto_runner.py"
timeout /t 3 /nobreak >nul
start "" /min cmd /c "python scanner\smart_alert.py"

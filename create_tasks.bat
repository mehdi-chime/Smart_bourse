@echo off
chcp 65001 >nul
echo ========================================
echo   ساخت تسک‌های Smart_Bourse
echo ========================================
echo.

echo [1] حذف تسک‌های قبلی...
schtasks /Delete /TN "Smart_Bourse_v9" /F 2>nul
schtasks /Delete /TN "Smart_Bourse_Refresh" /F 2>nul
schtasks /Delete /TN "Smart_Bourse_AutoRunner_Daily" /F 2>nul
schtasks /Delete /TN "Smart_Bourse_AutoRunner_Logon" /F 2>nul
echo    OK
echo.

echo [2] ساخت Smart_Bourse_v9 (8:45)...
schtasks /Create /TN "Smart_Bourse_v9" /TR "\"C:\Users\Mehdi\AppData\Local\Programs\Python\Python313\python.exe\" \"F:\python\har roz ba python\smart_bours\school_mode_v9.py\"" /SC DAILY /ST 08:45 /F
echo.

echo [3] ساخت Smart_Bourse_Refresh (9:00)...
schtasks /Create /TN "Smart_Bourse_Refresh" /TR "\"C:\Users\Mehdi\AppData\Local\Programs\Python\Python313\python.exe\" \"F:\python\har roz ba python\smart_bours\refresh_ins_codes.py\"" /SC DAILY /ST 09:00 /F
echo.

echo ========================================
echo   چک نهایی
echo ========================================
schtasks /Query /FO LIST | findstr Smart_Bourse
echo.
echo تمام!
pause

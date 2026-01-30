@echo off
REM Office Tracker - Setup for Windows

echo ============================================
echo    OFFICE TRACKER - SETUP (Windows)
echo ============================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0

echo Installation directory: %SCRIPT_DIR%
echo.

REM 1. Create attendance.json if not exists
echo [1/4] Setting up database...
if not exist "%SCRIPT_DIR%attendance.json" (
    echo {"dates":[]} > "%SCRIPT_DIR%attendance.json"
    echo    ✓ attendance.json created
) else (
    echo    ✓ Database already exists
)
echo.

REM 2. Check network
echo [2/4] Checking network connection...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"Default Gateway"') do set gateway=%%a
set gateway=%gateway: =%
if defined gateway (
    echo    Gateway detected: %gateway%
    if "%gateway%"=="10.15.16.1" (
        echo    ✓ You are connected to the office network!
    ) else (
        echo    ⚠ Not connected to office network
        echo    💡 When at BI-Mobile, gateway should be 10.15.16.1
    )
) else (
    echo    ⚠ No network detected
)
echo.

REM 3. Test script
echo [3/4] Testing detection script...
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%check_wifi.ps1"
if exist "%SCRIPT_DIR%tracker.log" (
    echo    Last log:
    powershell -Command "Get-Content '%SCRIPT_DIR%tracker.log' -Tail 1"
    echo    ✓ Script works correctly
) else (
    echo    ❌ No log generated
)
echo.

REM 4. Configure auto-start
echo [4/4] Configure automatic execution?
echo.
echo This will create a Windows Task to run every 30 minutes.
set /p response="Install automatic execution? (Y/N): "

if /i "%response%"=="Y" (
    schtasks /create /tn "OfficeTracker" /tr "powershell -ExecutionPolicy Bypass -File \"%SCRIPT_DIR%check_wifi.ps1\"" /sc minute /mo 30 /f
    schtasks /run /tn "OfficeTracker"
    echo    ✓ Task Scheduler configured
    echo    The system will run automatically every 30 minutes
) else (
    echo    ⏭ Skipping automatic installation
    echo    💡 To install later, run this script again
)
echo.

REM 5. Summary
echo ============================================
echo    ✓ SETUP COMPLETED
echo.
echo 📊 To view report:
echo    Double-click: view_report.bat
echo.
echo 📝 Files:
echo    • check_wifi.ps1 - Main script
echo    • attendance.json - Database
echo    • tracker.log - Detection history
echo.
echo 📖 More info: README.md
echo ============================================
echo.
pause

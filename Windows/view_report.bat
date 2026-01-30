@echo off
REM Office Attendance Report - Browser Viewer (Windows)
REM Double-click this file to view report in browser

cd /d "%~dp0"

echo Starting web server...
echo Report will open in your browser. Press Ctrl+C to stop the server.
echo.

REM Start Python HTTP server
start http://localhost:8765/report.html
python -m http.server 8765

pause

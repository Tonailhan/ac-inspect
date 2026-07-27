@echo off
cd /d "%~dp0"
title AC Inspect - Stop Servers
echo.
echo  ========================================
echo   AC Inspect - Stopping Servers...
echo  ========================================
echo.

echo  [1/2] Stopping Backend (Port 5001)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo  [2/2] Stopping Frontend (Port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Also close the CMD windows started by start.bat
taskkill /F /FI "WINDOWTITLE eq AC Inspect Backend*" /T >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq AC Inspect Frontend*" /T >nul 2>&1

echo.
echo  Servers have been stopped successfully!
echo.
pause

@echo off
rem Double-click to set up the L5X Memory Analyzer UI on Windows. The work is done by
rem scripts\setup_windows.ps1.
rem A fresh Windows blocks .ps1 files from running when double-clicked; this runs it for
rem this one invocation only, without changing any system setting.
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup_windows.ps1" %*
set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%

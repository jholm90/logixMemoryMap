@echo off
rem Double-click to remove what Setup.cmd installed: the desktop shortcut, the .venv
rem folder, and Python if Setup.cmd installed it. The work is done by
rem scripts\uninstall_windows.ps1.
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uninstall_windows.ps1" %*
set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%

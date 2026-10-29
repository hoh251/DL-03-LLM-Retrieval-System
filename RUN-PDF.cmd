@echo off
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start.ps1" -Pdf -Chat
set taskExit=%errorlevel%
pause
exit /b %taskExit%

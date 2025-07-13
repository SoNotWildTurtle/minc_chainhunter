@echo off
REM Install ChainHunter scheduled tasks with admin rights
set SCRIPT_DIR=%~dp0
set PS1=%SCRIPT_DIR%install_service.ps1
powershell.exe -NoProfile -Command "Start-Process powershell.exe -Verb runas -ArgumentList '-ExecutionPolicy Bypass -File "%PS1%" %*'"

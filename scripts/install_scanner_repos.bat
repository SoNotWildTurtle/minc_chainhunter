@echo off
REM Install scanner repositories using PowerShell with elevation
set SCRIPT_DIR=%~dp0
set PS1=%SCRIPT_DIR%install_scanner_repos.ps1
powershell.exe -NoProfile -Command "Start-Process powershell.exe -Verb runas -ArgumentList '-ExecutionPolicy Bypass -File "%PS1%" %*'"

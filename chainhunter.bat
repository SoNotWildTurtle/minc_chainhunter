@echo off
REM Entry point for ChainHunter on Windows
set SCRIPT_DIR=%~dp0
set PS1=%SCRIPT_DIR%chainhunter.ps1
powershell.exe -NoProfile -Command "Start-Process powershell.exe -Verb runas -ArgumentList '-ExecutionPolicy Bypass -File "%PS1%" %*'"

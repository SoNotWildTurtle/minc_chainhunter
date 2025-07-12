@echo off
REM Launch the analysis DB IPC server with admin rights
set SCRIPT_DIR=%~dp0
set PS1=%SCRIPT_DIR%setup_ipc_bus.ps1
powershell.exe -NoProfile -Command "Start-Process powershell.exe -Verb runas -ArgumentList '-ExecutionPolicy Bypass -File "%PS1%" %*'"

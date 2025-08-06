@echo off
REM Launch the analysis DB IPC server with admin rights
set SCRIPT_DIR=%~dp0
set PS1=%SCRIPT_DIR%setup_ipc_bus.ps1
powershell.exe -NoProfile -Command "Start-Process -FilePath powershell.exe -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File \"%PS1%\" %*'"

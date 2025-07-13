# Windows entry point for ChainHunter
param(
    [string]$Socket = "tcp://127.0.0.1:8765"
)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $ScriptDir 'venv'
if (-not (Test-Path "$Venv\Scripts\python.exe")) {
    python -m venv $Venv
    & "$Venv\Scripts\pip.exe" install -r (Join-Path $ScriptDir 'requirements.txt')
    & (Join-Path $ScriptDir 'scripts\install_scanner_repos.ps1')
}
# Start the IPC server elevated if not running
$bus = Start-Process powershell -Verb RunAs -PassThru -ArgumentList "-ExecutionPolicy Bypass -File `"$ScriptDir\scripts\setup_ipc_bus.ps1`" -Socket $Socket"
# Launch the CLI
& "$Venv\Scripts\python.exe" (Join-Path $ScriptDir 'cli\main.py') @Args

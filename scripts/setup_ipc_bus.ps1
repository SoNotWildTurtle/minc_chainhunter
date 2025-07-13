# Launch the analysis DB IPC server on Windows
param(
    [string]$Socket = "tcp://127.0.0.1:8765",
    [string]$DbDir = (Join-Path $PSScriptRoot "..\db_data")
)
if (-not (Test-Path $DbDir)) {
    New-Item -ItemType Directory -Force -Path $DbDir | Out-Null
}
python -m analysis_db.db_init --db_dir $DbDir --socket $Socket

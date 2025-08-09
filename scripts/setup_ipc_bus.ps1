# Launch the analysis DB IPC server on Windows
param(
    [string]$Socket = "tcp://127.0.0.1:8765",
    [string]$DbDir = (Join-Path $PSScriptRoot "..\db_data"),
    [string]$Python = "python"
)
if (-not (Test-Path $DbDir)) {
    New-Item -ItemType Directory -Force -Path $DbDir | Out-Null
}
& $Python -m analysis_db.db_init --db_dir $DbDir --socket $Socket

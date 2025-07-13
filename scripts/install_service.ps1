# Install a scheduled task to keep ChainHunter running on Windows
param(
    [string]$RepoDir = (Join-Path $PSScriptRoot ".."),
    [string]$VenvDir = (Join-Path $RepoDir "venv")
)
if (-not (Test-Path $VenvDir)) {
    python -m venv $VenvDir
    & "$VenvDir\Scripts\pip.exe" install numpy scikit-learn
}
$action = New-ScheduledTaskAction -Execute "$VenvDir\Scripts\python.exe" -Argument "$RepoDir\cli\main.py"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName "ChainHunter" -Action $action -Trigger $trigger -Force | Out-Null
# hourly check to ensure the task runs
$checkAction = New-ScheduledTaskAction -Execute "schtasks.exe" -Argument "/Run /TN ChainHunter"
$checkTrigger = New-ScheduledTaskTrigger -Daily -At 00:00 `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 1)
Register-ScheduledTask -TaskName "ChainHunterCheck" -Action $checkAction -Trigger $checkTrigger -Force | Out-Null
Write-Host "[+] Service installed"

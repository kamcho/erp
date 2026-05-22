# Windows PowerShell Backup Automation Script
# Automatically detects the project directory relative to the script location

$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$ProjectDir = Split-Path -Parent -Path $ScriptDir

# Move to project directory
Set-Location -Path $ProjectDir

# Try to find a virtualenv python if it exists (e.g., in .venv or venv)
$PythonPath = "python"
if (Test-Path "$ProjectDir\venv\Scripts\python.exe") {
    $PythonPath = "$ProjectDir\venv\Scripts\python.exe"
} elseif (Test-Path "$ProjectDir\env\Scripts\python.exe") {
    $PythonPath = "$ProjectDir\env\Scripts\python.exe"
}

Write-Host "Starting database backup task at $(Get-Date)..."
Write-Host "Using python: $PythonPath"
Write-Host "Project directory: $ProjectDir"

# Run management command
& $PythonPath manage.py backup_db

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup process completed successfully." -ForegroundColor Green
} else {
    Write-Warning "Backup process failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

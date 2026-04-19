$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Root "backend\.venv"
$Python = "python"

if (!(Get-Command $Python -ErrorAction SilentlyContinue)) {
    throw "Python was not found on PATH. Install Python 3.11+ or use the bundled Codex runtime launcher."
}

if (!(Test-Path $Venv)) {
    & $Python -m venv $Venv
}

$VenvPython = Join-Path $Venv "Scripts\python.exe"
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r (Join-Path $Root "backend\requirements.txt")

Write-Host "Backend environment ready at backend\.venv"
Write-Host "Start it with: .\scripts\start-backend.ps1"

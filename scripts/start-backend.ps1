$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $Root "backend\.venv\Scripts\python.exe"
$VenvUvicorn = Join-Path $Root "backend\.venv\Lib\site-packages\uvicorn"
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$LocalPython = "python"

if ((Test-Path $VenvPython) -and (Test-Path $VenvUvicorn) -and (& $VenvPython -c "import sys; print(sys.executable)" 2>$null)) {
    $Python = $VenvPython
    $env:PYTHONPATH = "$Root\backend"
} elseif (Test-Path $BundledPython) {
    $Python = $BundledPython
    $env:PYTHONPATH = "$Root\backend\.vendor;$Root\backend"
} else {
    $Python = $LocalPython
    $env:PYTHONPATH = "$Root\backend"
}

& $Python -m uvicorn app.main:app --reload --app-dir "$Root\backend"

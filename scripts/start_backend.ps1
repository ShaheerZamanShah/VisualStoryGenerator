$repoRoot = Split-Path $PSScriptRoot -Parent
$pythonExe = Join-Path $repoRoot ".venv311\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
	$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
}

if (-not (Test-Path $pythonExe)) {
	throw "Could not find a Python virtual environment under .venv311 or .venv."
}

Set-Location $repoRoot
& $pythonExe -m uvicorn backend.app:app --host 0.0.0.0 --port 8001 --reload

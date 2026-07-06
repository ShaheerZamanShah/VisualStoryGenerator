$repoRoot = Split-Path $PSScriptRoot -Parent
Set-Location (Join-Path $repoRoot "frontend")
npm run dev

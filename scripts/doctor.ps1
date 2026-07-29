$ErrorActionPreference = "Stop"

$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$ProjectPython = Join-Path $RepositoryRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $ProjectPython)) {
    Write-Error "Ambiente .venv ausente. Consulte docs/operations/environment-setup.md."
    exit 3
}

& $ProjectPython -m inova_av.cli.main doctor @args
exit $LASTEXITCODE

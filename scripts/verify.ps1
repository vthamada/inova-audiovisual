$ErrorActionPreference = "Stop"

$RepositoryRoot = Split-Path -Parent $PSScriptRoot
$ProjectPython = Join-Path $RepositoryRoot ".venv\Scripts\python.exe"
$ProjectNpm = Join-Path $RepositoryRoot "scripts\npm-project.cmd"

& $ProjectPython -m pytest
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $ProjectPython -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $ProjectPython -m mypy
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $ProjectPython -m inova_av.cli.main schema validate project schemas\examples\project.valid.yaml
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (Test-Path -LiteralPath $ProjectNpm) {
    & $ProjectNpm run doctor
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Output "Verificação concluída com sucesso."

@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
set "PROJECT_PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"

if not exist "%PROJECT_PYTHON%" (
  echo ERRO Ambiente .venv ausente. Consulte docs/operations/environment-setup.md. 1>&2
  exit /b 3
)

"%PROJECT_PYTHON%" -m inova_av.cli.main doctor %*
exit /b %ERRORLEVEL%

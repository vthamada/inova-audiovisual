@echo off
setlocal
set "PROJECT_ROOT=%~dp0.."
set "PROJECT_PYTHON=%PROJECT_ROOT%\.venv\Scripts\python.exe"

"%PROJECT_PYTHON%" -m pytest
if errorlevel 1 exit /b %ERRORLEVEL%

"%PROJECT_PYTHON%" -m ruff check .
if errorlevel 1 exit /b %ERRORLEVEL%

"%PROJECT_PYTHON%" -m mypy
if errorlevel 1 exit /b %ERRORLEVEL%

"%PROJECT_PYTHON%" -m pip check
if errorlevel 1 exit /b %ERRORLEVEL%

"%PROJECT_PYTHON%" -m inova_av.cli.main schema validate project schemas\examples\project.valid.yaml
if errorlevel 1 exit /b %ERRORLEVEL%

call "%PROJECT_ROOT%\scripts\npm-project.cmd" run doctor
if errorlevel 1 exit /b %ERRORLEVEL%

echo Verificacao concluida com sucesso.
exit /b 0

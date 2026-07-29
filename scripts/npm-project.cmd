@echo off
chcp 65001 >nul
setlocal
set "PROJECT_ROOT=%~dp0.."
set "NODE_HOME=%PROJECT_ROOT%\.tools\node-v24.18.0-win-x64"

if not exist "%NODE_HOME%\node.exe" (
  echo ERRO Node 24 portatil ausente em "%NODE_HOME%" 1>&2
  exit /b 3
)

set "PATH=%NODE_HOME%;%PATH%"
call "%NODE_HOME%\npm.cmd" %*
exit /b %ERRORLEVEL%

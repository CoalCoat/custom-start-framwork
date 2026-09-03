@echo off
cd /d "%~dp0"

set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo [Error] Python 3 not found. Install from https://www.python.org/downloads/
  echo         and enable "Add python.exe to PATH" during setup.
  pause
  exit /b 1
)

%PY% edit_profiles.py %*
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo.
  echo Editor exited with error %RC%.
  pause
)

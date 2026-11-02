@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PYTHON=py"
) else (
  set "PYTHON=python"
)
%PYTHON% -m venv .venv
if errorlevel 1 (
  echo Python 3 is required. Install Python and ensure it is on PATH.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Package install failed. Check your internet and Python installation.
  pause
  exit /b 1
)
python -m streamlit run app.py
pause

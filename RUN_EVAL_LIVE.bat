@echo off
cd /d "%~dp0"
echo Live evaluation requires GROQ_API_KEY already set in this terminal.
py evaluation\run_eval.py --live
pause

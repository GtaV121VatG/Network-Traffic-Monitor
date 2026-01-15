@echo off

REM Start backend
cd /d %~dp0\backend || exit /b
python -m pip install -r requirements.txt
start cmd /k "python app.py"

REM Wait for backend
timeout /t 5 /nobreak

REM Start frontend (non-interactive)
cd /d %~dp0\frontend || exit /b
set BROWSER=none
set CI=true
start cmd /k "npm start"

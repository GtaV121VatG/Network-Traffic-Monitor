@echo off

REM Start backend
cd /d %~dp0\backend || exit /b
python -m pip install -r requirements.txt
start cmd /k "python app.py"

REM Give backend time to start
timeout /t 5 /nobreak

REM Start frontend
cd /d %~dp0\frontend || exit /b
npm install
start cmd /k "npm start"

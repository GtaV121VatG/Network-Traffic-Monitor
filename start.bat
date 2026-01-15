@echo off

cd /d %~dp0\backend || exit /b
python -m pip install -r requirements.txt
start cmd /k "python app.py"


cd /d %~dp0\frontend || exit /b
set CI=true
start cmd /k "npm start"

@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Hay chay CAI_DAT.bat truoc.
  pause
  exit /b 1
)
if not exist "artifacts\spam_model.joblib" (
  ".venv\Scripts\python.exe" train.py
  if errorlevel 1 goto failed
)
echo Mo http://127.0.0.1:8000/docs de thu API.
".venv\Scripts\python.exe" -m uvicorn spamguard.service:app --host 127.0.0.1 --port 8000
if errorlevel 1 goto failed
exit /b 0
:failed
pause
exit /b 1

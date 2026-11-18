@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Bạn chạy CAI_DAT.bat trước nhé.
  pause
  exit /b 1
)
if not exist "pkl\model_viet.pkl" (
  ".venv\Scripts\python.exe" train.py
  if errorlevel 1 goto failed
)
echo Mở http://127.0.0.1:8000/docs để thử API.
".venv\Scripts\python.exe" -m uvicorn api:app --host 127.0.0.1 --port 8000
if errorlevel 1 goto failed
exit /b 0
:failed
pause
exit /b 1

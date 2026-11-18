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
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Chưa chạy được. Bạn xem thông báo phía trên nhé.
pause
exit /b 1

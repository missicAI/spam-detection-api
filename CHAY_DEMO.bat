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
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Chua chay duoc. Xem thong bao loi phia tren.
pause
exit /b 1

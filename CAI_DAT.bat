@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Da cai dat. Mo CHAY_DEMO.bat de chay giao dien.
pause
exit /b 0
:failed
echo Cai dat chua thanh cong. Kiem tra Python 3.12 va ket noi Internet.
pause
exit /b 1

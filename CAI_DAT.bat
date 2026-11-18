@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Đã cài xong. Bạn mở CHAY_DEMO.bat để chạy nhé.
pause
exit /b 0
:failed
echo Chưa cài xong. Bạn kiểm tra Python 3.12 và kết nối mạng nhé.
pause
exit /b 1

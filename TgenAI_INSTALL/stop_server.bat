@echo off
chcp 65001 >nul
REM ==========================================================
REM TgenAI 서버 중지
REM ==========================================================

echo.
echo ========================================
echo   TgenAI 서버 중지
echo ========================================
echo.

REM Python 프로세스 중지
taskkill /F /FI "COMMANDLINE eq *erp_api_server.py*" >nul 2>&1
taskkill /F /FI "COMMANDLINE eq *tgenai_erp_gateway_monitor.py*" >nul 2>&1

timeout /t 2 /nobreak >nul

echo ✓ TgenAI 서버가 중지되었습니다
echo.

pause

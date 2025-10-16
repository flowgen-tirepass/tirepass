@echo off
chcp 65001 >nul
REM ==========================================================
REM TgenAI 수동 시작 (테스트용)
REM ==========================================================

cd /d %~dp0

echo.
echo ========================================
echo   TgenAI 서버 수동 시작
echo ========================================
echo.

REM 가상환경 활성화
call venv\Scripts\activate.bat

echo FastAPI 서버 시작 중...
echo 중지하려면 Ctrl+C를 누르세요
echo.
echo 서비스 확인: http://localhost:8002/health
echo.

REM FastAPI 서버 실행
python erp_api_server.py

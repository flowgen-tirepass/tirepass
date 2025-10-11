@echo off
REM ========================================
REM TgenAI ERP API 서버 재시작 스크립트
REM ========================================
echo.
echo ========================================
echo TgenAI ERP API 서버 재시작
echo ========================================
echo.

REM 1. 기존 프로세스 종료
echo [1/3] 기존 서버 프로세스 종료 중...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 >nul
echo 기존 프로세스 종료 완료.
echo.

REM 2. TgenAI 디렉토리로 이동
echo [2/3] TgenAI 디렉토리로 이동...
if not exist "C:\TgenAI\erp_api" (
    echo 오류: C:\TgenAI\erp_api 디렉토리를 찾을 수 없습니다.
    echo 이 스크립트를 C:\TgenAI\ 폴더에 복사한 후 실행하세요.
    pause
    exit /b 1
)
cd /d C:\TgenAI\erp_api
echo.

REM 3. 서버 시작
echo [3/3] FastAPI 서버 시작 중...
echo 서버 로그를 확인하세요...
echo.
C:\TgenAI\venv\Scripts\python.exe erp_api_server.py

REM 서버가 종료되면
echo.
echo ========================================
echo 서버가 종료되었습니다.
echo ========================================
pause

@echo off
chcp 65001 >nul
REM ==========================================================
REM TgenAI 상태 확인
REM ==========================================================

echo.
echo ========================================
echo   TgenAI 서버 상태 확인
echo ========================================
echo.

REM 프로세스 확인
echo [1] 프로세스 상태:
tasklist /FI "IMAGENAME eq python.exe" | findstr python.exe >nul
if %errorlevel% equ 0 (
    echo ✓ Python 프로세스 실행 중
) else (
    echo ✗ Python 프로세스 없음
)
echo.

REM 포트 확인
echo [2] 포트 상태:
netstat -ano | findstr :8002 >nul
if %errorlevel% equ 0 (
    echo ✓ 8002 포트 사용 중
) else (
    echo ✗ 8002 포트 사용 안 됨
)
echo.

REM 헬스체크
echo [3] 헬스체크:
curl -s http://localhost:8002/health
echo.
echo.

REM 로그 확인
echo [4] 최근 로그 (마지막 10줄):
if exist tgenai_gateway_monitor.log (
    powershell -Command "Get-Content tgenai_gateway_monitor.log -Tail 10"
) else (
    echo 로그 파일 없음
)
echo.

echo ========================================
echo.

pause

@echo off
REM ==========================================================
REM TgenAI ERP 게이트웨이 모니터 시작 (TgenAI PC 전용)
REM ==========================================================

echo ========================================
echo TgenAI ERP 게이트웨이 모니터 시작
echo ========================================
echo.

REM Python 경로 (시스템 PATH 사용)
set PYTHON_PATH=python

REM 스크립트 경로
set SCRIPT_PATH=C:\TgenAI\tgenai_erp_gateway_monitor.py

REM 작업 디렉토리 이동
cd /d C:\TgenAI

echo Python: %PYTHON_PATH%
echo Script: %SCRIPT_PATH%
echo.

REM psutil 설치 확인
echo psutil 패키지 확인 중...
%PYTHON_PATH% -m pip install psutil requests >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 패키지 설치 실패 - 수동 설치 필요
    echo 명령어: python -m pip install psutil requests
    pause
)

echo 패키지 확인 완료
echo.

REM 모니터 실행
echo 게이트웨이 모니터 시작...
echo 중지하려면 Ctrl+C를 누르세요
echo ========================================
echo.

%PYTHON_PATH% %SCRIPT_PATH%

REM 오류 발생 시 대기
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo 오류가 발생했습니다!
    echo 로그 파일: C:\TgenAI\tgenai_gateway_monitor.log
    echo ========================================
    pause
)

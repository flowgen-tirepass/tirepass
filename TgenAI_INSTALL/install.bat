@echo off
chcp 65001 >nul
REM ==========================================================
REM TgenAI ERP Gateway 자동 설치 스크립트
REM 작성일: 2025-10-16
REM ==========================================================

echo.
echo ========================================
echo   TgenAI ERP Gateway 설치
echo ========================================
echo.

REM 현재 디렉토리 확인
cd /d %~dp0
echo 작업 디렉토리: %CD%
echo.

REM ==========================================================
REM 1. Python 확인
REM ==========================================================

echo [1/7] Python 설치 확인 중...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python이 설치되지 않았습니다!
    echo.
    echo Python 3.11 이상을 설치하세요:
    echo https://www.python.org/downloads/
    echo.
    echo 설치 시 "Add Python to PATH" 체크 필수!
    pause
    exit /b 1
)

python --version
echo ✓ Python 설치 확인 완료
echo.

REM ==========================================================
REM 2. 가상환경 생성
REM ==========================================================

echo [2/7] Python 가상환경 생성 중...
if exist venv (
    echo 기존 가상환경 발견 - 삭제 후 재생성
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] 가상환경 생성 실패!
    pause
    exit /b 1
)

echo ✓ 가상환경 생성 완료
echo.

REM ==========================================================
REM 3. 가상환경 활성화 및 패키지 설치
REM ==========================================================

echo [3/7] 필요한 패키지 설치 중...
call venv\Scripts\activate.bat

python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] 패키지 설치 실패!
    pause
    exit /b 1
)

echo ✓ 패키지 설치 완료
echo.

REM ==========================================================
REM 4. ERP DB 연결 테스트
REM ==========================================================

echo [4/7] ERP 데이터베이스 연결 테스트 중...
python -c "import pymysql; conn = pymysql.connect(host='itire2.iptime.org', port=3306, user='root', password='tirepass', database='itire_db'); print('✓ ERP DB 연결 성공!'); conn.close()"

if %errorlevel% neq 0 (
    echo [ERROR] ERP DB 연결 실패!
    echo.
    echo 다음을 확인하세요:
    echo 1. 인터넷 연결 상태
    echo 2. 광주 ERP 서버 상태 (itire2.iptime.org)
    echo 3. 방화벽 설정 (3306 포트)
    pause
    exit /b 1
)

echo.

REM ==========================================================
REM 5. FastAPI 서버 테스트
REM ==========================================================

echo [5/7] FastAPI 서버 테스트 중...
echo 서버 시작 중... (10초 대기)

start /min cmd /c "venv\Scripts\python.exe erp_api_server.py > server_test.log 2>&1"
timeout /t 10 /nobreak >nul

REM 헬스체크
curl -s http://localhost:8002/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] FastAPI 서버 시작 실패!
    echo 로그 확인: server_test.log
    pause
    exit /b 1
)

echo ✓ FastAPI 서버 테스트 성공!
echo.

REM 테스트 서버 중지
taskkill /F /FI "WINDOWTITLE eq erp_api_server.py*" >nul 2>&1
timeout /t 2 /nobreak >nul

REM ==========================================================
REM 6. 게이트웨이 모니터 테스트
REM ==========================================================

echo [6/7] 게이트웨이 모니터 설치 확인 중...
if not exist tgenai_erp_gateway_monitor.py (
    echo [ERROR] tgenai_erp_gateway_monitor.py 파일 없음!
    pause
    exit /b 1
)

echo ✓ 게이트웨이 모니터 설치 확인 완료
echo.

REM ==========================================================
REM 7. 설치 완료
REM ==========================================================

echo [7/7] 설치 완료 확인...
echo.
echo ========================================
echo   ✓ TgenAI ERP Gateway 설치 완료!
echo ========================================
echo.
echo 다음 단계:
echo.
echo 1. 수동 테스트:
echo    start_server.bat 실행
echo    브라우저에서 http://localhost:8002/health 접속
echo.
echo 2. 자동 시작 등록:
echo    register_autostart.bat 실행
echo    (부팅 시 자동 시작 설정)
echo.
echo ========================================
echo.

pause

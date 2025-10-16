@echo off
REM ==========================================================
REM TgenAI 전체 감시 시스템 설치 (TgenAI PC 전용)
REM
REM 관리자 권한으로 실행하세요!
REM ==========================================================

REM 관리자 권한 확인
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ========================================
    echo 관리자 권한이 필요합니다!
    echo ========================================
    echo.
    echo 이 파일을 마우스 우클릭 후
    echo "관리자 권한으로 실행"을 선택하세요.
    echo.
    pause
    exit /b 1
)

echo ========================================
echo TgenAI 전체 감시 시스템 설치
echo ========================================
echo.
echo 설치 경로: C:\TgenAI
echo.
echo 다음 항목들을 Windows 작업 스케줄러에 등록합니다:
echo   1. ERP 게이트웨이 모니터 (24/7)
echo   2. TeamViewer 감시견
echo   3. 네트워크 감시견
echo.
pause

REM 설치 경로
set BASE_DIR=C:\TgenAI\

REM ==========================================================
REM 1. ERP 게이트웨이 모니터
REM ==========================================================

echo.
echo ========================================
echo [1/3] ERP 게이트웨이 모니터 등록
echo ========================================

set TASK_NAME_1=TgenAI_ERP_Gateway_Monitor
set SCRIPT_PATH_1=%BASE_DIR%start_tgenai_gateway_monitor.bat

REM 기존 작업 삭제
schtasks /delete /tn "%TASK_NAME_1%" /f >nul 2>&1

REM 새 작업 생성
schtasks /create ^
    /tn "%TASK_NAME_1%" ^
    /tr "%SCRIPT_PATH_1%" ^
    /sc onstart ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /f

if %errorlevel% equ 0 (
    echo [SUCCESS] ERP 게이트웨이 모니터 등록 완료
) else (
    echo [ERROR] ERP 게이트웨이 모니터 등록 실패
)

REM ==========================================================
REM 2. TeamViewer 감시견
REM ==========================================================

echo.
echo ========================================
echo [2/3] TeamViewer 감시견 등록
echo ========================================

set TASK_NAME_2=TgenAI_TeamViewer_Watchdog
set SCRIPT_PATH_2=%BASE_DIR%teamviewer_watchdog.bat

REM 기존 작업 삭제
schtasks /delete /tn "%TASK_NAME_2%" /f >nul 2>&1

REM 새 작업 생성
schtasks /create ^
    /tn "%TASK_NAME_2%" ^
    /tr "%SCRIPT_PATH_2%" ^
    /sc onstart ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /f

if %errorlevel% equ 0 (
    echo [SUCCESS] TeamViewer 감시견 등록 완료
) else (
    echo [ERROR] TeamViewer 감시견 등록 실패
)

REM ==========================================================
REM 3. 네트워크 감시견
REM ==========================================================

echo.
echo ========================================
echo [3/3] 네트워크 감시견 등록
echo ========================================

set TASK_NAME_3=TgenAI_Network_Watchdog
set SCRIPT_PATH_3=%BASE_DIR%network_watchdog.bat

REM 기존 작업 삭제
schtasks /delete /tn "%TASK_NAME_3%" /f >nul 2>&1

REM 새 작업 생성
schtasks /create ^
    /tn "%TASK_NAME_3%" ^
    /tr "%SCRIPT_PATH_3%" ^
    /sc onstart ^
    /ru SYSTEM ^
    /rl HIGHEST ^
    /f

if %errorlevel% equ 0 (
    echo [SUCCESS] 네트워크 감시견 등록 완료
) else (
    echo [ERROR] 네트워크 감시견 등록 실패
)

REM ==========================================================
REM 최종 요약
REM ==========================================================

echo.
echo ========================================
echo 설치 완료!
echo ========================================
echo.
echo 등록된 작업:
echo   1. %TASK_NAME_1%
echo   2. %TASK_NAME_2%
echo   3. %TASK_NAME_3%
echo.
echo 다음 단계:
echo   1. 시스템 재부팅하여 자동 시작 확인
echo   2. 작업 스케줄러 확인: Win + R → taskschd.msc
echo   3. 로그 파일 확인: C:\TgenAI\*.log
echo.
echo ========================================
echo.

REM 작업 스케줄러 열기 (선택)
choice /c YN /m "작업 스케줄러를 열어서 확인하시겠습니까?"
if %errorlevel% equ 1 (
    start taskschd.msc
)

echo.
pause

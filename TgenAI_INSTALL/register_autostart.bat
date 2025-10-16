@echo off
chcp 65001 >nul
REM ==========================================================
REM TgenAI ERP Gateway 자동 시작 등록 스크립트
REM Windows 작업 스케줄러 사용
REM 작성일: 2025-10-16
REM ==========================================================

echo.
echo ========================================
echo   TgenAI 자동 시작 등록
echo ========================================
echo.

REM 관리자 권한 확인
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 관리자 권한이 필요합니다!
    echo.
    echo 이 파일을 마우스 우클릭 → "관리자 권한으로 실행" 선택
    echo.
    pause
    exit /b 1
)

echo ✓ 관리자 권한 확인 완료
echo.

REM 현재 디렉토리
cd /d %~dp0
set TGENAI_DIR=%CD%

echo 설치 디렉토리: %TGENAI_DIR%
echo.

REM ==========================================================
REM 기존 작업 삭제 (있는 경우)
REM ==========================================================

echo 기존 작업 삭제 중...
schtasks /Delete /TN "TgenAI_ERP_Gateway" /F >nul 2>&1
echo.

REM ==========================================================
REM Windows 작업 스케줄러 등록
REM ==========================================================

echo 작업 스케줄러에 등록 중...
echo.

REM XML 파일 생성
echo ^<?xml version="1.0" encoding="UTF-16"?^> > "%TEMP%\tgenai_task.xml"
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> >> "%TEMP%\tgenai_task.xml"
echo   ^<RegistrationInfo^> >> "%TEMP%\tgenai_task.xml"
echo     ^<Description^>TgenAI ERP Gateway - 24/7 모니터링 및 자동 재시작^</Description^> >> "%TEMP%\tgenai_task.xml"
echo   ^</RegistrationInfo^> >> "%TEMP%\tgenai_task.xml"
echo   ^<Triggers^> >> "%TEMP%\tgenai_task.xml"
echo     ^<BootTrigger^> >> "%TEMP%\tgenai_task.xml"
echo       ^<Enabled^>true^</Enabled^> >> "%TEMP%\tgenai_task.xml"
echo       ^<Delay^>PT1M^</Delay^> >> "%TEMP%\tgenai_task.xml"
echo     ^</BootTrigger^> >> "%TEMP%\tgenai_task.xml"
echo   ^</Triggers^> >> "%TEMP%\tgenai_task.xml"
echo   ^<Principals^> >> "%TEMP%\tgenai_task.xml"
echo     ^<Principal^> >> "%TEMP%\tgenai_task.xml"
echo       ^<LogonType^>S4U^</LogonType^> >> "%TEMP%\tgenai_task.xml"
echo       ^<RunLevel^>HighestAvailable^</RunLevel^> >> "%TEMP%\tgenai_task.xml"
echo     ^</Principal^> >> "%TEMP%\tgenai_task.xml"
echo   ^</Principals^> >> "%TEMP%\tgenai_task.xml"
echo   ^<Settings^> >> "%TEMP%\tgenai_task.xml"
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^> >> "%TEMP%\tgenai_task.xml"
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^> >> "%TEMP%\tgenai_task.xml"
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^> >> "%TEMP%\tgenai_task.xml"
echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^> >> "%TEMP%\tgenai_task.xml"
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^> >> "%TEMP%\tgenai_task.xml"
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^> >> "%TEMP%\tgenai_task.xml"
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^> >> "%TEMP%\tgenai_task.xml"
echo     ^<Enabled^>true^</Enabled^> >> "%TEMP%\tgenai_task.xml"
echo     ^<Hidden^>false^</Hidden^> >> "%TEMP%\tgenai_task.xml"
echo     ^<ExecutionTimeLimit^>PT0S^</ExecutionTimeLimit^> >> "%TEMP%\tgenai_task.xml"
echo   ^</Settings^> >> "%TEMP%\tgenai_task.xml"
echo   ^<Actions^> >> "%TEMP%\tgenai_task.xml"
echo     ^<Exec^> >> "%TEMP%\tgenai_task.xml"
echo       ^<Command^>%TGENAI_DIR%\venv\Scripts\python.exe^</Command^> >> "%TEMP%\tgenai_task.xml"
echo       ^<Arguments^>%TGENAI_DIR%\tgenai_erp_gateway_monitor.py^</Arguments^> >> "%TEMP%\tgenai_task.xml"
echo       ^<WorkingDirectory^>%TGENAI_DIR%^</WorkingDirectory^> >> "%TEMP%\tgenai_task.xml"
echo     ^</Exec^> >> "%TEMP%\tgenai_task.xml"
echo   ^</Actions^> >> "%TEMP%\tgenai_task.xml"
echo ^</Task^> >> "%TEMP%\tgenai_task.xml"

REM 작업 등록
schtasks /Create /TN "TgenAI_ERP_Gateway" /XML "%TEMP%\tgenai_task.xml" /F

if %errorlevel% neq 0 (
    echo [ERROR] 작업 스케줄러 등록 실패!
    del "%TEMP%\tgenai_task.xml"
    pause
    exit /b 1
)

del "%TEMP%\tgenai_task.xml"

echo ✓ 작업 스케줄러 등록 완료
echo.

REM ==========================================================
REM 즉시 시작
REM ==========================================================

echo 게이트웨이 모니터 시작 중...
schtasks /Run /TN "TgenAI_ERP_Gateway"

timeout /t 3 /nobreak >nul

echo ✓ 게이트웨이 모니터 시작됨
echo.

REM ==========================================================
REM 완료
REM ==========================================================

echo ========================================
echo   ✓ 자동 시작 등록 완료!
echo ========================================
echo.
echo 설정 내용:
echo - 작업 이름: TgenAI_ERP_Gateway
echo - 시작 시기: PC 부팅 후 1분
echo - 실행 파일: tgenai_erp_gateway_monitor.py
echo - 작동 방식: 24/7 자동 모니터링 및 재시작
echo.
echo 확인 방법:
echo 1. 작업 스케줄러 열기 (taskschd.msc)
echo 2. "TgenAI_ERP_Gateway" 작업 확인
echo 3. 또는 PC 재부팅 후 자동 시작 확인
echo.
echo 로그 확인:
echo %TGENAI_DIR%\tgenai_gateway_monitor.log
echo.
echo 서비스 상태 확인:
echo http://localhost:8002/health
echo.
echo ========================================
echo.

pause

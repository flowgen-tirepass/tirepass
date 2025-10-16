@echo off
chcp 65001 >nul
REM ==========================================================
REM TeamViewer 감시견 (TgenAI PC 전용)
REM ==========================================================

setlocal enabledelayedexpansion

REM 설정
set TEAMVIEWER_EXE=TeamViewer.exe
set CHECK_INTERVAL=60
set LOG_FILE=C:\TgenAI\teamviewer_watchdog.log
set MAX_LOG_SIZE=10485760

REM TeamViewer 설치 경로 찾기
set "TEAMVIEWER_PATH="

if exist "C:\Program Files\TeamViewer\TeamViewer.exe" (
    set "TEAMVIEWER_PATH=C:\Program Files\TeamViewer\TeamViewer.exe"
) else if exist "C:\Program Files (x86)\TeamViewer\TeamViewer.exe" (
    set "TEAMVIEWER_PATH=C:\Program Files (x86)\TeamViewer\TeamViewer.exe"
) else (
    echo [ERROR] TeamViewer 설치 경로를 찾을 수 없습니다!
    exit /b 1
)

REM Silent mode - no console output (runs in background)

REM 로그 파일 크기 확인
if exist "%LOG_FILE%" (
    for %%A in ("%LOG_FILE%") do set LOG_SIZE=%%~zA
    if !LOG_SIZE! gtr %MAX_LOG_SIZE% (
        copy /y "%LOG_FILE%" "%LOG_FILE%.bak" >nul 2>&1
        echo. > "%LOG_FILE%"
    )
)

REM 시작 로그
call :LogMessage "TeamViewer 감시견 시작"

REM 무한 루프
set ITERATION=0

:LOOP
    set /a ITERATION+=1

    REM TeamViewer 프로세스 확인
    tasklist /FI "IMAGENAME eq %TEAMVIEWER_EXE%" 2>NUL | find /I /N "%TEAMVIEWER_EXE%">NUL

    if %ERRORLEVEL% equ 0 (
        REM TeamViewer 실행 중
        set /a "MOD=ITERATION %% 30"
        if !MOD! equ 0 (
            call :LogMessage "TeamViewer 실행 중 (정상)"
        )
    ) else (
        REM TeamViewer 종료됨 - 재시작
        call :LogMessage "TeamViewer 종료 감지 - 재시작 시도"

        start "" "%TEAMVIEWER_PATH%"
        timeout /t 10 /nobreak >nul

        tasklist /FI "IMAGENAME eq %TEAMVIEWER_EXE%" 2>NUL | find /I /N "%TEAMVIEWER_EXE%">NUL
        if %ERRORLEVEL% equ 0 (
            call :LogMessage "TeamViewer 재시작 성공"
        ) else (
            call :LogMessage "TeamViewer 재시작 실패"
        )
    )

    timeout /t %CHECK_INTERVAL% /nobreak >nul
goto LOOP

:LogMessage
    set MSG=%~1
    set TIMESTAMP=%DATE% %TIME%
    echo [%TIMESTAMP%] %MSG% >> "%LOG_FILE%"
    exit /b 0

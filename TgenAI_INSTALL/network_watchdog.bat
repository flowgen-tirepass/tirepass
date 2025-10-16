@echo off
chcp 65001 >nul
REM ==========================================================
REM 네트워크 감시견 (TgenAI PC 전용)
REM ==========================================================

setlocal enabledelayedexpansion

REM 설정
set CHECK_INTERVAL=60
set LOG_FILE=C:\TgenAI\network_watchdog.log
set MAX_LOG_SIZE=10485760
set PING_TARGET=8.8.8.8
set PING_COUNT=4

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
call :LogMessage "네트워크 감시견 시작"

REM 무한 루프
set ITERATION=0
set CONSECUTIVE_FAILURES=0

:LOOP
    set /a ITERATION+=1

    REM 인터넷 연결 확인
    ping -n %PING_COUNT% %PING_TARGET% >nul 2>&1

    if %ERRORLEVEL% equ 0 (
        REM 연결 정상
        set CONSECUTIVE_FAILURES=0
        set /a "MOD=ITERATION %% 30"
        if !MOD! equ 0 (
            call :LogMessage "네트워크 연결 정상"
        )
    ) else (
        REM 연결 끊김
        set /a CONSECUTIVE_FAILURES+=1
        call :LogMessage "네트워크 연결 실패 (!CONSECUTIVE_FAILURES!회)"

        REM 3회 연속 실패 시 네트워크 어댑터 재시작
        if !CONSECUTIVE_FAILURES! geq 3 (
            call :LogMessage "3회 연속 실패 - 네트워크 어댑터 재시작 시도"

            netsh interface set interface "이더넷" disabled >nul 2>&1
            timeout /t 5 /nobreak >nul
            netsh interface set interface "이더넷" enabled >nul 2>&1

            call :LogMessage "네트워크 어댑터 재시작 완료"
            timeout /t 30 /nobreak >nul

            ping -n %PING_COUNT% %PING_TARGET% >nul 2>&1
            if %ERRORLEVEL% equ 0 (
                set CONSECUTIVE_FAILURES=0
                call :LogMessage "네트워크 복구 성공"
            ) else (
                call :LogMessage "네트워크 복구 실패"
            )
        )
    )

    timeout /t %CHECK_INTERVAL% /nobreak >nul
goto LOOP

:LogMessage
    set MSG=%~1
    set TIMESTAMP=%DATE% %TIME%
    echo [%TIMESTAMP%] %MSG% >> "%LOG_FILE%"
    exit /b 0

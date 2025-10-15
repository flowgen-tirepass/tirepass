# TgenAI ERP 게이트웨이 24/7 자동 복구 시스템 설치 가이드

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [설치 준비](#설치-준비)
3. [Windows 작업 스케줄러 등록](#windows-작업-스케줄러-등록)
4. [수동 실행 및 테스트](#수동-실행-및-테스트)
5. [로그 확인](#로그-확인)
6. [문제 해결](#문제-해결)

---

## 시스템 개요

### 역할
TgenAI (화성 로컬 PC)에서 24시간 실행되며 다음 작업을 자동으로 수행합니다:

1. **ERP API 서버 모니터링** (매 1분)
   - `erp_api_server.py` 프로세스 상태 확인
   - `/health` 엔드포인트 헬스체크
   - Firebird DB 연결 상태 확인

2. **자동 복구**
   - ERP API 서버 다운 시 자동 재시작
   - 3회 연속 헬스체크 실패 시 재시작
   - 재시작 쿨다운 (5분) 적용

3. **PythonAnywhere 연결 모니터링** (매 5분)
   - API 연결 상태 확인
   - 연결 실패 시 로그 기록

4. **완전 자동화**
   - 시스템 부팅 시 자동 시작
   - 장애 발생 시 자동 복구
   - 모든 이벤트 로그 기록

### 아키텍처
```
┌─────────────────────────────────────────┐
│           TgenAI (화성 로컬 PC)          │
├─────────────────────────────────────────┤
│                                          │
│  [게이트웨이 모니터] (24/7 실행)        │
│   tgenai_erp_gateway_monitor.py         │
│   - ERP API 서버 감시                   │
│   - 자동 재시작                          │
│   - PythonAnywhere 연결 체크            │
│          │                               │
│          ▼                               │
│  [ERP API 서버]                         │
│   erp_api_server.py                     │
│   - FastAPI (포트 8000)                 │
│   - Firebird DB 연결                    │
│          │                               │
│          ▼                               │
│  [ERP Firebird DB]                      │
│   C:\...\ITIRE.GDB                      │
│                                          │
└─────────────────────────────────────────┘
           │
           │ HTTP (인터넷)
           ▼
┌─────────────────────────────────────────┐
│       PythonAnywhere (클라우드)         │
│    tirepass.pythonanywhere.com          │
└─────────────────────────────────────────┘
```

---

## 설치 준비

### 1. Python 패키지 설치

TgenAI 컴퓨터에서 다음 명령 실행:

```bash
cd C:\Users\jmyang\Dropbox\1.0_tirepass

# 가상환경 활성화 (이미 활성화된 경우 생략)
venv\Scripts\activate

# 필요한 패키지 설치
pip install psutil requests
```

### 2. 파일 확인

다음 파일들이 있는지 확인:
- ✅ `tgenai_erp_gateway_monitor.py` (게이트웨이 모니터)
- ✅ `start_tgenai_gateway_monitor.bat` (시작 배치 파일)
- ✅ `erp_api_server.py` (ERP API 서버)

---

## Windows 작업 스케줄러 등록

### 방법 1: 배치 파일을 통한 자동 등록 (권장)

1. **작업 스케줄러 등록 스크립트 작성**

   새 파일 생성: `C:\Users\jmyang\Dropbox\1.0_tirepass\install_scheduler_task.bat`

   ```batch
   @echo off
   REM TgenAI 게이트웨이 모니터를 Windows 작업 스케줄러에 등록

   set TASK_NAME=TgenAI_ERP_Gateway_Monitor
   set SCRIPT_PATH=C:\Users\jmyang\Dropbox\1.0_tirepass\start_tgenai_gateway_monitor.bat

   echo ========================================
   echo 작업 스케줄러 등록 중...
   echo ========================================

   REM 기존 작업 삭제 (있는 경우)
   schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

   REM 새 작업 생성
   schtasks /create ^
       /tn "%TASK_NAME%" ^
       /tr "%SCRIPT_PATH%" ^
       /sc onstart ^
       /ru SYSTEM ^
       /rl HIGHEST ^
       /f

   if %errorlevel% equ 0 (
       echo.
       echo ========================================
       echo ✅ 작업 스케줄러 등록 완료!
       echo ========================================
       echo.
       echo 작업 이름: %TASK_NAME%
       echo 실행 파일: %SCRIPT_PATH%
       echo 트리거: 시스템 시작 시
       echo 권한: SYSTEM (최고 권한)
       echo.
       echo 시스템을 재부팅하면 자동으로 시작됩니다.
       echo.
   ) else (
       echo.
       echo ========================================
       echo ❌ 작업 스케줄러 등록 실패!
       echo ========================================
       echo.
       echo 관리자 권한으로 다시 실행해주세요.
       echo.
   )

   pause
   ```

2. **관리자 권한으로 실행**

   - `install_scheduler_task.bat` 파일을 **마우스 우클릭**
   - **"관리자 권한으로 실행"** 선택
   - 등록 완료 메시지 확인

### 방법 2: GUI를 통한 수동 등록

1. **작업 스케줄러 열기**
   - Windows 검색: "작업 스케줄러" 입력
   - 또는 `Win + R` → `taskschd.msc` 입력

2. **새 작업 만들기**
   - 오른쪽 패널: **"기본 작업 만들기"** 클릭

3. **기본 작업 만들기 마법사**

   **1단계: 이름 및 설명**
   - 이름: `TgenAI ERP Gateway Monitor`
   - 설명: `ERP API 서버 24/7 모니터링 및 자동 복구`
   - **다음** 클릭

   **2단계: 트리거**
   - **"컴퓨터 시작 시"** 선택
   - **다음** 클릭

   **3단계: 작업**
   - **"프로그램 시작"** 선택
   - **다음** 클릭

   **4단계: 프로그램 시작**
   - 프로그램/스크립트:
     ```
     C:\Users\jmyang\Dropbox\1.0_tirepass\start_tgenai_gateway_monitor.bat
     ```
   - 시작 위치 (옵션):
     ```
     C:\Users\jmyang\Dropbox\1.0_tirepass
     ```
   - **다음** 클릭

   **5단계: 마침**
   - **"마침을 클릭할 때 이 작업의 속성 대화 상자 열기"** 체크
   - **마침** 클릭

4. **고급 설정 (속성 대화 상자)**

   **일반 탭:**
   - "가장 높은 수준의 권한으로 실행" 체크
   - "사용자의 로그온 여부에 관계없이 실행" 선택

   **트리거 탭:**
   - 트리거 더블클릭
   - "작업 시작: 시작할 때" 확인
   - 고급 설정:
     - "작업 반복 간격: 사용 안 함" (무한 실행)
   - **확인** 클릭

   **조건 탭:**
   - "다음 경우에만 작업 시작" 섹션:
     - "컴퓨터의 전원이 AC 전원일 때만 작업 시작" **체크 해제**
   - **확인** 클릭

5. **작업 확인**
   - 작업 스케줄러 라이브러리에서 작업 확인
   - 상태: "준비됨" 확인

---

## 수동 실행 및 테스트

작업 스케줄러 등록 전에 먼저 수동으로 테스트:

### 1. 배치 파일로 실행

```batch
# 배치 파일 더블클릭
start_tgenai_gateway_monitor.bat
```

또는 명령 프롬프트에서:

```bash
cd C:\Users\jmyang\Dropbox\1.0_tirepass
start_tgenai_gateway_monitor.bat
```

### 2. Python으로 직접 실행

```bash
cd C:\Users\jmyang\Dropbox\1.0_tirepass
venv\Scripts\python.exe tgenai_erp_gateway_monitor.py
```

### 3. 정상 작동 확인

콘솔 출력 예시:
```
================================================================================
🚀 TgenAI ERP 게이트웨이 모니터링 시작
================================================================================
📂 작업 디렉토리: C:\Users\jmyang\Dropbox\1.0_tirepass
🔍 체크 주기: 60초
🔄 재시작 쿨다운: 300초
📊 로그 파일: C:\Users\jmyang\Dropbox\1.0_tirepass\tgenai_gateway_monitor.log
================================================================================
✅ ERP API 서버 실행 중 (PID: 12345)
✅ ERP API 정상 | PID: 12345 | 상품: 6,530개 | DB: connected
✅ PythonAnywhere API 연결 정상
```

---

## 로그 확인

### 로그 파일 위치
```
C:\Users\jmyang\Dropbox\1.0_tirepass\tgenai_gateway_monitor.log
```

### 로그 내용 예시

```log
2025-10-15 14:30:00 - INFO - 🚀 TgenAI ERP 게이트웨이 모니터링 시작
2025-10-15 14:30:00 - INFO - ✅ ERP API 서버 실행 중 (PID: 12345)
2025-10-15 14:31:00 - INFO - ✅ ERP API 정상 | PID: 12345 | 상품: 6,530개 | DB: connected
2025-10-15 14:35:00 - INFO - ✅ PythonAnywhere API 연결 정상
2025-10-15 14:45:00 - ERROR - ❌ ERP API 서버 헬스체크 실패 (1회) | 오류: Connection timeout
2025-10-15 14:46:00 - ERROR - ❌ ERP API 서버 헬스체크 실패 (2회) | 오류: Connection timeout
2025-10-15 14:47:00 - ERROR - ❌ ERP API 서버 헬스체크 실패 (3회) | 오류: Connection timeout
2025-10-15 14:47:00 - ERROR - 🔄 3회 연속 실패 - 재시작 시도
2025-10-15 14:47:00 - INFO - 🛑 ERP API 서버 중지 중... (PID: 12345)
2025-10-15 14:47:03 - INFO - ✅ ERP API 서버 정상 종료
2025-10-15 14:47:03 - INFO - 🚀 ERP API 서버 시작 시도...
2025-10-15 14:47:13 - INFO - ✅ ERP API 서버 시작 성공 (PID: 23456, 상품: 6,530개)
2025-10-15 14:47:13 - INFO - ✅ ERP API 서버 재시작 성공
```

### 실시간 로그 확인 (PowerShell)

```powershell
Get-Content C:\Users\jmyang\Dropbox\1.0_tirepass\tgenai_gateway_monitor.log -Wait -Tail 50
```

---

## 문제 해결

### 1. psutil 설치 오류

**증상**: `ModuleNotFoundError: No module named 'psutil'`

**해결**:
```bash
cd C:\Users\jmyang\Dropbox\1.0_tirepass
venv\Scripts\pip install psutil
```

### 2. ERP API 서버가 계속 재시작됨

**원인**: Firebird DB 연결 문제

**확인 사항**:
- Firebird DB 서비스 실행 여부
- DB 파일 경로: `C:\Program Files\PsimCarS\Data\ITIRE.GDB`
- DB 연결 정보 (ID: SYSDBA, PW: masterkey)

**해결**:
1. Firebird 서비스 재시작
2. ERP API 서버 로그 확인

### 3. 작업 스케줄러에서 실행 안 됨

**확인 사항**:
- "가장 높은 수준의 권한으로 실행" 체크됨
- "사용자의 로그온 여부에 관계없이 실행" 선택됨
- 배치 파일 경로 정확한지 확인

**테스트**:
- 작업 스케줄러에서 작업 우클릭 → "실행" 클릭
- 로그 파일 생성되는지 확인

### 4. 로그 파일이 너무 큼

**해결**: 주기적으로 로그 파일 정리

```batch
REM 로그 파일 백업 및 초기화
cd C:\Users\jmyang\Dropbox\1.0_tirepass
copy tgenai_gateway_monitor.log tgenai_gateway_monitor_backup_%date:~0,4%%date:~5,2%%date:~8,2%.log
echo. > tgenai_gateway_monitor.log
```

### 5. PythonAnywhere 연결 실패 계속됨

**원인**: 인터넷 연결 문제 또는 PythonAnywhere 서버 다운

**확인**:
```bash
# 브라우저에서 접속 테스트
https://tirepass.pythonanywhere.com/api/admin/erp/status/
```

---

## 시스템 상태 확인 명령어

### Windows 명령 프롬프트

```batch
# 작업 스케줄러 작업 상태 확인
schtasks /query /tn "TgenAI_ERP_Gateway_Monitor"

# ERP API 서버 프로세스 확인
tasklist | findstr python

# 포트 8000 사용 프로세스 확인
netstat -ano | findstr :8000
```

### PowerShell

```powershell
# 게이트웨이 모니터 프로세스 확인
Get-Process python | Where-Object {$_.Path -like "*tgenai_erp_gateway_monitor*"}

# 로그 실시간 확인
Get-Content C:\Users\jmyang\Dropbox\1.0_tirepass\tgenai_gateway_monitor.log -Wait -Tail 20

# ERP API 헬스체크
Invoke-WebRequest -Uri "http://localhost:8000/health" | Select-Object -ExpandProperty Content
```

---

## 정리

### ✅ 설치 완료 체크리스트

- [ ] Python 패키지 설치 (`psutil`, `requests`)
- [ ] 배치 파일로 수동 실행 테스트
- [ ] 로그 파일 생성 확인
- [ ] ERP API 서버 자동 시작 확인
- [ ] Windows 작업 스케줄러 등록
- [ ] 시스템 재부팅 후 자동 시작 확인

### 🎯 기대 효과

1. **무중단 운영**: ERP API 서버 24/7 자동 관리
2. **즉시 복구**: 장애 발생 시 자동 재시작 (평균 10초)
3. **완전 자동화**: 사람 개입 없이 자동 복구
4. **가시성**: 모든 이벤트 로그 기록
5. **안정성**: 재시작 쿨다운으로 무한 재시작 방지

### 📞 문제 발생 시

1. 로그 파일 확인: `tgenai_gateway_monitor.log`
2. 수동 실행으로 오류 메시지 확인
3. Firebird DB 서비스 상태 확인
4. 네트워크 연결 상태 확인

---

**작성일**: 2025-10-15
**버전**: 1.0
**작성자**: Claude (TirePASS 시스템)

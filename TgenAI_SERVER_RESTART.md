# TgenAI ERP API 서버 재시작 가이드

## 현재 상황
- Firebird charset을 'NONE'으로 변경 (한글 인코딩 문제 해결)
- 변경사항 적용을 위해 FastAPI 서버 재시작 필요

## 재시작 방법

### 🎯 준비사항 (최초 1회만)
1. TeamViewer로 TgenAI PC 접속
2. 노트북 Dropbox 폴더에서 `restart_erp_api.bat` 파일을 TgenAI PC의 `C:\TgenAI\` 폴더로 복사

### 옵션 1: restart_erp_api.bat 스크립트 사용 (권장)

**TgenAI PC**에서 실행:
```cmd
cd C:\TgenAI
restart_erp_api.bat
```

또는 파일 탐색기에서 `C:\TgenAI\restart_erp_api.bat` 더블클릭

### 옵션 2: 수동 재시작

**TgenAI PC**에서 명령 프롬프트 실행:

#### 1단계: 현재 실행 중인 서버 종료
```cmd
# 8000번 포트 사용 중인 프로세스 찾기
netstat -ano | findstr :8000

# PID 확인 후 프로세스 종료 (PID는 위 명령에서 확인한 번호)
taskkill /F /PID <PID번호>
```

#### 2단계: 서버 재시작
```cmd
cd C:\TgenAI\erp_api
C:\TgenAI\venv\Scripts\python.exe erp_api_server.py
```

## 재시작 확인

### 1. 헬스 체크
브라우저에서 접속:
```
http://localhost:8000/health
```

또는 명령 프롬프트에서:
```cmd
powershell -Command "Invoke-RestMethod -Uri http://localhost:8000/health"
```

예상 결과:
```json
{
  "status": "healthy",
  "database": "connected",
  "total_goods": 6528
}
```

### 2. 한글 인코딩 확인
Django admin 페이지에서 상품 목록 확인:
```
https://tirepass.pythonanywhere.com/admin/tire_data/goods/
```

- 상품명이 한글로 정상 표시되는지 확인
- 분류(BUN1)가 한글로 정상 표시되는지 확인

## 문제 해결

### 서버가 시작되지 않는 경우
1. Firebird 데이터베이스 연결 확인:
   - ITIRE2.iptime.org에 접속 가능한지 확인
   - Firebird 서비스가 실행 중인지 확인

2. Python 환경 확인:
   ```cmd
   C:\TgenAI\venv\Scripts\python.exe --version
   C:\TgenAI\venv\Scripts\pip.exe list | findstr fdb
   ```

3. 포트 충돌 확인:
   ```cmd
   netstat -ano | findstr :8000
   ```

### 한글이 여전히 깨지는 경우
1. charset 설정 확인:
   ```python
   # C:\TgenAI\erp_api\erp_api_server.py 파일에서
   FIREBIRD_CONFIG = {
       'charset': 'NONE'  # 이 값이 'NONE'인지 확인
   }
   ```

2. 서버 재시작 확인:
   - 로그에서 "ERP API Server 시작" 메시지 확인
   - 타임스탬프가 최근인지 확인

## 24/7 자동 시작 설정 (추후 작업)

현재는 수동 시작이 필요합니다.
24/7 자동 시작을 위해서는 다음 작업이 필요:
- Windows 시작 프로그램 등록
- 또는 Windows 서비스로 등록
- 또는 Task Scheduler 활용

## 연락처
문제 발생시 시스템 관리자에게 문의

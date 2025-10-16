# 집 PC TgenAI 설치 가이드 (완전 자동화)

## 📋 개요
집 데스크톱 PC에 TgenAI ERP 게이트웨이를 설치하여 24/7 자동 운영합니다.

---

## ✅ 사전 준비 (집 PC에서 확인)

### 1. Python 설치 확인
```cmd
python --version
```

**Python이 없다면:**
- https://www.python.org/downloads/ 에서 Python 3.11 이상 설치
- 설치 시 "Add Python to PATH" 체크 필수!

### 2. 인터넷 연결 확인
```cmd
ping itire2.iptime.org
```

---

## 🚀 설치 방법 (5분)

### 1단계: TgenAI 폴더 생성

```cmd
cd C:\
mkdir TgenAI
cd TgenAI
```

### 2단계: 필요한 파일 복사

**노트북에서 집 PC로 복사할 파일들:**
```
C:\Users\jmyang\Dropbox\1.0_tirepass\TgenAI_INSTALL\
  ├─ erp_api_server.py
  ├─ tgenai_erp_gateway_monitor.py
  ├─ requirements.txt
  ├─ install.bat
  └─ register_autostart.bat
```

**방법 1: TeamViewer 파일 전송**
- TeamViewer에서 "파일 전송" 클릭
- 위 파일들을 C:\TgenAI\ 폴더로 복사

**방법 2: Dropbox 공유**
- 노트북: TgenAI_INSTALL 폴더를 Dropbox에 복사
- 집 PC: Dropbox에서 다운로드하여 C:\TgenAI\로 이동

### 3단계: 자동 설치 실행

```cmd
cd C:\TgenAI
install.bat
```

이 명령어가 자동으로:
- ✅ Python 가상환경 생성
- ✅ 필요한 패키지 설치
- ✅ ERP DB 연결 테스트
- ✅ FastAPI 서버 테스트

### 4단계: 자동 시작 등록

```cmd
cd C:\TgenAI
register_autostart.bat
```

이 명령어가 자동으로:
- ✅ Windows 작업 스케줄러 등록
- ✅ 부팅 시 자동 시작 설정
- ✅ 게이트웨이 모니터 시작

---

## ✅ 설치 완료 확인

### 1. 서비스 상태 확인
브라우저에서 접속:
```
http://localhost:8002/health
```

**예상 결과:**
```json
{
  "status": "healthy",
  "database": "itire_db",
  "total_goods": 12345
}
```

### 2. PythonAnywhere 연동 확인
PythonAnywhere Admin에서:
```
https://tirepass.pythonanywhere.com/admin/tire_data/erpsnapshot/
```

최신 스냅샷이 생성되는지 확인

---

## 🔧 문제 해결

### 오류 1: Python을 찾을 수 없음
```
해결: Python 재설치, "Add to PATH" 체크
```

### 오류 2: ERP DB 연결 실패
```cmd
# MariaDB 접속 테스트
mysql -h itire2.iptime.org -u root -ptirepass itire_db
```

### 오류 3: 포트 8002가 이미 사용 중
```cmd
# 실행 중인 프로세스 확인
netstat -ano | findstr :8002

# 프로세스 종료
taskkill /PID [프로세스ID] /F
```

---

## 📊 로그 확인

**설치 로그:**
```
C:\TgenAI\install.log
```

**실행 로그:**
```
C:\TgenAI\tgenai_gateway_monitor.log
```

---

## 🎯 최종 확인 사항

- [ ] Python 설치됨
- [ ] TgenAI 폴더 생성 (C:\TgenAI\)
- [ ] 모든 파일 복사 완료
- [ ] install.bat 실행 성공
- [ ] http://localhost:8002/health 접속 가능
- [ ] register_autostart.bat 실행 성공
- [ ] PC 재부팅 후 자동 시작 확인

---

**작성일:** 2025-10-16
**예상 시간:** 5-10분

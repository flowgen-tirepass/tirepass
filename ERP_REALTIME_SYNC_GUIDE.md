# ERP 실시간 동기화 설치 가이드

광주 ERP 서버에서 PythonAnywhere로 실시간 데이터 동기화

## 📋 개요

**동작 방식:**
1. Firebird 트리거가 CUSTOMS/GOODS 테이블 변경 감지
2. 변경 로그를 SYNC_LOG 테이블에 기록
3. Python 데몬이 SYNC_LOG를 주기적으로 확인
4. PythonAnywhere API로 변경 데이터 전송
5. PythonAnywhere MySQL 실시간 업데이트

**장점:**
- 거의 실시간 동기화 (5초 간격)
- 트랜잭션 안전성 보장
- 에러 처리 및 재시도 기능
- 변경 이력 추적 가능

---

## 🔧 1단계: Firebird 트리거 설치 (광주 ERP 서버)

### 1.1 FlameRobin 또는 isql로 접속

```bash
# Windows 명령 프롬프트
cd "C:\Program Files\Firebird\Firebird_3_0"
isql.exe -user SYSDBA -password masterkey "C:\Program Files\PsimCarS\Data\ITIRE.GDB"
```

### 1.2 트리거 SQL 실행

```sql
-- erp_sync_trigger.sql 파일 내용 복사하여 실행
INPUT 'C:\path\to\erp_sync_trigger.sql';
```

또는 FlameRobin GUI에서:
1. 데이터베이스 연결
2. SQL 에디터 열기
3. `erp_sync_trigger.sql` 파일 내용 붙여넣기
4. 실행 (F4)

### 1.3 트리거 확인

```sql
-- 설치된 트리거 확인
SELECT
    RDB$TRIGGER_NAME,
    RDB$RELATION_NAME,
    RDB$TRIGGER_TYPE
FROM RDB$TRIGGERS
WHERE RDB$RELATION_NAME IN ('CUSTOMS', 'GOODS')
  AND RDB$SYSTEM_FLAG = 0;

-- 결과:
-- TRG_CUSTOMS_AI (CUSTOMS - AFTER INSERT)
-- TRG_CUSTOMS_AU (CUSTOMS - AFTER UPDATE)
-- TRG_CUSTOMS_AD (CUSTOMS - AFTER DELETE)
-- TRG_GOODS_AI (GOODS - AFTER INSERT)
-- TRG_GOODS_AU (GOODS - AFTER UPDATE)
-- TRG_GOODS_AD (GOODS - AFTER DELETE)
```

---

## 🐍 2단계: Python 동기화 데몬 설치 (광주 ERP 서버)

### 2.1 Python 설치 확인

```bash
python --version
# Python 3.8 이상 필요
```

### 2.2 필요 라이브러리 설치

```bash
# 프로젝트 디렉토리 생성
mkdir C:\TirepassSync
cd C:\TirepassSync

# 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 라이브러리 설치
pip install fdb requests
```

### 2.3 동기화 스크립트 복사

- `scripts/erp_sync_daemon.py` 파일을 `C:\TirepassSync\` 폴더에 복사

### 2.4 설정 수정

`erp_sync_daemon.py` 파일 열기:

```python
# PythonAnywhere API 정보 수정
PYTHONANYWHERE_API = {
    'base_url': 'https://tirepass.pythonanywhere.com/api',
    'api_key': 'tirepass_erp_sync_key_2024_change_in_production',  # 여기 수정
    'timeout': 30
}

# Firebird 연결 정보 (로컬 서버이므로 localhost 사용)
FIREBIRD_CONFIG = {
    'host': 'localhost',
    'database': r'C:\Program Files\PsimCarS\Data\ITIRE.GDB',
    'user': 'SYSDBA',
    'password': 'masterkey',
    'charset': 'NONE'
}
```

### 2.5 수동 테스트

```bash
cd C:\TirepassSync
venv\Scripts\activate
python erp_sync_daemon.py
```

로그 확인:
```
=== ERP 동기화 데몬 시작 ===
Firebird: localhost
PythonAnywhere: https://tirepass.pythonanywhere.com/api
폴링 간격: 5초
처리할 로그 0개 발견
```

---

## 🖥️ 3단계: Windows 서비스 등록 (자동 실행)

### 방법 1: NSSM 사용 (권장)

```bash
# NSSM 다운로드: https://nssm.cc/download

# 서비스 설치
nssm install TirepassSync "C:\TirepassSync\venv\Scripts\python.exe" "C:\TirepassSync\erp_sync_daemon.py"

# 서비스 시작
nssm start TirepassSync

# 서비스 상태 확인
nssm status TirepassSync
```

### 방법 2: Windows 작업 스케줄러

1. `작업 스케줄러` 실행
2. `기본 작업 만들기` 클릭
3. 이름: `TirepassSync`
4. 트리거: `컴퓨터를 시작할 때`
5. 동작: `프로그램 시작`
   - 프로그램: `C:\TirepassSync\venv\Scripts\python.exe`
   - 인수: `C:\TirepassSync\erp_sync_daemon.py`
   - 시작 위치: `C:\TirepassSync`
6. 완료

---

## 🌐 4단계: PythonAnywhere 설정

### 4.1 코드 배포

```bash
# PythonAnywhere Bash 콘솔
cd ~/tirepass
git pull

# 웹 앱 재시작
# PythonAnywhere 웹 인터페이스에서 "Reload" 버튼 클릭
```

### 4.2 환경변수 설정 (WSGI 파일)

```python
# /var/www/tirepass_pythonanywhere_com_wsgi.py
import os

os.environ['ERP_SYNC_API_KEY'] = 'tirepass_erp_sync_key_2024_change_in_production'
```

### 4.3 API 테스트

```bash
# 상태 확인 API
curl -H "Authorization: Bearer tirepass_erp_sync_key_2024_change_in_production" \
  https://tirepass.pythonanywhere.com/api/sync/status/

# 응답:
# {"success": true, "customers": 1368, "goods": 15234, "timestamp": "2024-10-10T..."}
```

---

## ✅ 5단계: 동기화 테스트

### 5.1 ERP에서 데이터 변경

```sql
-- Firebird (광주 ERP 서버)
UPDATE CUSTOMS SET NAME = '테스트변경' WHERE CODE = '0-0-0002';
COMMIT;
```

### 5.2 SYNC_LOG 확인

```sql
-- 로그 테이블에 기록되었는지 확인
SELECT * FROM SYNC_LOG ORDER BY LOG_ID DESC ROWS 5;
```

### 5.3 동기화 데몬 로그 확인

```bash
# C:\TirepassSync\erp_sync_daemon.log
2024-10-10 15:30:05 - INFO - 처리 중: CUSTOMS.0-0-0002 (UPDATE)
2024-10-10 15:30:05 - INFO - 성공: CUSTOMS.0-0-0002
```

### 5.4 PythonAnywhere 데이터 확인

```bash
# PythonAnywhere Bash
mysql -h tirepass.mysql.pythonanywhere-services.com -u tirepass -p \
  -e "SELECT NAME FROM tirepass\$itire_db.customers WHERE CODE='0-0-0002';"

# 결과: 테스트변경
```

---

## 🔍 모니터링 및 관리

### 로그 파일 위치

```
C:\TirepassSync\erp_sync_daemon.log
```

### 동기화 상태 확인

```sql
-- 대기 중인 로그
SELECT COUNT(*) FROM SYNC_LOG WHERE SYNC_STATUS = 'PENDING';

-- 에러 발생 로그
SELECT * FROM SYNC_LOG WHERE SYNC_STATUS = 'ERROR';

-- 최근 동기화 로그
SELECT * FROM SYNC_LOG ORDER BY CHANGED_AT DESC ROWS 10;
```

### 재시도 실패 로그 처리

```sql
-- 재시도 횟수 초기화 (수동 재처리)
UPDATE SYNC_LOG
SET SYNC_STATUS = 'PENDING', RETRY_COUNT = 0, ERROR_MESSAGE = NULL
WHERE SYNC_STATUS = 'ERROR' AND LOG_ID = ?;
COMMIT;
```

---

## 🛠️ 문제 해결

### 1. 트리거가 작동하지 않음

```sql
-- 트리거 활성화 상태 확인
SELECT RDB$TRIGGER_NAME, RDB$TRIGGER_INACTIVE
FROM RDB$TRIGGERS
WHERE RDB$RELATION_NAME IN ('CUSTOMS', 'GOODS');

-- INACTIVE = 1이면 비활성화됨
-- 활성화:
ALTER TRIGGER TRG_CUSTOMS_AI ACTIVE;
```

### 2. 동기화 데몬이 연결되지 않음

```bash
# Firebird 서버 확인
netstat -an | findstr 3050

# 방화벽 확인
# Windows Defender 방화벽 > 인바운드 규칙 > Firebird 포트 3050 허용
```

### 3. PythonAnywhere API 에러

```bash
# API 키 확인
echo $ERP_SYNC_API_KEY

# 로그 확인
tail -f ~/tirepass/logs/django.log
```

---

## 📊 성능 튜닝

### 폴링 간격 조정

```python
# erp_sync_daemon.py
SYNC_CONFIG = {
    'poll_interval': 5,  # 5초 (기본) → 1초 (빠름) or 30초 (절약)
    'batch_size': 100,
    'max_retry': 3
}
```

### 일괄 처리 크기 조정

```python
SYNC_CONFIG = {
    'poll_interval': 5,
    'batch_size': 100,  # 100개 (기본) → 500개 (대량 처리)
    'max_retry': 3
}
```

---

## 📝 유지보수

### 로그 정리 (주기적으로 실행)

```sql
-- 30일 이상 지난 성공 로그 삭제
DELETE FROM SYNC_LOG
WHERE SYNC_STATUS = 'SENT'
  AND CHANGED_AT < DATEADD(-30 DAY TO CURRENT_TIMESTAMP);
COMMIT;
```

### 서비스 재시작

```bash
# NSSM 사용 시
nssm restart TirepassSync

# 작업 스케줄러 사용 시
# 작업 스케줄러에서 작업 종료 후 다시 실행
```

---

## 🚀 완료!

이제 광주 ERP 서버에서 CUSTOMS/GOODS 테이블이 변경되면:
1. 트리거가 자동으로 SYNC_LOG에 기록
2. Python 데몬이 5초마다 확인
3. PythonAnywhere API로 전송
4. MySQL 데이터 실시간 업데이트

**모니터링 대시보드:** https://tirepass.pythonanywhere.com/admin/

**API 상태 확인:** https://tirepass.pythonanywhere.com/api/sync/status/

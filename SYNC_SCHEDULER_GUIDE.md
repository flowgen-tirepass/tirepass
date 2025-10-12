# ERP 상품 자동 동기화 스케줄러 설정 가이드

## 개요
ERP API의 실시간 상품 데이터를 MySQL DB에 자동으로 동기화하여 PC 관리자와 모바일 앱의 재고 정보를 일치시킵니다.

---

## 1. 로컬 개발 환경 (Windows)

### 1-1. 수동 동기화 (즉시 실행)
```bash
cd C:\Users\jmyang\Dropbox\1.0_tirepass
venv\Scripts\python.exe manage.py sync_erp_goods
```

### 1-2. 자동 동기화 스케줄러 실행
```bash
# 5분 간격 (기본값)
venv\Scripts\python.exe scripts\auto_sync_scheduler.py

# 10분 간격
set SYNC_INTERVAL_MINUTES=10
venv\Scripts\python.exe scripts\auto_sync_scheduler.py
```

### 1-3. 중지
```
Ctrl + C
```

---

## 2. PythonAnywhere 배포

### 2-1. 파일 업로드
Git으로 최신 코드 가져오기:
```bash
cd ~/tirepass
git pull origin main
```

### 2-2. Django Management Command 실행 (수동)
```bash
cd ~/tirepass
python manage.py sync_erp_goods
```

### 2-3. 자동 스케줄러 실행 (백그라운드)

#### 로그 디렉토리 생성
```bash
cd ~/tirepass
mkdir -p logs
```

#### 백그라운드 실행
```bash
cd ~/tirepass
nohup python scripts/auto_sync_scheduler.py > logs/sync_scheduler.log 2>&1 &
```

#### 실행 확인
```bash
# 프로세스 확인
ps aux | grep auto_sync_scheduler

# 로그 실시간 확인
tail -f ~/tirepass/logs/sync_scheduler.log
```

#### 중지
```bash
# 프로세스 ID 확인
ps aux | grep auto_sync_scheduler

# 프로세스 종료
kill <PID>

# 또는 강제 종료
killall -9 python
```

### 2-4. PythonAnywhere 스케줄러 사용 (권장)

**PythonAnywhere 무료 플랜 제한:**
- 하루 1번 실행만 가능
- 5분 간격 실행 불가

**대안: Scheduled Tasks 설정**
1. PythonAnywhere → Tasks 탭
2. **Add a new scheduled task** 클릭
3. 명령어 입력:
```bash
cd ~/tirepass && python manage.py sync_erp_goods
```
4. 시간 설정: 매일 특정 시간 (예: 09:00)
5. **Create** 클릭

---

## 3. 동기화 간격 설정

| 간격 | 재고 오차 | 서버 부하 | 사용자 경험 | 권장 환경 |
|------|-----------|-----------|-------------|-----------|
| **3분** | 최소 | 높음 | 최상 | 로컬 개발 |
| **5분** | 낮음 | 중간 | 우수 | **운영 환경 (권장)** |
| **10분** | 중간 | 낮음 | 양호 | 트래픽 적은 환경 |
| **30분** | 높음 | 매우 낮음 | 보통 | 백업용 |

### 환경변수로 간격 조정
```bash
# 3분 간격
export SYNC_INTERVAL_MINUTES=3
python scripts/auto_sync_scheduler.py

# 10분 간격
export SYNC_INTERVAL_MINUTES=10
python scripts/auto_sync_scheduler.py
```

---

## 4. 모니터링

### 로그 확인
```bash
# 전체 로그
cat ~/tirepass/logs/sync_scheduler.log

# 최근 50줄
tail -50 ~/tirepass/logs/sync_scheduler.log

# 실시간 확인
tail -f ~/tirepass/logs/sync_scheduler.log
```

### 동기화 성공 확인
```bash
# 최근 동기화 결과만 보기
grep "동기화 완료" ~/tirepass/logs/sync_scheduler.log | tail -5

# 에러만 보기
grep "ERROR" ~/tirepass/logs/sync_scheduler.log | tail -10
```

---

## 5. 문제 해결

### 문제: 프로세스가 실행 중인지 확인
```bash
ps aux | grep auto_sync_scheduler
```

### 문제: 로그 파일이 너무 큼
```bash
# 로그 파일 크기 확인
du -h ~/tirepass/logs/sync_scheduler.log

# 로그 백업 후 삭제
mv ~/tirepass/logs/sync_scheduler.log ~/tirepass/logs/sync_scheduler_$(date +%Y%m%d).log
touch ~/tirepass/logs/sync_scheduler.log
```

### 문제: 동기화 실패
```bash
# 에러 로그 확인
tail -100 ~/tirepass/logs/sync_scheduler.log

# ERP API 연결 테스트
curl http://itire2.iptime.org:8002/goods?limit=1

# Django 설정 확인
cd ~/tirepass
python manage.py check
```

---

## 6. 성능 및 리소스

### 예상 리소스 사용량
- **메모리:** ~100MB
- **CPU:** 동기화 중 10-20%, 대기 중 0%
- **네트워크:** 동기화당 ~5-10MB
- **디스크 I/O:** 낮음

### 동기화 소요 시간
- **상품 5,000개:** 약 30초
- **상품 10,000개:** 약 60초
- **상품 20,000개:** 약 120초

---

## 7. 보안

### 권장 사항
1. **로그 파일 권한 설정**
```bash
chmod 600 ~/tirepass/logs/sync_scheduler.log
```

2. **환경변수로 민감 정보 관리**
```bash
# .env 파일 사용
ERP_API_URL=http://itire2.iptime.org:8002
SYNC_INTERVAL_MINUTES=5
```

---

## 8. 자주 묻는 질문 (FAQ)

### Q: PythonAnywhere 무료 플랜에서 5분마다 실행 가능한가요?
A: **아니오.** 무료 플랜은 하루 1번만 가능합니다. 유료 플랜 필요합니다.

### Q: 백그라운드 프로세스가 멈추면 어떻게 되나요?
A: 자동으로 재시작되지 않습니다. 모니터링 스크립트를 추가로 구현하거나, systemd (Linux)를 사용하세요.

### Q: 동기화 중 DB가 잠기나요?
A: 아니오. `update_or_create`는 row-level lock을 사용하여 읽기/쓰기 동시 가능합니다.

### Q: 동기화 실패 시 알림을 받을 수 있나요?
A: 현재는 로그 파일만 기록됩니다. 이메일/슬랙 알림은 추가 구현이 필요합니다.

---

## 9. 다음 단계

### 개선 사항 (선택 사항)
1. **이메일 알림**: 동기화 실패 시 관리자에게 이메일 발송
2. **헬스 체크**: 웹 엔드포인트로 스케줄러 상태 확인
3. **Systemd 서비스** (Linux): 자동 재시작 설정
4. **증분 동기화**: 변경된 상품만 업데이트 (성능 개선)

---

## 10. 연락처

문제 발생 시:
1. 로그 파일 확인
2. GitHub Issues에 보고
3. 관리자에게 문의

---

**작성일:** 2025-01-13
**버전:** 1.0

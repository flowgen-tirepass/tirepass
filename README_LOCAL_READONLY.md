# 로컬 개발환경 - PythonAnywhere 읽기 전용 연결

로컬에서 PythonAnywhere의 실제 데이터를 조회하면서 개발할 수 있습니다.

## 🔐 보안 설정

**중요:** 데이터 변경은 차단되며, 조회만 가능합니다.

## 📋 사전 준비

### 1. PythonAnywhere 데이터베이스 정보 확인

PythonAnywhere 웹 콘솔에서:
- **Database 탭** 접속
- MySQL 호스트: `tirepass.mysql.pythonanywhere-services.com`
- 데이터베이스명: `tirepass$itire_db`
- 사용자명: `tirepass`
- 비밀번호: (설정된 비밀번호)

### 2. 외부 접속 허용 확인

**PythonAnywhere 무료 계정 제한:**
- 외부 MySQL 접속이 기본적으로 차단됨
- 화이트리스트에 등록된 IP만 접속 가능

**유료 계정:**
- 외부 MySQL 접속 가능
- 추가 설정 불필요

### 3. 환경 변수 설정 (선택사항)

`.env` 파일 생성:

```env
PYTHONANYWHERE_DB_HOST=tirepass.mysql.pythonanywhere-services.com
PYTHONANYWHERE_DB_NAME=tirepass$itire_db
PYTHONANYWHERE_DB_USER=tirepass
PYTHONANYWHERE_DB_PASSWORD=your_password_here
```

## 🚀 사용 방법

### 1. 읽기 전용 모드로 서버 실행

```cmd
cd C:\Users\jmyang\Dropbox\1.0_tirepass
python manage.py runserver --settings=itire.settings_local
```

### 2. 관리자 페이지 접속

```
URL: http://127.0.0.1:8000/admin/
Username: admin
Password: tirepass2024!
```

## ✅ 기능

### 허용되는 작업
- ✅ 데이터 조회
- ✅ 목록 보기
- ✅ 상세 정보 확인
- ✅ 검색 및 필터링
- ✅ 로그인/로그아웃

### 차단되는 작업
- ❌ 데이터 추가
- ❌ 데이터 수정
- ❌ 데이터 삭제
- ❌ 일괄 삭제 액션

## 🔍 화면 표시

### 읽기 전용 경고
관리자 페이지 상단에 경고 메시지 표시:
```
🔒 읽기 전용 모드: PythonAnywhere 데이터를 조회만 할 수 있습니다.
```

### 버튼 숨김
- "추가" 버튼 숨김
- "저장" 버튼 숨김
- "삭제" 버튼 숨김

## ⚠️ 주의사항

### 1. 외부 접속 제한
PythonAnywhere 무료 계정은 외부 MySQL 접속이 제한됩니다.

**해결 방법:**
- 유료 계정으로 업그레이드
- SSH 터널링 사용
- VPN을 통한 화이트리스트 IP 사용

### 2. 연결 오류 처리
연결 실패 시 에러 메시지:
```
django.db.utils.OperationalError: (2003, "Can't connect to MySQL server...")
```

**해결 방법:**
- PythonAnywhere에서 외부 접속 허용 확인
- 방화벽 설정 확인
- 비밀번호 확인

### 3. 읽기 전용 모드 해제
일반 모드로 돌아가려면:

```cmd
python manage.py runserver
```

(settings_local 없이 실행)

## 🛠️ 트러블슈팅

### 연결 테스트

```cmd
python manage.py shell --settings=itire.settings_local
```

Shell에서:
```python
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM goods")
    print(cursor.fetchone())
```

### 연결 타임아웃 조정

`settings_local.py`에서:
```python
'connect_timeout': 30,  # 기본 10초에서 30초로 증가
```

## 📊 데이터 동기화

로컬에서는 **조회만** 가능하므로:
- PythonAnywhere의 실시간 데이터 확인 가능
- ERP 동기화 상태 모니터링 가능
- 실제 운영 환경 디버깅 가능

## 🔄 일반 모드와 비교

| 항목 | 일반 모드 | 읽기 전용 모드 |
|------|----------|---------------|
| 데이터베이스 | 로컬 MySQL | PythonAnywhere MySQL |
| 데이터 조회 | ✅ | ✅ |
| 데이터 추가 | ✅ | ❌ |
| 데이터 수정 | ✅ | ❌ |
| 데이터 삭제 | ✅ | ❌ |
| ERP 동기화 | 로컬 서버 필요 | 실시간 확인 가능 |

## 📝 파일 구조

```
itire/
├── settings.py              # 일반 모드 (로컬 DB)
├── settings_local.py        # 읽기 전용 모드 (PythonAnywhere DB)

tire_data/
├── middleware.py            # 읽기 전용 미들웨어
├── admin_readonly.py        # 읽기 전용 Admin 믹스인
```

## 🎯 사용 사례

1. **실제 데이터로 개발**: 로컬에서 실제 운영 데이터 확인
2. **디버깅**: 운영 환경의 이슈 재현 및 분석
3. **데이터 확인**: 고객 문의 시 실시간 데이터 조회
4. **ERP 모니터링**: 실시간 동기화 상태 확인

---

**보안 알림:** 읽기 전용 모드에서는 데이터 변경이 완전히 차단됩니다. 안전하게 운영 데이터를 조회할 수 있습니다.

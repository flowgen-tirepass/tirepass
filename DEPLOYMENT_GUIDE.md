# PythonAnywhere 배포 가이드

## 개요
이 문서는 TirePASS 프로젝트를 PythonAnywhere에 배포하는 단계별 가이드입니다.

## 전제 조건
- ✅ PythonAnywhere 계정 생성 완료
- ✅ ERP 서버에서 pythonanywhere MySQL로 트리거 설정 완료
- ✅ 로컬에서 모든 기능 테스트 완료

---

## 1단계: pythonanywhere MySQL 데이터베이스 설정

### 1.1 MySQL 데이터베이스 접속
1. PythonAnywhere 대시보드에서 **Databases** 탭 클릭
2. MySQL 비밀번호 설정 (아직 설정하지 않은 경우)
3. 데이터베이스 이름 확인: `yourusername$itire_db`

### 1.2 테이블 생성
1. **MySQL console** 열기 (Databases 탭에서)
2. `pythonanywhere_tables.sql` 파일 내용 복사
3. MySQL console에 붙여넣기 및 실행
4. 테이블 생성 확인:
   ```sql
   USE yourusername$itire_db;
   SHOW TABLES;
   ```

### 1.3 ERP 트리거 확인
ERP 서버에서 다음 테이블들이 실시간으로 동기화되는지 확인:
- `goods` - 상품 정보
- `customers_simple` - 고객 정보

---

## 2단계: 코드 업로드

### 방법 A: Git 사용 (권장)
1. PythonAnywhere Bash console 열기
2. Git repository clone:
   ```bash
   cd ~
   git clone [your-repo-url] itire
   cd itire
   ```

### 방법 B: Files 탭 사용
1. **Files** 탭에서 `/home/yourusername/` 디렉토리로 이동
2. `itire` 폴더 생성
3. 다음 파일/폴더 업로드:
   - `manage.py`
   - `requirements.txt`
   - `pythonanywhere_wsgi.py`
   - `itire/` (전체 폴더)
   - `tire_data/` (전체 폴더)
   - `templates/` (전체 폴더)
   - `static/` (전체 폴더)

### 업로드하지 않을 것
- ❌ `venv/`, `__pycache__/`, `*.pyc`
- ❌ `debug.log`, `*.db`
- ❌ `mobile/`, `work/`, `data/`
- ❌ `node_modules/`, `.claude/`

---

## 3단계: 가상환경 생성 및 패키지 설치

### 3.1 Bash console에서 실행
```bash
cd ~/itire

# Python 3.10 가상환경 생성
mkvirtualenv --python=/usr/bin/python3.10 itire-venv

# 가상환경 활성화
workon itire-venv

# 패키지 설치
pip install -r requirements.txt
```

### 3.2 설치 확인
```bash
pip list
# Django, mysqlclient, requests 등 확인
```

---

## 4단계: Django 설정 수정

### 4.1 settings.py 환경 변수 설정

PythonAnywhere 환경에 맞게 설정을 변경해야 합니다.

#### 옵션 1: 환경 변수 사용 (권장)
Web 탭 > WSGI configuration file에서 환경 변수 추가:
```python
import os
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'
os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'
os.environ['DB_NAME'] = 'yourusername$itire_db'
os.environ['DB_USER'] = 'yourusername'
os.environ['DB_PASSWORD'] = 'your-mysql-password'
os.environ['DB_HOST'] = 'yourusername.mysql.pythonanywhere-services.com'
```

#### 옵션 2: settings_production.py 사용
```bash
# settings_production.py 파일이 있다면
export DJANGO_SETTINGS_MODULE=itire.settings_production
```

### 4.2 필수 설정 항목
```python
DEBUG = False
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yourusername$itire_db',
        'USER': 'yourusername',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'yourusename.mysql.pythonanywhere-services.com',
        'PORT': '3306',
    }
}
CSRF_TRUSTED_ORIGINS = ['https://yourusername.pythonanywhere.com']
```

---

## 5단계: Static 파일 수집

```bash
cd ~/itire
workon itire-venv
python manage.py collectstatic --noinput
```

---

## 6단계: Django 마이그레이션 실행

```bash
cd ~/itire
workon itire-venv

# 마이그레이션 생성 (필요시)
python manage.py makemigrations

# 마이그레이션 적용 (Django 기본 테이블만)
# managed=False 테이블은 이미 SQL로 생성했으므로 --fake 사용
python manage.py migrate --fake-initial
```

---

## 7단계: Web App 설정

### 7.1 Web 탭에서 설정
1. **Web** 탭 클릭
2. **Add a new web app** 클릭
3. **Manual configuration** 선택
4. **Python 3.10** 선택

### 7.2 WSGI Configuration
1. **Code** 섹션에서 **WSGI configuration file** 링크 클릭
2. 기존 내용 삭제하고 다음 내용으로 교체:

```python
import os
import sys

# 프로젝트 경로 추가
path = '/home/yourusername/itire'
if path not in sys.path:
    sys.path.append(path)

# Django 환경 변수 설정
os.environ['DJANGO_SETTINGS_MODULE'] = 'itire.settings'

# 환경 변수 설정
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 7.3 Virtualenv 설정
1. **Virtualenv** 섹션에서 경로 입력:
   ```
   /home/yourusername/.virtualenvs/itire-venv
   ```

### 7.4 Static Files 설정
1. **Static files** 섹션에서 매핑 추가:
   ```
   URL: /static/
   Directory: /home/yourusername/itire/staticfiles
   ```

---

## 8단계: Web App 재시작 및 확인

### 8.1 재시작
1. **Web** 탭 상단의 **Reload** 버튼 클릭

### 8.2 로그 확인
에러가 발생한 경우:
1. **Web** 탭 > **Log files** 섹션
2. Error log, Server log 확인

---

## 9단계: 테스트

### 9.1 기본 접속 테스트
```
https://yourusername.pythonanywhere.com/
```

### 9.2 관리자 페이지 테스트
```
https://yourusername.pythonanywhere.com/admin/
- 로그인: admin / admin1234
```

### 9.3 모바일 페이지 테스트
```
https://yourusername.pythonanywhere.com/mobile/
```

### 9.4 API 테스트
```bash
# 상품 목록 API
curl https://yourusername.pythonanywhere.com/api/mobile/products/

# 로그인 API
curl -X POST https://yourusername.pythonanywhere.com/api/mobile/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"customer_code":"C001","password":"test1234"}'
```

---

## 10단계: ERP 트리거 연동 테스트

### 10.1 상품 데이터 확인
1. ERP에서 상품 추가/수정
2. pythonanywhere MySQL에 실시간 반영 확인:
   ```sql
   SELECT * FROM goods ORDER BY code DESC LIMIT 10;
   ```

### 10.2 고객 데이터 확인
1. ERP에서 고객 추가/수정
2. pythonanywhere MySQL에 실시간 반영 확인:
   ```sql
   SELECT * FROM customers_simple ORDER BY code DESC LIMIT 10;
   ```

---

## 11단계: 로컬 테스트 데이터 삭제

⚠️ **배포 후 즉시 실행**

로컬 데스크톱에서 테스트 데이터 삭제:

```sql
-- 로컬 itire_db에서 실행
USE itire_db;

-- 테스트 고객 삭제
DELETE FROM customers_simple WHERE code IN ('C001', 'C002', 'testcar');

-- 테스트 주문 삭제
DELETE FROM orders WHERE customer_code IN ('C001', 'C002', 'testcar');

-- 테스트 장바구니 삭제
DELETE FROM shopping_cart WHERE customer_code IN ('C001', 'C002', 'testcar');

-- 확인
SELECT * FROM customers_simple;
SELECT * FROM orders;
SELECT * FROM shopping_cart;
```

---

## 문제 해결

### 500 Internal Server Error
1. Error log 확인 (Web 탭)
2. settings.py의 ALLOWED_HOSTS 확인
3. WSGI configuration 파일 확인
4. MySQL 연결 정보 확인

### Static 파일 로딩 안 됨
1. `python manage.py collectstatic` 재실행
2. Static files 매핑 확인 (Web 탭)

### MySQL 연결 오류
1. Database 탭에서 MySQL 비밀번호 확인
2. settings.py의 DB 설정 확인
3. Host 이름 확인 (pythonanywhere-services.com)

### Import 오류
1. 가상환경 활성화 확인: `workon itire-venv`
2. requirements.txt 재설치: `pip install -r requirements.txt`

---

## 체크리스트

배포 전:
- [ ] ERP 트리거 설정 완료
- [ ] 로컬에서 모든 기능 테스트 완료
- [ ] pythonanywhere_tables.sql 파일 준비

배포 중:
- [ ] MySQL 데이터베이스 생성
- [ ] pythonanywhere_tables.sql 실행
- [ ] 코드 업로드 완료
- [ ] 가상환경 생성 및 패키지 설치
- [ ] settings.py 환경 설정
- [ ] collectstatic 실행
- [ ] WSGI configuration 설정
- [ ] Web app 재시작

배포 후:
- [ ] 관리자 페이지 접속 확인
- [ ] 모바일 페이지 접속 확인
- [ ] ERP 트리거 동작 확인
- [ ] 로컬 테스트 데이터 삭제

---

## 참고 문서
- DEPLOYMENT_CHECKLIST.md - 배포 체크리스트
- pythonanywhere_tables.sql - MySQL 테이블 생성 스크립트
- requirements.txt - Python 패키지 의존성

# TirePASS PythonAnywhere 배포 가이드

## 1. 사전 준비

### 필수 정보
- PythonAnywhere 계정
- MariaDB/MySQL 데이터베이스 접속 정보
- 프로젝트 파일 업로드

### 환경 변수 설정값
배포 시 다음 환경 변수를 설정해야 합니다:

```bash
# Django 설정
DJANGO_SECRET_KEY=<새로운-시크릿-키-생성>
DEBUG=False
ALLOWED_HOSTS=<your-username>.pythonanywhere.com

# 데이터베이스 설정
DB_NAME=itire_db
DB_USER=<your-mysql-username>
DB_PASSWORD=<your-mysql-password>
DB_HOST=<your-mysql-hostname>.mysql.pythonanywhere-services.com
DB_PORT=3306

# CSRF 설정
CSRF_TRUSTED_ORIGINS=https://<your-username>.pythonanywhere.com
```

## 2. PythonAnywhere 배포 단계

### Step 1: 파일 업로드
1. PythonAnywhere Files 탭에서 프로젝트 폴더 생성
2. 프로젝트 파일 업로드 (zip 압축 후 업로드 권장)
   - `itire/` (Django 프로젝트 설정)
   - `tire_data/` (앱)
   - `templates/`
   - `static/`
   - `manage.py`
   - `requirements.txt`

### Step 2: MySQL 데이터베이스 설정
1. Databases 탭에서 MySQL 데이터베이스 생성
2. 데이터베이스명: `itire_db`
3. 백업 파일 복원:
   ```bash
   mysql -u <username> -h <hostname> -p <database_name> < db_dumps/itire_db_dump_20251002_201440.sql
   ```

### Step 3: 가상환경 및 패키지 설치
Bash 콘솔에서:
```bash
mkvirtualenv --python=python3.10 tirepass-env
pip install -r requirements.txt
```

### Step 4: 환경 변수 설정
`.env` 파일 생성 또는 PythonAnywhere Web 탭의 환경 변수 섹션에서 설정

### Step 5: Static 파일 수집
```bash
python manage.py collectstatic --noinput
```

### Step 6: 마이그레이션 (이미 존재하는 테이블이므로 fake)
```bash
python manage.py migrate --fake
```

### Step 7: 슈퍼유저 생성
```bash
python manage.py createsuperuser
```

### Step 8: Web 앱 설정
PythonAnywhere Web 탭에서:

1. **Source code**: `/home/<username>/tirepass/`
2. **Working directory**: `/home/<username>/tirepass/`
3. **Virtualenv**: `/home/<username>/.virtualenvs/tirepass-env`

4. **WSGI 파일 수정** (`/var/www/<username>_pythonanywhere_com_wsgi.py`):
```python
import os
import sys

# 프로젝트 경로 추가
path = '/home/<username>/tirepass'
if path not in sys.path:
    sys.path.append(path)

# Django 설정 모듈
os.environ['DJANGO_SETTINGS_MODULE'] = 'itire.settings'

# 환경 변수 설정 (또는 .env 파일 사용)
os.environ.setdefault('DJANGO_SECRET_KEY', '<your-secret-key>')
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('ALLOWED_HOSTS', '<username>.pythonanywhere.com')
os.environ.setdefault('DB_NAME', 'itire_db')
os.environ.setdefault('DB_USER', '<username>')
os.environ.setdefault('DB_PASSWORD', '<password>')
os.environ.setdefault('DB_HOST', '<username>.mysql.pythonanywhere-services.com')
os.environ.setdefault('DB_PORT', '3306')
os.environ.setdefault('CSRF_TRUSTED_ORIGINS', 'https://<username>.pythonanywhere.com')

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. **Static files 매핑**:
   - URL: `/static/`
   - Directory: `/home/<username>/tirepass/staticfiles/`

6. **Media files 매핑** (필요시):
   - URL: `/media/`
   - Directory: `/home/<username>/tirepass/media/`

### Step 9: 웹앱 재시작
Web 탭에서 "Reload" 버튼 클릭

## 3. 배포 후 확인

### 접속 테스트
1. `https://<username>.pythonanywhere.com/` - 메인 대시보드 (로그인 필요)
2. `https://<username>.pythonanywhere.com/admin/` - Django Admin

### 기능 확인
- [ ] 로그인 페이지 정상 작동
- [ ] 대시보드 접근 시 인증 확인
- [ ] 상품 목록 조회
- [ ] 고객 목록 조회
- [ ] Static 파일 로딩 (CSS, JS)
- [ ] Admin 페이지 접속

## 4. 보안 체크리스트

- [ ] `DEBUG=False` 설정 확인
- [ ] `SECRET_KEY` 새로 생성하여 안전하게 보관
- [ ] `ALLOWED_HOSTS`에 실제 도메인만 포함
- [ ] HTTPS 강제 (PythonAnywhere는 기본 제공)
- [ ] 데이터베이스 백업 주기적 실행
- [ ] Admin 계정 강력한 비밀번호 사용

## 5. 문제 해결

### Static 파일이 로드되지 않는 경우
```bash
python manage.py collectstatic --noinput
```
Web 탭에서 static files 매핑 재확인

### 데이터베이스 연결 오류
- 환경 변수 설정 확인
- MySQL 호스트명 확인 (pythonanywhere-services.com)
- 데이터베이스 사용자 권한 확인

### 500 에러 발생
- Error log 확인: PythonAnywhere Web 탭 → Log files
- `DEBUG=True`로 임시 변경하여 에러 메시지 확인 (완료 후 False로 복구)

## 6. 유지보수

### 코드 업데이트 시
1. 파일 업로드
2. `python manage.py collectstatic --noinput` (static 파일 변경 시)
3. `python manage.py migrate` (모델 변경 시)
4. Web 탭에서 "Reload" 버튼 클릭

### 데이터베이스 백업
```bash
mysqldump -u <username> -h <hostname> -p itire_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## 7. 참고사항

- PythonAnywhere 무료 계정은 1개의 웹앱만 가능
- MySQL 데이터베이스는 계정당 1개 제공 (무료)
- Static/Media 파일은 총 500MB 제한 (무료)
- 매일 자동 재시작 설정 권장 (Web 탭에서 설정 가능)

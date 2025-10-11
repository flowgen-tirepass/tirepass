# PythonAnywhere 배포 가이드

## 개요
이 문서는 TirePASS Django 프로젝트를 PythonAnywhere에 배포하는 방법을 설명합니다.

## 사전 준비

### 1. PythonAnywhere 계정 생성
- https://www.pythonanywhere.com 에서 무료 계정 생성
- 무료 플랜은 1개의 웹앱과 MySQL 데이터베이스를 제공합니다

### 2. 필요한 정보
- PythonAnywhere 사용자명 (예: yourusername)
- MySQL 데이터베이스 비밀번호

## 배포 단계

### 단계 1: 코드 업로드

#### 옵션 A: Git을 사용한 배포 (권장)
1. PythonAnywhere Bash 콘솔에서:
```bash
cd ~
git clone https://github.com/yourusername/tirepass.git
cd tirepass
```

#### 옵션 B: 파일 직접 업로드
1. PythonAnywhere Files 탭에서 파일을 직접 업로드
2. 또는 로컬에서 압축 후 업로드 후 압축 해제

### 단계 2: 가상환경 설정

PythonAnywhere Bash 콘솔에서:
```bash
cd ~/tirepass
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 단계 3: MySQL 데이터베이스 설정

1. PythonAnywhere 대시보드에서 "Databases" 탭 클릭
2. MySQL 비밀번호 설정 (처음 한 번만)
3. 새 데이터베이스 생성:
   - 데이터베이스 이름: `yourusername$itire_db`

4. MySQL 콘솔에서 데이터베이스 초기화:
```bash
mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p
```

```sql
USE yourusername$itire_db;

-- 테이블 생성 (마이그레이션 실행 필요)
-- 또는 기존 데이터베이스 덤프 임포트
```

### 단계 4: Django 설정 수정

1. `itire/settings_production.py` 파일에서 다음 정보 수정:
   - `ALLOWED_HOSTS`에 `yourusername.pythonanywhere.com` 추가
   - `DATABASES` 설정에서:
     - `NAME`: `yourusername$itire_db`
     - `USER`: `yourusername`
     - `PASSWORD`: MySQL 비밀번호
     - `HOST`: `yourusername.mysql.pythonanywhere-services.com`

### 단계 5: Static 파일 수집

Bash 콘솔에서:
```bash
cd ~/tirepass
source venv/bin/activate
python manage.py collectstatic --noinput
```

### 단계 6: 데이터베이스 마이그레이션

```bash
python manage.py migrate
```

### 단계 7: 웹 앱 설정

1. PythonAnywhere "Web" 탭 클릭
2. "Add a new web app" 클릭
3. "Manual configuration" 선택
4. Python 버전 선택 (3.10 이상 권장)

### 단계 8: WSGI 파일 설정

1. Web 탭에서 "WSGI configuration file" 링크 클릭
2. 파일 내용을 다음과 같이 수정:

```python
import os
import sys

# 프로젝트 경로 추가 (실제 사용자명으로 수정)
path = '/home/yourusername/tirepass'
if path not in sys.path:
    sys.path.insert(0, path)

# Django 설정 모듈 지정
os.environ['DJANGO_SETTINGS_MODULE'] = 'itire.settings_production'

# 가상환경 활성화
activate_this = '/home/yourusername/tirepass/venv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 단계 9: Virtualenv 설정

Web 탭에서:
1. "Virtualenv" 섹션에서 가상환경 경로 입력:
   ```
   /home/yourusername/tirepass/venv
   ```

### 단계 10: Static 파일 매핑

Web 탭의 "Static files" 섹션에서:

| URL          | Directory                                    |
|--------------|----------------------------------------------|
| /static/     | /home/yourusername/tirepass/staticfiles     |
| /media/      | /home/yourusername/tirepass/media           |

### 단계 11: 웹 앱 재시작

1. Web 탭 상단의 "Reload yourusername.pythonanywhere.com" 버튼 클릭
2. 사이트 접속 확인: `https://yourusername.pythonanywhere.com`

## 데이터베이스 마이그레이션

### 로컬 데이터를 PythonAnywhere로 이전

#### 옵션 1: MySQL 덤프 사용
로컬에서:
```bash
mysqldump -u root -p itire_db > itire_db_dump.sql
```

PythonAnywhere에서:
```bash
mysql -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p yourusername$itire_db < itire_db_dump.sql
```

#### 옵션 2: Django dumpdata/loaddata 사용
로컬에서:
```bash
python manage.py dumpdata > data.json
```

PythonAnywhere에 파일 업로드 후:
```bash
python manage.py loaddata data.json
```

## 환경변수 설정 (선택사항)

Bash 콘솔에서 `.env` 파일 생성:
```bash
cd ~/tirepass
nano .env
```

내용:
```
DEBUG=False
SECRET_KEY=your-secret-key-here
DB_PASSWORD=your-mysql-password
```

## 주의사항

### 무료 플랜 제한사항
- 1개의 웹앱만 운영 가능
- 하루 100초 CPU 시간 제한
- 3개월마다 웹앱 재활성화 필요
- 24시간마다 자동으로 웹앱이 중지됨 (재접속시 자동 시작)

### Firebird 데이터베이스
- PythonAnywhere는 Firebird를 직접 지원하지 않습니다
- 해결책:
  1. 로컬에서 Firebird → MariaDB 동기화 스크립트 실행
  2. MariaDB 데이터를 PythonAnywhere MySQL로 정기적으로 동기화
  3. 또는 로컬 서버를 API 서버로 운영하고 PythonAnywhere를 프론트엔드로 사용

### 실시간 동기화
현재 프로젝트는 Firebird와 실시간 동기화를 수행합니다. PythonAnywhere에서는 다음 방법 고려:
1. **로컬 서버 유지**: 로컬에서 Firebird 동기화 스크립트를 계속 실행
2. **주기적 동기화**: PythonAnywhere 스케줄 태스크로 API를 통해 데이터 동기화
3. **읽기 전용**: PythonAnywhere를 읽기 전용으로 운영하고 정기적으로 데이터 업데이트

## 문제 해결

### 500 에러 발생시
1. Web 탭에서 "Error log" 확인
2. Bash 콘솔에서:
   ```bash
   cd ~/tirepass
   cat error.log
   ```

### Static 파일이 로드되지 않을 때
```bash
python manage.py collectstatic --noinput
```
Web 탭에서 Reload 버튼 클릭

### 데이터베이스 연결 오류
- `settings_production.py`의 데이터베이스 설정 확인
- MySQL 서비스가 실행 중인지 확인
- 비밀번호가 올바른지 확인

## 유용한 명령어

### 로그 확인
```bash
# Django 에러 로그
tail -f ~/tirepass/error.log

# PythonAnywhere 서버 로그
# Web 탭에서 "Server log", "Error log" 링크 클릭
```

### 웹 앱 재시작
```bash
# Bash 콘솔에서
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

### 데이터베이스 백업
```bash
mysqldump -u yourusername -h yourusername.mysql.pythonanywhere-services.com -p yourusername$itire_db > backup_$(date +%Y%m%d).sql
```

## 추가 리소스

- PythonAnywhere 공식 문서: https://help.pythonanywhere.com/
- Django 배포 가이드: https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/
- PythonAnywhere 포럼: https://www.pythonanywhere.com/forums/

## 업데이트 방법

코드 변경시:
```bash
cd ~/tirepass
git pull  # Git 사용시
source venv/bin/activate
pip install -r requirements.txt  # 패키지 변경시
python manage.py migrate  # 모델 변경시
python manage.py collectstatic --noinput  # Static 파일 변경시
```

Web 탭에서 "Reload" 버튼 클릭

## 보안 권장사항

1. `SECRET_KEY`를 환경변수로 관리
2. `DEBUG=False` 설정 확인
3. `ALLOWED_HOSTS` 제한
4. 정기적인 데이터베이스 백업
5. `.env` 파일을 Git에 커밋하지 않기 (`.gitignore`에 추가)

## 연락처

문제 발생시:
- PythonAnywhere 포럼에 질문
- Django 공식 문서 참조
- 프로젝트 이슈 트래커 확인

"""
로컬 개발환경 설정 - PythonAnywhere DB 읽기 전용 연결

이 파일을 사용하려면:
python manage.py runserver --settings=itire.settings_local
"""

from .settings import *

# ============================================
# PythonAnywhere 원격 데이터베이스 연결 (읽기 전용)
# ============================================

# PythonAnywhere MySQL 접속 정보
# 주의: PythonAnywhere 무료 계정은 외부 접속이 제한됩니다.
# 유료 계정이거나 화이트리스트에 등록된 IP에서만 접속 가능합니다.

PYTHONANYWHERE_DB_HOST = os.environ.get('PYTHONANYWHERE_DB_HOST', 'tirepass.mysql.pythonanywhere-services.com')
PYTHONANYWHERE_DB_NAME = os.environ.get('PYTHONANYWHERE_DB_NAME', 'tirepass$itire_db')
PYTHONANYWHERE_DB_USER = os.environ.get('PYTHONANYWHERE_DB_USER', 'tirepass')
PYTHONANYWHERE_DB_PASSWORD = os.environ.get('PYTHONANYWHERE_DB_PASSWORD', '')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': PYTHONANYWHERE_DB_NAME,
        'USER': PYTHONANYWHERE_DB_USER,
        'PASSWORD': PYTHONANYWHERE_DB_PASSWORD,
        'HOST': PYTHONANYWHERE_DB_HOST,
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'connect_timeout': 10,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', SESSION TRANSACTION READ ONLY",
        },
        'CONN_MAX_AGE': 0,  # 연결 풀링 비활성화 (읽기 전용)
    }
}

# 읽기 전용 모드 활성화
READ_ONLY_MODE = True

# 디버그 모드
DEBUG = True

# 세션 쿠키 설정
SESSION_COOKIE_NAME = 'sessionid_local'  # 로컬과 프로덕션 세션 분리

# 읽기 전용 미들웨어 추가
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tire_data.middleware.ReadOnlyMiddleware',  # 읽기 전용 요청 차단
    'tire_data.middleware.ReadOnlyAdminMiddleware',  # 읽기 전용 경고
]

print("=" * 70)
print("🔍 로컬 개발환경 (읽기 전용 모드)")
print("=" * 70)
print(f"데이터베이스: {PYTHONANYWHERE_DB_NAME}")
print(f"호스트: {PYTHONANYWHERE_DB_HOST}")
print(f"읽기 전용: {READ_ONLY_MODE}")
print("⚠️  데이터 추가/수정/삭제가 차단됩니다.")
print("=" * 70)

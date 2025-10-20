"""
Django settings for itire project.
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-tirepass-2024-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*,localhost,127.0.0.1').split(',')

# ============================================
# Toss Payments 설정
# ============================================
TOSS_PAYMENTS_CLIENT_KEY = os.environ.get('TOSS_PAYMENTS_CLIENT_KEY', 'test_ck_EP59LybZ8BlBZd2LBbAQV6GYo7pR')
TOSS_PAYMENTS_SECRET_KEY = os.environ.get('TOSS_PAYMENTS_SECRET_KEY', 'test_ck_EP59LybZ8BlBZd2LBbAQV6GYo7pR')
TOSS_PAYMENTS_SECURITY_KEY = os.environ.get('TOSS_PAYMENTS_SECURITY_KEY', '1f1e0fecdf0102c9bd1d27391d29dd1fc4ee3fa5737c560f5e9bb4f37c2200a7')
TOSS_PAYMENTS_API_URL = 'https://api.tosspayments.com/v1'

# ============================================
# ERP 실시간 동기화 API 설정
# ============================================
ERP_SYNC_API_URL = os.environ.get('ERP_SYNC_API_URL', 'http://itire2.iptime.org:8000')
ERP_SYNC_API_KEY = os.environ.get('ERP_SYNC_API_KEY', 'tirepass_erp_sync_key_2024_change_in_production')
ERP_SYNC_TIMEOUT = 5  # 연결 타임아웃 (초)
ERP_SYNC_RETRY_COUNT = 3  # 재시도 횟수
ERP_SYNC_RETRY_DELAY = 2  # 재시도 대기 시간 (초)

# ============================================
# UTF-8 인코딩 강제 설정 (Windows 전용)
# ============================================
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 환경변수로도 UTF-8 설정
os.environ['PYTHONIOENCODING'] = 'utf-8'


# Application definition
INSTALLED_APPS = [
    # 프로젝트 앱 (템플릿 오버라이드를 위해 먼저 등록)
    'tire_data',

    # Django 기본 앱
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # 천단위 콤마 (intcomma) 필터
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'itire.middleware.RestrictAdminAccessMiddleware',  # 관리자 페이지 접근 제한
    'itire.middleware.MobileUserCheckMiddleware',  # 모바일 사용자 체크
]

# ============================================
# 보안 설정 (프로덕션)
# ============================================
SECURE_SSL_REDIRECT = not DEBUG  # 프로덕션에서 HTTPS 강제
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
X_FRAME_OPTIONS = 'DENY'

ROOT_URLCONF = 'itire.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'itire.wsgi.application'


# ============================================
# Database
# ============================================
# PythonAnywhere 환경 자동 감지
IS_PYTHONANYWHERE = 'PYTHONANYWHERE_SITE' in os.environ or '/home/tirepass' in str(BASE_DIR)

if IS_PYTHONANYWHERE:
    # PythonAnywhere 환경: 원격 MySQL 서버 사용
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'tirepass$itire_db',
            'USER': 'tirepass',
            'PASSWORD': os.environ.get('DB_PASSWORD', '#flowgen9569yjm*'),
            'HOST': 'tirepass.mysql.pythonanywhere-services.com',
            'PORT': '3306',
            'OPTIONS': {
                'charset': 'utf8mb4',
                'connect_timeout': 10,  # 연결 타임아웃 10초
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;",
            },
            'CONN_MAX_AGE': 0,  # 매 요청마다 새 연결 (타임아웃 방지)
        }
    }
else:
    # 로컬 개발 환경: localhost MySQL 사용
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ.get('DB_NAME', 'itire_db'),
            'USER': os.environ.get('DB_USER', 'root'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'tirepass'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'connect_timeout': 28800,
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'; SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;",
            },
            'CONN_MAX_AGE': 600,
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================
# 국제화 및 지역화 설정
# ============================================
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 파일 인코딩 설정
FILE_CHARSET = 'utf-8'
DEFAULT_CHARSET = 'utf-8'


# ============================================
# Static files (CSS, JavaScript, Images)
# ============================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================
# Default primary key field type
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================
# Logging 설정 (UTF-8 문제 디버깅용)
# ============================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# ============================================
# Session 설정 (PG사/카드사 가맹 승인을 위한 보안 강화)
# ============================================
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 3600  # 1시간 (금융거래 보안 강화)
SESSION_SAVE_EVERY_REQUEST = True  # 매 요청마다 세션 갱신 (활동 시 자동 연장)
SESSION_COOKIE_SECURE = not DEBUG  # 프로덕션에서 HTTPS only
SESSION_COOKIE_HTTPONLY = True  # JavaScript 접근 차단 (XSS 방지)
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF 공격 방지
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # 브라우저 닫아도 세션 유지 (SESSION_COOKIE_AGE까지)


# ============================================
# CSRF 설정
# ============================================
CSRF_COOKIE_SECURE = not DEBUG  # 프로덕션에서 True
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = os.environ.get('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080,http://127.0.0.1:8080').split(',')


# ============================================
# Admin 설정
# ============================================
ADMIN_SITE_HEADER = 'TirePASS 관리자'
ADMIN_SITE_TITLE = 'TirePASS Admin'
ADMIN_INDEX_TITLE = '타이어패스 관리 시스템'


# ============================================
# 인증 설정
# ============================================

# 커스텀 인증 백엔드 (사업자등록번호 admin 로그인 차단)
AUTHENTICATION_BACKENDS = [
    'tire_data.auth_backends.AdminAuthBackend',
]

# 로그인 필요 시 리다이렉트할 URL (모바일 로그인 페이지로)
LOGIN_URL = '/mobile/login/'

# 로그인 성공 후 리다이렉트할 URL (모바일 홈으로)
LOGIN_REDIRECT_URL = '/mobile/home/'

# 로그아웃 후 리다이렉트할 URL
# admin 로그아웃 → admin 로그인 페이지
# mobile 로그아웃 → mobile 인트로 페이지 (뷰에서 명시적으로 처리)
LOGOUT_REDIRECT_URL = '/admin/login/'
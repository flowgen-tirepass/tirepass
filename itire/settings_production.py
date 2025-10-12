"""
PythonAnywhere용 프로덕션 설정

사용법:
1. PythonAnywhere 환경변수에 다음을 설정:
   DJANGO_SETTINGS_MODULE=itire.settings_production

2. 또는 pythonanywhere_wsgi.py에서:
   os.environ['DJANGO_SETTINGS_MODULE'] = 'itire.settings_production'
"""

from .settings import *

# PythonAnywhere 프로덕션 설정
DEBUG = False

# PythonAnywhere 도메인 설정 (실제 배포시 수정)
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
]

# 데이터베이스 설정 (PythonAnywhere MySQL)
# PythonAnywhere는 무료 플랜에서 MySQL을 제공합니다
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'yourusername$itire_db',  # PythonAnywhere 형식: username$dbname
        'USER': 'yourusername',
        'PASSWORD': 'your_mysql_password',  # PythonAnywhere MySQL 비밀번호
        'HOST': 'yourusername.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 600,
    }
}

# Static 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'mobile', 'static'),
]

# Media 파일 설정
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 보안 설정
SECURE_SSL_REDIRECT = False  # PythonAnywhere는 자동으로 HTTPS 처리
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# 로깅 설정
# Django admin 로그아웃 리다이렉트 (settings.py에서 상속되지만 명시적으로 설정)
LOGOUT_REDIRECT_URL = '/admin/login/'

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
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),
            'formatter': 'verbose',
        },
        'info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'info.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'tire_data': {
            'handlers': ['console', 'info_file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

"""
WSGI config for PythonAnywhere deployment.

This WSGI file is for deploying the Django project on PythonAnywhere.

사용 방법:
1. PythonAnywhere Web 탭에서 WSGI configuration file 편집
2. 'yourusername'을 실제 PythonAnywhere 사용자명으로 변경
3. Save 후 Reload
"""

import os
import sys

# PythonAnywhere 경로 설정
# yourusername을 실제 사용자명으로 변경하세요
path = '/home/yourusername/tirepass'
if path not in sys.path:
    sys.path.insert(0, path)

# Django 프로덕션 설정 사용
os.environ['DJANGO_SETTINGS_MODULE'] = 'itire.settings_production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

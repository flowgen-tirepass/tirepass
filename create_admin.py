"""
Django admin 슈퍼유저 생성 스크립트
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 기존 admin 계정 확인
username = 'admin'
email = 'admin@tirepass.com'
password = 'tirepass2024!'

if User.objects.filter(username=username).exists():
    print(f"'{username}' 계정이 이미 존재합니다.")
    user = User.objects.get(username=username)
    user.set_password(password)
    user.save()
    print(f"'{username}' 계정의 비밀번호를 재설정했습니다.")
else:
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"슈퍼유저 '{username}' 계정을 생성했습니다.")

print(f"\n{'='*50}")
print(f"관리자 로그인 정보:")
print(f"{'='*50}")
print(f"URL: http://127.0.0.1:8000/admin/")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"{'='*50}")

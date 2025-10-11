"""비밀번호 해시 테스트"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from django.contrib.auth.hashers import check_password

# pythonanywhere DB의 해시
pwd_hash = "pbkdf2_sha256$870000$MMpYAX4Bn2EgujNLRafkOe$pGwZeqMv2Kb5eAwSxFqLqaY39goQlShe44TLAOKNimk="

print("=" * 60)
print("비밀번호 테스트")
print("=" * 60)

test_passwords = ["44458", "test1234", "123456"]

for pwd in test_passwords:
    result = check_password(pwd, pwd_hash)
    print(f"{pwd:15s} -> {'✅ 일치' if result else '❌ 불일치'}")

"""
pythonanywhere 비밀번호 해시 테스트
"""
from django.contrib.auth.hashers import make_password, check_password

# pythonanywhere DB에서 가져온 해시
pwd_hash = "pbkdf2_sha256$870000$MMpYAX4Bn2EgujNLRafkOe$pGwZeqMv2Kb5eAwSxFqLqaY39goQlShe44TLAOKNimk="

print("=" * 60)
print("pythonanywhere 비밀번호 해시 테스트")
print("=" * 60)

# 여러 비밀번호 테스트
test_passwords = [
    "44458",      # 초기 비밀번호
    "test1234",   # 변경한 비밀번호
    "123456",     # 이전 테스트
]

for pwd in test_passwords:
    result = check_password(pwd, pwd_hash)
    print(f"{pwd:15s} -> {'✅ 일치' if result else '❌ 불일치'}")

print("\n" + "=" * 60)
print("새 비밀번호 해시 생성 테스트")
print("=" * 60)

# test1234의 해시 생성
new_hash = make_password("test1234")
print(f"test1234 새 해시: {new_hash[:50]}...")
print(f"검증: {check_password('test1234', new_hash)}")

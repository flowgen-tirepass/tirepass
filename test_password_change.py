"""
비밀번호 변경 테스트 스크립트
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers
from django.contrib.auth.hashers import make_password, check_password

print("=" * 50)
print("비밀번호 변경 테스트")
print("=" * 50)

# 테스트할 고객 선택
try:
    customer = Customers.objects.filter(is_registered=True).first()

    if not customer:
        print("❌ 등록된 고객이 없습니다.")
        exit()

    print(f"\n✅ 테스트 고객: {customer.code} - {customer.name}")
    print(f"   사업자번호: {customer.enno}")
    print(f"   초기 비밀번호: {customer.enno[-5:] if customer.enno else 'N/A'}")
    print(f"   must_change_password: {customer.must_change_password}")

    # 현재 비밀번호 확인
    current_password = customer.enno[-5:] if customer.enno else ''
    print(f"\n현재 비밀번호로 로그인 테스트: {current_password}")

    if check_password(current_password, customer.password):
        print("✅ 현재 비밀번호 일치")
    else:
        print("❌ 현재 비밀번호 불일치")
        print(f"   저장된 해시: {customer.password}")

    # 비밀번호 변경 시뮬레이션
    new_password = "test1234"
    print(f"\n새 비밀번호로 변경: {new_password}")

    customer.password = make_password(new_password)
    customer.must_change_password = False
    customer.save()

    print("✅ 비밀번호 변경 저장 완료")

    # 다시 불러와서 확인
    customer.refresh_from_db()
    print(f"   must_change_password: {customer.must_change_password}")

    # 새 비밀번호로 로그인 테스트
    print(f"\n새 비밀번호로 로그인 테스트: {new_password}")
    if check_password(new_password, customer.password):
        print("✅ 새 비밀번호로 로그인 성공")
    else:
        print("❌ 새 비밀번호로 로그인 실패")

    # 이전 비밀번호로 로그인 시도
    print(f"\n이전 비밀번호로 로그인 시도: {current_password}")
    if check_password(current_password, customer.password):
        print("❌ 이전 비밀번호로 로그인 성공 (문제!)")
    else:
        print("✅ 이전 비밀번호로 로그인 실패 (정상)")

    print("\n" + "=" * 50)
    print("테스트 완료")
    print("=" * 50)

except Exception as e:
    print(f"❌ 에러 발생: {str(e)}")
    import traceback
    traceback.print_exc()

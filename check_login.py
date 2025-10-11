"""
로그인 문제 디버깅 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers
from django.contrib.auth.hashers import check_password

print("=" * 60)
print("로그인 문제 디버깅")
print("=" * 60)

# 테스트할 사업자번호 입력
test_enno = input("\n사업자등록번호 10자리 입력 (예: 4101967194): ").strip().replace('-', '')

try:
    # code로 조회 (migrate_erp_customers에서 code=enno로 저장했음)
    customer = Customers.objects.get(code=test_enno)

    print(f"\n✅ 고객 찾음:")
    print(f"   code: {customer.code}")
    print(f"   name: {customer.name}")
    print(f"   enno: {customer.enno}")
    print(f"   is_registered: {customer.is_registered}")
    print(f"   must_change_password: {customer.must_change_password}")
    print(f"   password 해시: {customer.password[:50]}...")

    # 초기 비밀번호 테스트
    initial_password = test_enno[-5:]
    print(f"\n초기 비밀번호 테스트: {initial_password}")

    if customer.password:
        result = check_password(initial_password, customer.password)
        if result:
            print("✅ 초기 비밀번호 일치 - 로그인 가능")
        else:
            print("❌ 초기 비밀번호 불일치 - 로그인 불가")
            print("\n비밀번호가 변경되었을 수 있습니다.")

            # 다른 비밀번호 시도
            test_password = input("다른 비밀번호로 테스트 (Enter=건너뛰기): ").strip()
            if test_password:
                if check_password(test_password, customer.password):
                    print("✅ 테스트 비밀번호 일치")
                else:
                    print("❌ 테스트 비밀번호 불일치")
    else:
        print("❌ 비밀번호가 설정되지 않음")

except Customers.DoesNotExist:
    print(f"\n❌ 고객을 찾을 수 없습니다: {test_enno}")
    print("\n가능한 원인:")
    print("1. 사업자번호가 잘못 입력됨")
    print("2. migrate_erp_customers 스크립트가 실행되지 않음")
    print("3. 해당 고객이 ERP에 없음")

    # 등록된 고객 수 확인
    total = Customers.objects.filter(is_registered=True).count()
    print(f"\n현재 등록된 고객 수: {total}명")

    if total > 0:
        print("\n처음 5명의 고객 코드:")
        for c in Customers.objects.filter(is_registered=True)[:5]:
            print(f"  - {c.code} ({c.name})")

except Exception as e:
    print(f"\n❌ 에러 발생: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

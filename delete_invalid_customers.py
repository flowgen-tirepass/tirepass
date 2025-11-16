"""
잘못된 고객 레코드 삭제

삭제 대상:
1. 고객코드가 10자리 숫자 (사업자등록번호)
2. 고객코드가 Z로 시작하고 000 포함
3. 고객코드가 100000으로 시작
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers

print("=" * 80)
print("잘못된 고객 레코드 삭제")
print("=" * 80)

all_customers = Customers.objects.all()
print(f"\n삭제 전 전체 고객 수: {all_customers.count()}")

# 삭제 대상 찾기
to_delete = []

for customer in all_customers:
    code = customer.code

    # 1. 10자리 숫자 (사업자등록번호)
    if code.isdigit() and len(code) == 10:
        to_delete.append(customer)

    # 2. Z로 시작하고 000 포함
    elif code.startswith('Z') and '000' in code:
        to_delete.append(customer)

    # 3. 100000으로 시작
    elif code.startswith('100000'):
        to_delete.append(customer)

if not to_delete:
    print("\n✅ 삭제할 레코드가 없습니다!")
else:
    print(f"\n삭제 대상: {len(to_delete)}개")
    print("-" * 80)

    for customer in to_delete:
        print(f"삭제: {customer.code} - {customer.name or '이름없음'}")

    # 삭제 실행
    print("\n삭제 중...")
    deleted_codes = [c.code for c in to_delete]

    deleted_count = Customers.objects.filter(code__in=deleted_codes).delete()[0]

    print(f"✅ {deleted_count}개 레코드 삭제 완료")
    print(f"\n삭제 후 전체 고객 수: {Customers.objects.count()}")

print("\n" + "=" * 80)

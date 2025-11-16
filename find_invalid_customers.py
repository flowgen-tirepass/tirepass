"""
잘못된 고객 레코드 찾기

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
import re

print("=" * 80)
print("잘못된 고객 레코드 검색")
print("=" * 80)

all_customers = Customers.objects.all()
print(f"\n전체 고객 수: {all_customers.count()}")

# 삭제 대상 찾기
invalid_customers = []

for customer in all_customers:
    code = customer.code
    reason = None

    # 1. 10자리 숫자 (사업자등록번호)
    if code.isdigit() and len(code) == 10:
        reason = "사업자등록번호 (10자리 숫자)"

    # 2. Z로 시작하고 000 포함
    elif code.startswith('Z') and '000' in code:
        reason = "Z*000*** 패턴"

    # 3. 100000으로 시작
    elif code.startswith('100000'):
        reason = "100000** 패턴"

    if reason:
        invalid_customers.append({
            'customer': customer,
            'reason': reason
        })

print(f"\n삭제 대상 고객 수: {len(invalid_customers)}")
print("=" * 80)

if invalid_customers:
    print("\n삭제할 레코드 목록:")
    print("-" * 80)
    print(f"{'고객코드':<15} {'고객명':<25} {'사업자번호':<15} {'사유':<20}")
    print("-" * 80)

    for item in invalid_customers:
        customer = item['customer']
        reason = item['reason']
        print(f"{customer.code:<15} {(customer.name or ''):<25} {(customer.enno or ''):<15} {reason:<20}")

    print("-" * 80)
    print(f"\n총 {len(invalid_customers)}개 레코드")

    # 올바른 고객 코드 예시 확인
    print("\n" + "=" * 80)
    print("올바른 고객 레코드 예시 (유지할 레코드):")
    print("-" * 80)
    print(f"{'고객코드':<15} {'고객명':<25} {'사업자번호':<15}")
    print("-" * 80)

    valid_customers = Customers.objects.exclude(
        code__in=[item['customer'].code for item in invalid_customers]
    )[:10]

    for customer in valid_customers:
        print(f"{customer.code:<15} {(customer.name or ''):<25} {(customer.enno or ''):<15}")

    print("-" * 80)
    print(f"올바른 고객 수: {Customers.objects.exclude(code__in=[item['customer'].code for item in invalid_customers]).count()}")

else:
    print("\n✅ 삭제할 잘못된 레코드가 없습니다!")

print("\n" + "=" * 80)
print("다음 단계: delete_invalid_customers.py 실행")
print("=" * 80)

"""
중복 고객 찾기 및 삭제
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers

print("=== 사업자번호 4108305068 고객 검색 ===\n")

# 사업자번호로 모든 고객 찾기
customers = Customers.objects.filter(enno__contains='4108305068')

print(f"발견된 고객 수: {customers.count()}\n")

for customer in customers:
    print(f"코드: {customer.code}")
    print(f"이름: '{customer.name}'")
    print(f"대표자: '{customer.rep}'")
    print(f"사업자번호: {customer.enno}")
    print(f"전화1: {customer.tel1}")
    print(f"비밀번호: {'설정됨' if customer.password else '없음'}")
    print(f"ID: {customer.id}")
    print("-" * 60)

print("\n=== '정확한'이 포함된 모든 고객 ===\n")

bad_customers = Customers.objects.filter(name__icontains='정확한')
print(f"발견된 고객 수: {bad_customers.count()}\n")

for customer in bad_customers:
    print(f"코드: {customer.code}")
    print(f"이름: '{customer.name}'")
    print(f"사업자번호: {customer.enno}")
    print(f"비밀번호: {'설정됨' if customer.password else '없음'}")
    print(f"ID: {customer.id}")
    print("-" * 60)

# 잘못된 레코드 삭제 (확인용)
print("\n=== 삭제 대상 ===")
delete_target = Customers.objects.filter(
    code='4108305068',
    name__icontains='정확한'
).first()

if delete_target:
    print(f"삭제할 레코드: 코드={delete_target.code}, 이름='{delete_target.name}'")
    print("\n이 레코드를 삭제하시겠습니까?")
    print("삭제하려면 'delete_bad_customer.py'를 실행하세요.")
else:
    print("삭제할 레코드가 없습니다.")

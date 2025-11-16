"""
사업자번호 410-83-05068 고객 정보 확인
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers

# 사업자번호로 검색 (하이픈 제거)
business_number = '4108305068'

print(f"=== 사업자번호 {business_number} 고객 검색 ===\n")

customers = Customers.objects.filter(enno=business_number)

if not customers.exists():
    print(f"❌ 사업자번호 {business_number}로 고객을 찾을 수 없습니다.")
    print("\n고객 코드로 검색:")
    customers = Customers.objects.filter(code='0-1-0003')

for customer in customers:
    print(f"고객 코드: {customer.code}")
    print(f"고객명(name): '{customer.name}'")
    print(f"대표자(rep): '{customer.rep}'")
    print(f"전화번호1: {customer.tel1}")
    print(f"사업자번호(enno): {customer.enno}")
    print(f"비밀번호 설정 여부: {'있음' if customer.password else '없음'}")
    print("-" * 50)

# "정확한"이 포함된 모든 고객 검색
print("\n=== '정확한'이 포함된 고객명 검색 ===\n")
bad_customers = Customers.objects.filter(name__icontains='정확한')
print(f"발견된 고객 수: {bad_customers.count()}")

for customer in bad_customers:
    print(f"코드: {customer.code}, 이름: '{customer.name}', 사업자번호: {customer.enno}")

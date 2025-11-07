#!/usr/bin/env python
"""
특정 고객의 이름 정보 확인
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers

# 광주전자공업고등학교 정보 확인
customer_code = '0-1-0003'
business_number = '4108305068'  # 하이픈 제거

print("=" * 80)
print("고객 정보 확인")
print("=" * 80)

# 코드로 검색
try:
    customer = Customers.objects.get(code=customer_code)
    print(f"\n✅ 고객 코드로 찾음: {customer_code}")
    print(f"   - name: '{customer.name}'")
    print(f"   - rep: '{customer.rep}'")
    print(f"   - enno: '{customer.enno}'")
    print(f"   - tel1: '{customer.tel1}'")
    print(f"   - tel3: '{customer.tel3}'")
    print(f"   - is_registered: {customer.is_registered}")
    print(f"   - user_id: {customer.user_id}")
except Customers.DoesNotExist:
    print(f"\n❌ 코드로 찾을 수 없음: {customer_code}")

# 사업자번호로 검색
try:
    customer = Customers.objects.get(enno=business_number)
    print(f"\n✅ 사업자번호로 찾음: {business_number}")
    print(f"   - code: '{customer.code}'")
    print(f"   - name: '{customer.name}'")
    print(f"   - rep: '{customer.rep}'")
    print(f"   - tel1: '{customer.tel1}'")
    print(f"   - tel3: '{customer.tel3}'")
    print(f"   - is_registered: {customer.is_registered}")
    print(f"   - user_id: {customer.user_id}")
except Customers.DoesNotExist:
    print(f"\n❌ 사업자번호로 찾을 수 없음: {business_number}")

# 이름에 "정확한"이 포함된 고객 검색
print("\n" + "=" * 80)
print("이름에 '정확한'이 포함된 고객 검색")
print("=" * 80)

customers_with_wrong_name = Customers.objects.filter(name__contains='정확한')
if customers_with_wrong_name.exists():
    print(f"\n⚠️  발견: {customers_with_wrong_name.count()}명")
    for c in customers_with_wrong_name[:10]:
        print(f"   - {c.code} | {c.name} | {c.enno}")
else:
    print("\n✅ 없음: 이름에 '정확한'이 포함된 고객 없음")

# 이름이 비어있거나 이상한 고객 검색
print("\n" + "=" * 80)
print("이름이 비어있거나 이상한 고객 검색")
print("=" * 80)

empty_names = Customers.objects.filter(name='')
if empty_names.exists():
    print(f"\n⚠️  이름이 비어있는 고객: {empty_names.count()}명")
else:
    print("\n✅ 이름이 비어있는 고객 없음")

print("\n" + "=" * 80)

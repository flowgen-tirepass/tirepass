#!/usr/bin/env python
"""
모든 고객의 이름에 '정확한', '입력', 'placeholder' 등이 포함되어 있는지 확인
"""

import os
import django
import sys

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Customers

print("=" * 80)
print("모든 고객의 이름 확인 (의심스러운 패턴 검색)")
print("=" * 80)

# 의심스러운 키워드
suspicious_keywords = ['정확한', '입력', 'placeholder', '예:', '고객명', '상호', '이름']

print("\n1. 의심스러운 키워드가 포함된 고객 검색:")
print("-" * 80)

found_suspicious = False

for keyword in suspicious_keywords:
    customers = Customers.objects.filter(name__icontains=keyword)
    if customers.exists():
        print(f"\n⚠️  '{keyword}' 포함된 고객: {customers.count()}명")
        for c in customers:
            print(f"   - code: {c.code}")
            print(f"     name: '{c.name}'")
            print(f"     enno: {c.enno}")
            print(f"     is_registered: {c.is_registered}")
            print(f"     user_id: {c.user_id}")
            print()
        found_suspicious = True

if not found_suspicious:
    print("✅ 의심스러운 이름 없음")

# 최근 회원가입한 고객 확인 (user_id가 있는 경우)
print("\n" + "=" * 80)
print("2. 최근 회원가입한 고객 (user_id 있는 경우):")
print("-" * 80)

registered_customers = Customers.objects.filter(is_registered=True).order_by('-user_id')[:10]

if registered_customers.exists():
    print(f"\n최근 10명:")
    for c in registered_customers:
        print(f"   - code: {c.code}")
        print(f"     name: '{c.name}'")
        print(f"     enno: {c.enno}")
        print(f"     user_id: {c.user_id}")
        print()
else:
    print("\n⚠️  회원가입한 고객 없음")

# 이름이 비어있거나 None인 경우
print("=" * 80)
print("3. 이름이 비어있거나 None인 고객:")
print("-" * 80)

empty_names = Customers.objects.filter(name__isnull=True) | Customers.objects.filter(name='')
if empty_names.exists():
    print(f"\n⚠️  {empty_names.count()}명 발견")
    for c in empty_names[:10]:
        print(f"   - code: {c.code}, enno: {c.enno}, is_registered: {c.is_registered}")
else:
    print("\n✅ 이름이 비어있는 고객 없음")

# 통계
print("\n" + "=" * 80)
print("4. 통계:")
print("-" * 80)

total = Customers.objects.count()
registered = Customers.objects.filter(is_registered=True).count()
with_user_id = Customers.objects.filter(user_id__isnull=False).count()

print(f"전체 고객: {total}명")
print(f"회원가입한 고객: {registered}명")
print(f"user_id 있는 고객: {with_user_id}명")

print("\n" + "=" * 80)

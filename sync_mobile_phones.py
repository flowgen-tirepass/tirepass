"""
ERP 서버에서 휴대폰 번호 가져와서 Django DB 휴대전화 컬럼 업데이트

광주 ERP 연락처 순서:
1. 전화1 (TEL1)
2. 전화2 (TEL2)
3. 팩스 (FAX)
4. 휴대폰 (TEL3 또는 MOBILE)

Django 모델:
- tel1: 전화1
- tel3: 휴대전화 (여기에 ERP 휴대폰 저장)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient
from tire_data.models import Customers
import re

print("\n" + "=" * 80)
print("ERP 휴대폰 번호 → Django 휴대전화 동기화")
print("=" * 80)

# 1. ERP에서 고객 데이터 샘플 확인
print("\n1️⃣ ERP 고객 데이터 구조 확인")
print("-" * 80)

sample_customers = ERPAPIClient.get_customers_list(offset=0, limit=5)

if sample_customers:
    print(f"샘플 고객 {len(sample_customers)}명 데이터 구조:")
    for i, customer in enumerate(sample_customers[:2], 1):
        print(f"\n[{i}] {customer.get('code')} - {customer.get('name')}")
        print(f"    전체 필드: {list(customer.keys())}")

        # 전화번호 관련 필드 확인
        tel_fields = {k: v for k, v in customer.items() if 'tel' in k.lower() or 'mobile' in k.lower() or 'phone' in k.lower()}
        print(f"    연락처 필드: {tel_fields}")
else:
    print("❌ ERP 연결 실패")
    exit(1)

# 2. 휴대폰 필드명 확인
print("\n2️⃣ 휴대폰 필드명 확인")
print("-" * 80)

# ERP에서 사용하는 휴대폰 필드명 (예상)
possible_mobile_fields = ['tel3', 'mobile', 'phone', 'hp', 'cell']

mobile_field = None
for field in possible_mobile_fields:
    if field in sample_customers[0]:
        mobile_field = field
        print(f"✅ 휴대폰 필드명: '{mobile_field}'")
        break

if not mobile_field:
    print("⚠️  휴대폰 필드를 자동으로 찾지 못했습니다.")
    print("   사용 가능한 필드:", list(sample_customers[0].keys()))
    print("\n   아래에서 수동으로 필드명을 확인하세요:")

    for customer in sample_customers[:3]:
        print(f"\n   {customer.get('code')}:")
        for key, value in customer.items():
            if value and str(value).startswith('010'):
                print(f"      → {key}: {value} ✅ (010으로 시작)")

    mobile_field = input("\n   휴대폰 필드명 입력 (예: tel3): ").strip()

# 3. 전체 고객 데이터 가져오기
print(f"\n3️⃣ ERP 전체 고객 데이터 가져오기 (필드: {mobile_field})")
print("-" * 80)

total_count = ERPAPIClient.get_customers_count()
print(f"ERP 전체 고객 수: {total_count:,}명")

all_customers = ERPAPIClient.get_customers_list(offset=0, limit=total_count)
print(f"가져온 고객 수: {len(all_customers):,}명")

# 4. 휴대폰 번호 유효성 검사 및 통계
print(f"\n4️⃣ 휴대폰 번호 통계")
print("-" * 80)

mobile_stats = {
    'total': 0,
    'valid_010': 0,
    'empty': 0,
    'invalid': 0
}

erp_mobile_data = {}  # {customer_code: mobile_number}

for customer in all_customers:
    code = customer.get('code')
    mobile = customer.get(mobile_field) or ''
    mobile = str(mobile).strip()

    mobile_stats['total'] += 1

    if not mobile:
        mobile_stats['empty'] += 1
    elif mobile.startswith('010'):
        mobile_stats['valid_010'] += 1
        erp_mobile_data[code] = mobile
    else:
        mobile_stats['invalid'] += 1

print(f"전체: {mobile_stats['total']:,}명")
print(f"010으로 시작: {mobile_stats['valid_010']:,}명 ✅")
print(f"빈 값: {mobile_stats['empty']:,}명")
print(f"기타: {mobile_stats['invalid']:,}명")

# 5. Django DB 업데이트
print(f"\n5️⃣ Django DB 업데이트")
print("-" * 80)

updated_count = 0
cleared_count = 0
not_found_count = 0

# 모든 고객의 휴대전화 초기화
print("모든 고객의 휴대전화 필드 초기화...")
Customers.objects.all().update(tel3=None)
print(f"✅ 초기화 완료")

# ERP 데이터로 업데이트
print(f"\n010 휴대폰 번호가 있는 {len(erp_mobile_data):,}명 업데이트 중...")

for code, mobile in erp_mobile_data.items():
    try:
        customer = Customers.objects.get(code=code)
        customer.tel3 = mobile
        customer.save()
        updated_count += 1

        if updated_count % 100 == 0:
            print(f"  진행중... {updated_count}/{len(erp_mobile_data)}")

    except Customers.DoesNotExist:
        not_found_count += 1

print(f"\n✅ 업데이트 완료!")
print(f"   업데이트: {updated_count:,}명")
print(f"   Django DB에 없음: {not_found_count:,}명")

# 6. 결과 확인
print(f"\n6️⃣ 결과 확인 (샘플)")
print("-" * 80)

samples = Customers.objects.filter(tel3__startswith='010')[:10]
print(f"010으로 시작하는 휴대전화가 있는 고객 샘플 (10명):")
for customer in samples:
    print(f"  {customer.code:<12} {customer.name:<30} {customer.tel3}")

print("\n" + "=" * 80)
print("✅ 동기화 완료!")
print("=" * 80)

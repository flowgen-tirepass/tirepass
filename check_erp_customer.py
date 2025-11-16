"""
ERP에서 광주전자공업고등학교 고객 확인
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient

print("=" * 80)
print("ERP 고객 검색: 광주전자공업고등학교")
print("=" * 80)

# 1. 고객 코드로 검색
print("\n1️⃣ 고객 코드 '0-1-0003'으로 검색:")
print("-" * 80)

try:
    customer = ERPAPIClient.get_customer_by_code('0-1-0003')
    if customer:
        print(f"✅ 발견!")
        print(f"   코드: {customer.get('code')}")
        print(f"   이름: {customer.get('name')}")
        print(f"   대표자: {customer.get('rep')}")
        print(f"   전화1: {customer.get('tel1')}")
        print(f"   사업자번호: {customer.get('enno')}")
    else:
        print("❌ 코드 '0-1-0003' 고객이 ERP에 없습니다!")
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 2. 사업자번호로 검색
print("\n2️⃣ 사업자번호 '410-83-05068'로 검색:")
print("-" * 80)

try:
    # 검색어로 조회
    search_terms = ['410-83-05068', '4108305068', '410 83 05068']

    for search in search_terms:
        print(f"\n검색어: '{search}'")
        customers = ERPAPIClient.get_customers_list(search=search)

        if customers:
            print(f"✅ {len(customers)}개 발견:")
            for c in customers[:5]:  # 최대 5개만 표시
                print(f"   - {c.get('code')} | {c.get('name')} | {c.get('enno')}")
        else:
            print("   ❌ 없음")
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 3. 이름으로 검색
print("\n3️⃣ 이름 '광주전자'로 검색:")
print("-" * 80)

try:
    customers = ERPAPIClient.get_customers_list(search='광주전자')

    if customers:
        print(f"✅ {len(customers)}개 발견:")
        for c in customers[:10]:
            print(f"   - {c.get('code'):<12} | {c.get('name'):<30} | {c.get('enno')}")
    else:
        print("❌ '광주전자' 검색 결과 없음")
except Exception as e:
    print(f"❌ 오류: {str(e)}")

# 4. ERP 연결 상태 확인
print("\n4️⃣ ERP 연결 상태:")
print("-" * 80)

try:
    count = ERPAPIClient.get_customers_count()
    print(f"✅ ERP 전체 고객 수: {count:,}개")
except Exception as e:
    print(f"❌ ERP 연결 실패: {str(e)}")

print("\n" + "=" * 80)

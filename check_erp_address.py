"""
ERP API 주소 필드 확인 스크립트
PythonAnywhere 또는 로컬에서 실행
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient

print("\n" + "=" * 80)
print("ERP API 주소 필드 확인")
print("=" * 80)

# 고객 데이터 가져오기
customers = ERPAPIClient.get_customers_list(offset=0, limit=10)

if not customers:
    print("❌ ERP 연결 실패")
    exit(1)

print(f"\n고객 수: {len(customers)}명")

print("\n첫 번째 고객의 전체 필드:")
first_customer = customers[0]
for key, value in first_customer.items():
    print(f"  {key}: {value}")

# 주소 필드 확인
print("\n" + "=" * 80)

if 'address1' in first_customer:
    print("✅ ADDRESS1 필드 있음!")
    print("\n주소 샘플 데이터:")
    print("-" * 80)

    for i, customer in enumerate(customers, 1):
        code = customer.get('code', '')
        name = customer.get('name', '')
        address1 = customer.get('address1', '')
        zip1 = customer.get('zip1', '')
        address2 = customer.get('address2', '')
        zip2 = customer.get('zip2', '')

        status = "✅" if address1 else "❌"

        print(f"  [{i}] {code:12s} {name:30s} {status}")
        if address1:
            print(f"      주소: {address1}")
            if zip1:
                print(f"      우편번호: {zip1}")
        if address2:
            print(f"      주소2: {address2}")
        print()
else:
    print("❌ ADDRESS1 필드 없음!")
    print("\n사용 가능한 필드:")
    for key in first_customer.keys():
        print(f"  - {key}")
    print("\n⚠️  FastAPI 서버 코드 수정 필요!")

print("=" * 80)

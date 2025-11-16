"""
ERP FastAPI 서버에서 TEL4 필드가 반환되는지 확인
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient

print("\n" + "=" * 80)
print("ERP API 필드 확인")
print("=" * 80)

# 샘플 고객 5명 가져오기
customers = ERPAPIClient.get_customers_list(offset=0, limit=10)

if customers:
    print(f"\n고객 수: {len(customers)}명")

    # 첫 번째 고객의 모든 필드 확인
    print(f"\n첫 번째 고객의 전체 필드:")
    first = customers[0]
    for key, value in first.items():
        print(f"  {key}: {value}")

    # TEL4 필드 확인
    print(f"\n" + "=" * 80)
    if 'tel4' in first:
        print("✅ TEL4 필드 있음!")

        print(f"\nTEL4 샘플 데이터:")
        for i, customer in enumerate(customers, 1):
            code = customer.get('code')
            name = customer.get('name')
            tel4 = customer.get('tel4', '')

            if tel4 and tel4.startswith('010'):
                print(f"  [{i}] {code:<12} {name:<30} {tel4} ✅")
            else:
                print(f"  [{i}] {code:<12} {name:<30} {tel4 or '(빈값)'}")
    else:
        print("❌ TEL4 필드 없음!")
        print("\n사용 가능한 필드:")
        for key in first.keys():
            print(f"  - {key}")

        print("\n" + "=" * 80)
        print("⚠️  FastAPI 서버 코드 수정 필요!")
        print("=" * 80)
        print("\n화성 PC FastAPI 서버에서 TEL4 필드를 반환하도록 수정해야 합니다.")
        print("\nFirebird 쿼리에 TEL4 컬럼 추가:")
        print("  SELECT CODE, NAME, REP, TEL1, TEL2, TEL3, TEL4, ENNO ...")
        print("                                        ^^^^")
        print("=" * 80)
else:
    print("❌ ERP 연결 실패")

print("\n")

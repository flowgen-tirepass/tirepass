"""
ERP 주소 데이터를 Django ShippingAddress로 동기화
- ERP에 등록된 모든 고객의 주소를 기본 배송지로 등록
- 이미 배송지가 있는 고객은 스킵

실행: python sync_erp_addresses.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.erp_api_client import ERPAPIClient
from tire_data.models_shopping import ShippingAddress
from tire_data.models import Customers

print("\n" + "=" * 80)
print("ERP 주소 → Django 배송지 동기화")
print("=" * 80)

# 1. ERP에서 전체 고객 데이터 가져오기
print("\n1️⃣ ERP 전체 고객 데이터 가져오기")
print("-" * 80)

total_count = ERPAPIClient.get_customers_count()
print(f"ERP 전체 고객 수: {total_count:,}명")

all_customers = ERPAPIClient.get_customers_list(offset=0, limit=total_count)
print(f"가져온 고객 수: {len(all_customers):,}명")

# 2. 주소 데이터 통계
print("\n2️⃣ 주소 데이터 통계")
print("-" * 80)

stats = {
    'total': 0,
    'has_address1': 0,
    'no_address': 0,
    'has_enno': 0,
    'no_enno': 0,
}

address_customers = []

for customer in all_customers:
    stats['total'] += 1

    address1 = customer.get('address1', '').strip() if customer.get('address1') else ''
    enno = customer.get('enno', '').strip() if customer.get('enno') else ''

    if address1:
        stats['has_address1'] += 1
    else:
        stats['no_address'] += 1

    if enno:
        stats['has_enno'] += 1
    else:
        stats['no_enno'] += 1

    # 주소와 사업자번호가 모두 있는 고객만 처리
    if address1 and enno:
        address_customers.append(customer)

print(f"전체: {stats['total']:,}명")
print(f"주소 있음 (ADDRESS1): {stats['has_address1']:,}명")
print(f"주소 없음: {stats['no_address']:,}명")
print(f"사업자번호 있음: {stats['has_enno']:,}명")
print(f"사업자번호 없음: {stats['no_enno']:,}명")
print(f"\n✅ 동기화 대상: {len(address_customers):,}명 (주소 + 사업자번호 모두 있음)")

# 3. Django DB와 매칭 확인
print("\n3️⃣ Django DB 고객 매칭 확인")
print("-" * 80)

matched_customers = []
unmatched_customers = []

for customer in address_customers:
    enno = customer.get('enno', '').strip()

    # Django DB에 해당 고객이 있는지 확인
    django_customer = Customers.objects.filter(enno=enno).first()

    if django_customer:
        customer['django_customer'] = django_customer
        matched_customers.append(customer)
    else:
        unmatched_customers.append(customer)

print(f"Django DB에서 찾음: {len(matched_customers):,}명")
print(f"Django DB에 없음: {len(unmatched_customers):,}명 (스킵 예정)")

# 4. 기존 배송지 확인
print("\n4️⃣ 기존 배송지 확인")
print("-" * 80)

customers_with_shipping = []
customers_without_shipping = []

for customer in matched_customers:
    enno = customer.get('enno', '').strip()

    # 이미 배송지가 있는지 확인
    existing_shipping = ShippingAddress.objects.filter(customer_code=enno).exists()

    if existing_shipping:
        customers_with_shipping.append(customer)
    else:
        customers_without_shipping.append(customer)

print(f"배송지 이미 있음: {len(customers_with_shipping):,}명 (스킵)")
print(f"배송지 없음: {len(customers_without_shipping):,}명 (새로 등록)")

# 5. 배송지 등록
print("\n5️⃣ 배송지 등록")
print("-" * 80)

if not customers_without_shipping:
    print("등록할 배송지가 없습니다.")
else:
    print(f"{len(customers_without_shipping):,}명의 배송지 등록 중...\n")

    created_count = 0
    error_count = 0

    for i, customer in enumerate(customers_without_shipping, 1):
        try:
            code = customer.get('code', '').strip()
            name = customer.get('name', '').strip()
            enno = customer.get('enno', '').strip()
            tel1 = customer.get('tel1', '').strip()
            tel4 = customer.get('tel4', '').strip()
            address1 = customer.get('address1', '').strip()
            zip1 = customer.get('zip1', '').strip()

            # 전화번호 우선순위: 휴대폰(tel4) > 일반전화(tel1)
            phone = tel4 if tel4 else tel1 if tel1 else ''

            # 배송지 생성
            ShippingAddress.objects.create(
                customer_code=enno,  # 사업자번호
                recipient_name=name,  # 상호명
                phone_number=phone,
                postal_code=zip1 if zip1 else '',
                address=address1,
                address_detail='',  # ADDRESS2는 일단 사용 안 함
                is_default=True  # 기본 배송지로 설정
            )

            created_count += 1

            if i % 100 == 0:
                print(f"  진행중... {i}/{len(customers_without_shipping)}")

        except Exception as e:
            error_count += 1
            print(f"  [에러] {code} - {name}: {e}")

    print(f"\n✅ 배송지 등록 완료!")
    print(f"   성공: {created_count:,}명")
    if error_count > 0:
        print(f"   실패: {error_count:,}명")

# 6. 결과 확인 (샘플)
print("\n6️⃣ 결과 확인 (샘플)")
print("-" * 80)

sample_shippings = ShippingAddress.objects.filter(
    is_default=True
).order_by('-created_at')[:10]

if sample_shippings:
    print(f"최근 등록된 배송지 {len(sample_shippings)}개:\n")
    for shipping in sample_shippings:
        print(f"  {shipping.customer_code:15s} {shipping.recipient_name:30s}")
        print(f"    주소: {shipping.address}")
        if shipping.postal_code:
            print(f"    우편번호: {shipping.postal_code}")
        print(f"    전화: {shipping.phone_number}")
        print()
else:
    print("등록된 배송지가 없습니다.")

print("=" * 80)
print("✅ 동기화 완료!")
print("=" * 80)

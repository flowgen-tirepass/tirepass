"""
고객 할인율 추가 스크립트: 4618603360 - 피렐리 브랜드 4% 할인

Django ORM을 사용하여 안전하게 고객 할인율을 추가합니다.
"""
import os
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import CustomerDiscount, Customers

def add_customer_discount():
    """고객 할인율 추가"""

    customer_code = '4618603360'
    brand = '피렐리'
    discount_rate = 4.00

    print("=" * 60)
    print("고객 할인율 추가 스크립트")
    print("=" * 60)
    print()

    # 1. 고객 정보 확인
    try:
        customer = Customers.objects.get(code=customer_code)
        print(f"✓ 고객 정보 확인:")
        print(f"  - 코드: {customer.code}")
        print(f"  - 상호: {customer.name}")
        print(f"  - 사업자번호: {customer.enno}")
        print()
    except Customers.DoesNotExist:
        print(f"✗ 오류: 고객 코드 {customer_code}를 찾을 수 없습니다.")
        return

    # 2. 기존 할인율 확인
    existing_discounts = CustomerDiscount.objects.filter(
        customer_code=customer_code,
        brand=brand
    )

    if existing_discounts.exists():
        print(f"⚠ 기존 할인율이 존재합니다:")
        for discount in existing_discounts:
            print(f"  - ID: {discount.id}")
            print(f"    브랜드: {discount.brand}")
            print(f"    할인율: {discount.discount_rate}%")
            print(f"    우선순위: {discount.priority}")
            print(f"    활성화: {discount.is_active}")
        print()

        # 기존 데이터 삭제
        deleted_count = existing_discounts.delete()[0]
        print(f"✓ 기존 {deleted_count}개 할인율 삭제 완료")
        print()
    else:
        print(f"✓ 기존 할인율 없음 (새로 추가)")
        print()

    # 3. 새로운 할인율 추가
    new_discount = CustomerDiscount.objects.create(
        customer_code=customer_code,
        brand=brand,
        group=None,  # 브랜드 전체 할인
        discount_rate=discount_rate,
        priority=1,
        is_active=True
    )

    print(f"✓ 고객 할인율 추가 완료!")
    print(f"  - ID: {new_discount.id}")
    print(f"  - 고객: {customer_code} ({customer.name})")
    print(f"  - 브랜드: {brand}")
    print(f"  - 할인율: {discount_rate}%")
    print(f"  - 우선순위: {new_discount.priority}")
    print(f"  - 활성화: {new_discount.is_active}")
    print()

    # 4. 전체 고객 할인율 목록 확인
    all_discounts = CustomerDiscount.objects.filter(
        customer_code=customer_code
    ).order_by('brand')

    print(f"현재 고객의 모든 브랜드 할인율 ({all_discounts.count()}개):")
    print("-" * 60)
    for discount in all_discounts:
        print(f"  [{discount.brand}] {discount.discount_rate}% (우선순위: {discount.priority}, 활성: {discount.is_active})")
    print()

    # 5. 테스트: P-PZERO-25 할인율 계산
    from tire_data.utils import calculate_discount_price

    print("=" * 60)
    print("테스트: P-PZERO-25 할인율 계산")
    print("=" * 60)

    test_product_code = 'P-PZERO-25'
    test_year = 2023

    price_info = calculate_discount_price(
        product_code=test_product_code,
        customer_code=customer_code,
        selected_year=test_year,
        quantity=1
    )

    print(f"상품: {price_info['product_name']}")
    print(f"브랜드: {price_info['brand']}")
    print(f"공장도가: {price_info['unit_price']:,}원")
    print()
    print(f"할인율 상세:")
    print(f"  - 기본 할인율: {price_info['basic_discount_rate']}%")
    print(f"  - 고객 할인율: {price_info['customer_discount_rate']}%  ← 새로 추가!")
    print(f"  - 추가 할인율: {price_info['additional_discount_rate']}%")
    print(f"  - DOT 할인율: {price_info['dot_discount_rate']}%")
    print(f"  - 총 할인율: {price_info['total_discount_rate']}%")
    print()
    print(f"최종 가격: {price_info['discounted_price']:,}원")
    print()

    # 예상 결과 확인
    expected_customer_discount = 4.0
    if float(price_info['customer_discount_rate']) == expected_customer_discount:
        print("✓ 고객 할인율 적용 성공!")
    else:
        print(f"⚠ 경고: 고객 할인율이 {expected_customer_discount}%가 아닙니다.")
        print(f"  실제 적용된 할인율: {price_info['customer_discount_rate']}%")

    print()
    print("=" * 60)
    print("완료!")
    print("=" * 60)

if __name__ == '__main__':
    add_customer_discount()

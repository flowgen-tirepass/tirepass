"""
모든 브랜드에 대해 고객 할인율 일괄 추가

실행 방법:
pythonanywhere에서:
cd ~/tirepass
python add_all_brand_discounts.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import CustomerDiscount

def add_all_brand_discounts():
    """모든 브랜드에 대해 4618603360 고객의 4% 할인율 추가"""

    customer_code = '4618603360'

    # 추가할 브랜드 목록 (한글명)
    brands = [
        '금호',
        '미쉐린',
        '넥센',
        '한국',
        '피렐리',  # 이미 있지만 확인용
        '콘티넨탈',
        '브리지스톤',
        '굳이어',
        '하이로',
        '던롭',
        'BFG',
        '안나이트',
        '맥시스',
        '하이플라이',
        '파이어스톤',
        '요코하마'
    ]

    added_count = 0
    skipped_count = 0

    for brand in brands:
        # 이미 존재하는지 확인
        existing = CustomerDiscount.objects.filter(
            customer_code=customer_code,
            brand=brand,
            group_id__isnull=True  # 브랜드 전체 할인만
        ).first()

        if existing:
            print(f"✓ [{brand}] 이미 설정됨 - {existing.discount_rate}%")
            skipped_count += 1
        else:
            # 새로 추가
            new_discount = CustomerDiscount.objects.create(
                customer_code=customer_code,
                brand=brand,
                group_id=None,  # 브랜드 전체
                discount_rate=4.00,
                priority=1,
                is_active=True
            )
            print(f"✓ [{brand}] 추가 완료 - 4%")
            added_count += 1

    print(f"\n===== 완료 =====")
    print(f"추가: {added_count}개 브랜드")
    print(f"건너뜀: {skipped_count}개 브랜드 (이미 설정됨)")
    print(f"총: {len(brands)}개 브랜드")

    # 최종 확인
    print(f"\n===== 최종 확인 =====")
    all_discounts = CustomerDiscount.objects.filter(
        customer_code=customer_code
    ).order_by('brand')

    for discount in all_discounts:
        print(f"  [{discount.brand}] {discount.discount_rate}%")

if __name__ == '__main__':
    add_all_brand_discounts()

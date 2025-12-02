#!/usr/bin/env python
"""
CustomerProductDiscount 데이터 확인 및 상품 코드 매칭 검증 스크립트
PythonAnywhere에서 실행하여 상품 코드 불일치 문제를 파악합니다.
"""
import os
import sys

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')

import django
django.setup()

from tire_data.models import CustomerProductDiscount, Goods

def check_product_discounts():
    """CustomerProductDiscount 데이터 확인"""
    print("=" * 80)
    print("CustomerProductDiscount 데이터 확인")
    print("=" * 80)

    discounts = CustomerProductDiscount.objects.filter(is_active=True)

    print(f"\n활성화된 고객별 상품 할인: {discounts.count()}개\n")

    mismatch_count = 0

    for d in discounts:
        print("-" * 80)
        print(f"고객코드: {d.customer_code}")
        print(f"등록된 상품코드: {d.product_code}")
        print(f"등록된 브랜드: {d.brand}")
        print(f"추가 할인율: {d.additional_discount_rate}%")

        # 상품 코드로 Goods 조회
        try:
            product = Goods.objects.get(code=d.product_code)
            print(f"✅ 상품 매칭 성공: {product.name}")
        except Goods.DoesNotExist:
            print(f"❌ 상품 코드 불일치! '{d.product_code}'에 해당하는 상품 없음")
            mismatch_count += 1

            # 비슷한 상품 검색 (브랜드와 상품명 일부로)
            if d.brand:
                similar = Goods.objects.filter(bun1=d.brand)[:5]
                if similar.exists():
                    print(f"   → 같은 브랜드({d.brand})의 상품 예시:")
                    for s in similar:
                        print(f"      - {s.code}: {s.name}")

    print("\n" + "=" * 80)
    print(f"총 {discounts.count()}개 중 {mismatch_count}개 상품 코드 불일치")
    print("=" * 80)

    return mismatch_count

def find_product_by_name(name_keyword):
    """상품명으로 상품 검색"""
    print(f"\n'{name_keyword}' 포함 상품 검색:")
    products = Goods.objects.filter(name__icontains=name_keyword)[:10]
    for p in products:
        print(f"  - {p.code}: {p.name} (브랜드: {p.bun1})")

if __name__ == "__main__":
    check_product_discounts()

    # 특정 상품 검색
    print("\n" + "=" * 80)
    print("PRIMACY ALL SEASON 상품 검색")
    print("=" * 80)
    find_product_by_name("PRIMACY ALL SEASON")
    find_product_by_name("235/55R19")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
고객 할인 시스템 테스트 스크립트
"""
import os
import sys
import django

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from tire_data.models import (
    Goods, Customers, BrandGroup, BrandGroupPattern,
    CustomerDiscount, DiscountHistory
)
from decimal import Decimal

def test_discount_system():
    """할인 시스템 테스트"""

    print("="*60)
    print("고객 할인 시스템 테스트")
    print("="*60)

    # 1. 브랜드 그룹 확인
    print("\n1. 브랜드 그룹 확인")
    print("-"*40)

    brand_groups = BrandGroup.objects.filter(is_active=True)[:10]
    print(f"활성 브랜드 그룹 수: {brand_groups.count()}")

    for bg in brand_groups[:5]:  # 처음 5개만 출력
        print(f"   - {bg.brand}: {bg.group_name} (순서: {bg.group_order})")

    # 2. TEST001 고객 할인 확인
    print("\n2. TEST001 고객 할인 설정 확인")
    print("-"*40)

    customer_discounts = CustomerDiscount.objects.filter(
        customer_code='TEST001',
        is_active=True
    )

    print(f"TEST001 고객 할인 설정 수: {customer_discounts.count()}")

    for cd in customer_discounts:
        group_name = cd.group.group_name if cd.group else '브랜드 전체'
        print(f"   - {cd.brand} / {group_name}: {cd.discount_rate}%")

    # 3. 실제 가격 계산 테스트
    print("\n3. 실제 가격 계산 테스트")
    print("-"*40)

    # MICHELIN 타이어 중 하나 선택
    sample_goods = Goods.objects.filter(brand='MICHELIN').first()

    if sample_goods:
        print(f"\n테스트 상품: {sample_goods.code} - {sample_goods.name}")
        print(f"브랜드: {sample_goods.brand}")
        print(f"원가: {sample_goods.fixp:,}원")
        print(f"기본 할인율: {sample_goods.discount_rate}%")

        # 기본 할인 적용 가격
        if sample_goods.discount_rate:
            basic_discounted = sample_goods.fixp * (1 - float(sample_goods.discount_rate) / 100)
            print(f"기본 할인 적용가: {int(basic_discounted):,}원")

        # TEST001 고객 할인 확인
        customer_discount = CustomerDiscount.objects.filter(
            customer_code='TEST001',
            brand='MICHELIN',
            is_active=True
        ).first()

        if customer_discount:
            print(f"\n고객 할인율: {customer_discount.discount_rate}%")
            customer_discounted = sample_goods.fixp * (1 - float(customer_discount.discount_rate) / 100)
            print(f"고객 할인 적용가: {int(customer_discounted):,}원")

            # 최종 가격 (더 높은 할인율 적용)
            max_discount = max(
                float(sample_goods.discount_rate) if sample_goods.discount_rate else 0,
                float(customer_discount.discount_rate)
            )
            final_price = sample_goods.fixp * (1 - max_discount / 100)
            print(f"\n최종 가격 (최대 할인 적용): {int(final_price):,}원")
            print(f"절약 금액: {int(sample_goods.fixp - final_price):,}원")
    else:
        print("MICHELIN 브랜드 상품을 찾을 수 없습니다.")

    # 4. 데이터베이스 테이블 상태
    print("\n4. 데이터베이스 테이블 상태")
    print("-"*40)

    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TABLE_NAME, TABLE_ROWS
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME IN ('brand_groups', 'brand_group_patterns',
                              'customer_discounts', 'discount_history')
        """)

        for table_name, row_count in cursor.fetchall():
            print(f"   - {table_name}: {row_count} rows")

    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)

def calculate_final_price(goods_code, customer_code):
    """특정 상품과 고객의 최종 가격 계산"""

    try:
        goods = Goods.objects.get(code=goods_code)

        # 기본 할인
        basic_discount = float(goods.discount_rate) if goods.discount_rate else 0

        # 고객 할인 조회
        customer_discount_obj = CustomerDiscount.objects.filter(
            customer_code=customer_code,
            brand=goods.brand,
            is_active=True
        ).order_by('-priority', '-discount_rate').first()

        customer_discount = 0
        if customer_discount_obj:
            customer_discount = float(customer_discount_obj.discount_rate)

        # 최종 할인율 (더 높은 것 적용)
        final_discount = max(basic_discount, customer_discount)

        # 최종 가격
        final_price = goods.fixp * (1 - final_discount / 100)

        return {
            'original_price': goods.fixp,
            'basic_discount': basic_discount,
            'customer_discount': customer_discount,
            'final_discount': final_discount,
            'final_price': int(final_price)
        }

    except Goods.DoesNotExist:
        return None

if __name__ == '__main__':
    test_discount_system()

    # 추가 테스트
    print("\n\n추가 테스트: 특정 상품 가격 계산")
    print("-"*40)

    # 상품 코드와 고객 코드로 가격 계산
    test_product = input("\n상품 코드 입력 (Enter 시 스킵): ").strip()
    if test_product:
        result = calculate_final_price(test_product, 'TEST001')
        if result:
            print(f"\n상품 코드: {test_product}")
            print(f"원가: {result['original_price']:,}원")
            print(f"기본 할인: {result['basic_discount']}%")
            print(f"고객 할인: {result['customer_discount']}%")
            print(f"최종 할인: {result['final_discount']}%")
            print(f"최종 가격: {result['final_price']:,}원")
        else:
            print("상품을 찾을 수 없습니다.")
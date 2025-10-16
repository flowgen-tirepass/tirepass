#!/usr/bin/env python3
"""
샘플 ERP 전화주문 생성 스크립트

오늘 날짜로 5개의 샘플 주문을 생성합니다.
- 주문 출처: ERP 전화주문 (erp_phone)
- 수정 가능한 샘플 데이터
- 실제 ERP 연동 테스트용
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.utils import timezone
from tire_data.models_shopping import Order, OrderItem
from tire_data.models import Goods


# 샘플 주문 데이터
SAMPLE_ORDERS = [
    {
        'order_number': 'ERP-20251016-001',
        'erp_order_number': '20251016-001',
        'customer_code': 'C001',
        'customer_name': '김철수 타이어',
        'items': [
            {
                'product_code': 'P-021',
                'quantity': 4,
            },
        ],
        'shipping_address': '광주광역시 북구 첨단과기로 123',
        'shipping_memo': '오후 2시 이후 배송 부탁드립니다.',
    },
    {
        'order_number': 'ERP-20251016-002',
        'erp_order_number': '20251016-002',
        'customer_code': 'C002',
        'customer_name': '이영희 자동차',
        'items': [
            {
                'product_code': 'N-택시-05',
                'quantity': 8,
            },
            {
                'product_code': 'N-택시-07',
                'quantity': 4,
            },
        ],
        'shipping_address': '광주광역시 동구 금남로 456',
        'shipping_memo': '택시 회사 - 대량 주문',
    },
    {
        'order_number': 'ERP-20251016-003',
        'erp_order_number': '20251016-003',
        'customer_code': 'C003',
        'customer_name': '박민수 카센터',
        'items': [
            {
                'product_code': 'P-030',
                'quantity': 2,
            },
        ],
        'shipping_address': '광주광역시 서구 상무대로 789',
        'shipping_memo': '카센터 영업시간 내 배송',
    },
    {
        'order_number': 'ERP-20251016-004',
        'erp_order_number': '20251016-004',
        'customer_code': 'C004',
        'customer_name': '최영수 정비소',
        'items': [
            {
                'product_code': 'P-CP7-11',
                'quantity': 4,
            },
        ],
        'shipping_address': '광주광역시 남구 백서로 321',
        'shipping_memo': '정비소 후문으로 배송',
    },
    {
        'order_number': 'ERP-20251016-005',
        'erp_order_number': '20251016-005',
        'customer_code': 'C005',
        'customer_name': '정미경 자동차정비',
        'items': [
            {
                'product_code': 'P-021',
                'quantity': 2,
            },
            {
                'product_code': 'P-030',
                'quantity': 2,
            },
        ],
        'shipping_address': '광주광역시 광산구 월계로 654',
        'shipping_memo': '급한 주문 - 빠른 배송 부탁',
    },
]


def get_product_info(product_code):
    """상품 정보 조회"""
    try:
        goods = Goods.objects.get(code=product_code)
        return {
            'name': goods.name,
            'brand': goods.bun1 or '',
            'price': goods.fixp or 0,
        }
    except Goods.DoesNotExist:
        print(f"[경고] 상품을 찾을 수 없음: {product_code}")
        return {
            'name': f'상품-{product_code}',
            'brand': '',
            'price': 100000,
        }


def create_sample_order(order_data):
    """샘플 주문 생성"""

    # 주문 중복 확인
    if Order.objects.filter(erp_order_number=order_data['erp_order_number']).exists():
        print(f"[스킵] 이미 존재하는 주문: {order_data['order_number']}")
        return None

    # 주문 상품 정보 및 금액 계산
    total_amount = 0
    items_info = []

    for item_data in order_data['items']:
        product_code = item_data['product_code']
        quantity = item_data['quantity']

        # 상품 정보 조회
        product_info = get_product_info(product_code)

        unit_price = product_info['price']
        discount_rate = Decimal('5.00')  # 기본 5% 할인
        discounted_price = int(unit_price * (1 - discount_rate / 100))
        final_price = discounted_price * quantity

        items_info.append({
            'product_code': product_code,
            'product_name': product_info['name'],
            'brand': product_info['brand'],
            'quantity': quantity,
            'unit_price': unit_price,
            'discount_rate': discount_rate,
            'discounted_price': discounted_price,
            'final_price': final_price,
        })

        total_amount += final_price

    # 주문 생성
    order = Order.objects.create(
        order_number=order_data['order_number'],
        erp_order_number=order_data['erp_order_number'],
        customer_code=order_data['customer_code'],
        customer_name=order_data['customer_name'],
        total_amount=total_amount,
        total_discount=0,
        final_amount=total_amount,
        order_status='confirmed',  # 전화주문은 확인됨
        payment_status='paid',  # 결제 완료
        payment_method='transfer',  # 계좌이체
        shipping_address=order_data.get('shipping_address', ''),
        shipping_memo=order_data.get('shipping_memo', ''),
        order_source='erp_phone',  # ERP 전화주문
        order_date=timezone.now(),
        confirmed_date=timezone.now(),
    )

    # 주문 상세 생성
    for item_info in items_info:
        OrderItem.objects.create(
            order=order,
            product_code=item_info['product_code'],
            product_name=item_info['product_name'],
            brand=item_info['brand'],
            quantity=item_info['quantity'],
            unit_price=item_info['unit_price'],
            basic_discount_rate=item_info['discount_rate'],
            total_discount_rate=item_info['discount_rate'],
            discounted_price=item_info['discounted_price'],
            final_price=item_info['final_price'],
        )

    print(f"[생성] {order.order_number} | {order.customer_name} | {total_amount:,}원 | {len(items_info)}개 상품")
    return order


def main():
    print("=" * 70)
    print("  ERP 전화주문 샘플 데이터 생성")
    print("  날짜: 오늘 ({})".format(timezone.now().strftime('%Y-%m-%d')))
    print("=" * 70)
    print()

    print(f"생성할 샘플 주문: {len(SAMPLE_ORDERS)}개")
    print()

    created_count = 0
    for order_data in SAMPLE_ORDERS:
        order = create_sample_order(order_data)
        if order:
            created_count += 1

    print()
    print("=" * 70)
    print(f"[완료] {created_count}개 샘플 주문 생성 완료")
    print("=" * 70)
    print()
    print("확인: https://tirepass.pythonanywhere.com/admin/tire_data/order/")
    print()
    print("[참고]")
    print("- 모든 주문은 수정 가능한 샘플 데이터입니다")
    print("- 주문 출처: ERP 전화주문 (erp_phone)")
    print("- 주문 상태: 주문확인 (confirmed)")
    print("- 결제 상태: 결제완료 (paid)")
    print()


if __name__ == '__main__':
    main()

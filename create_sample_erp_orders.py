#!/usr/bin/env python
"""
ERP 전화주문 샘플 데이터 생성 스크립트
"""
import os
import django
import sys
from datetime import datetime, timedelta

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models_shopping import Order, OrderItem, Payment
from tire_data.models import Customers

def create_sample_orders():
    """샘플 ERP 전화주문 3건 생성"""

    # 기존 고객 코드 확인
    customers = Customers.objects.all()[:3]
    if not customers:
        print("[오류] 고객 데이터가 없습니다. customers_simple 테이블에 고객을 먼저 추가하세요.")
        return

    print(f"[정보] {len(customers)}명의 고객 데이터를 찾았습니다.")

    # 샘플 주문 데이터
    sample_orders = [
        {
            'order_number': 'ERP-2025-001',
            'customer_code': customers[0].code if len(customers) > 0 else 'C001',
            'customer_name': customers[0].name if len(customers) > 0 else '테스트고객1',
            'order_status': 'confirmed',
            'payment_status': 'paid',
            'payment_method': 'transfer',
            'shipping_address': '서울시 강남구 테헤란로 123',
            'items': [
                {
                    'product_code': 'K-ENZA-01',
                    'product_name': '금호 엔자라 235/55R19',
                    'brand': '금호',
                    'quantity': 4,
                    'unit_price': 150000,
                    'discounted_price': 145000,
                },
                {
                    'product_code': 'H-VENT-02',
                    'product_name': '한국 벤투스 S1 225/45R18',
                    'brand': '한국',
                    'quantity': 2,
                    'unit_price': 130000,
                    'discounted_price': 125000,
                },
            ]
        },
        {
            'order_number': 'ERP-2025-002',
            'customer_code': customers[1].code if len(customers) > 1 else 'C002',
            'customer_name': customers[1].name if len(customers) > 1 else '테스트고객2',
            'order_status': 'shipped',
            'payment_status': 'paid',
            'payment_method': 'card',
            'shipping_address': '경기도 성남시 분당구 판교역로 235',
            'items': [
                {
                    'product_code': 'P-SCOR-18',
                    'product_name': '피렐리 스콜피온 255/45R20',
                    'brand': '피렐리',
                    'quantity': 4,
                    'unit_price': 280000,
                    'discounted_price': 270000,
                },
            ]
        },
        {
            'order_number': 'ERP-2025-003',
            'customer_code': customers[2].code if len(customers) > 2 else 'C003',
            'customer_name': customers[2].name if len(customers) > 2 else '테스트고객3',
            'order_status': 'pending',
            'payment_status': 'unpaid',
            'payment_method': 'cash',
            'shipping_address': '부산시 해운대구 센텀중앙로 48',
            'items': [
                {
                    'product_code': 'M-PRIM-04',
                    'product_name': '미쉐린 프라이머시 4 205/55R16',
                    'brand': '미쉐린',
                    'quantity': 4,
                    'unit_price': 160000,
                    'discounted_price': 155000,
                },
                {
                    'product_code': 'N-NFER-05',
                    'product_name': '넥센 엔페라 215/60R17',
                    'brand': '넥센',
                    'quantity': 4,
                    'unit_price': 120000,
                    'discounted_price': 115000,
                },
            ]
        },
    ]

    created_count = 0

    for order_data in sample_orders:
        # 중복 체크
        if Order.objects.filter(order_number=order_data['order_number']).exists():
            print(f"[건너뜀] {order_data['order_number']} - 이미 존재합니다.")
            continue

        # 주문 생성
        items_data = order_data.pop('items')

        # 금액 계산
        total_amount = sum(item['unit_price'] * item['quantity'] for item in items_data)
        total_discount = sum((item['unit_price'] - item['discounted_price']) * item['quantity'] for item in items_data)
        final_amount = total_amount - total_discount

        order = Order.objects.create(
            **order_data,
            order_source='erp_phone',
            total_amount=total_amount,
            total_discount=total_discount,
            final_amount=final_amount,
        )

        # 주문 상세 생성
        for item_data in items_data:
            unit_price = item_data['unit_price']
            discounted_price = item_data['discounted_price']
            quantity = item_data['quantity']
            final_price = discounted_price * quantity

            OrderItem.objects.create(
                order=order,
                product_code=item_data['product_code'],
                product_name=item_data['product_name'],
                brand=item_data['brand'],
                quantity=quantity,
                unit_price=unit_price,
                discounted_price=discounted_price,
                final_price=final_price,
            )

        # 결제 정보 생성 (결제완료 주문만)
        if order.payment_status == 'paid':
            Payment.objects.create(
                order=order,
                payment_method=order.payment_method,
                payment_amount=final_amount,
                payment_status='completed',
                payment_date=datetime.now(),
            )

        created_count += 1
        print(f"[생성] {order.order_number} - {order.customer_name} - {final_amount:,}원")

    print(f"\n[완료] 총 {created_count}건의 ERP 전화주문을 생성했습니다.")

    # 생성된 주문 확인
    print("\n=== 생성된 주문 목록 ===")
    erp_orders = Order.objects.filter(order_source='erp_phone').order_by('-order_date')
    for order in erp_orders:
        items_count = order.items.count()
        print(f"{order.order_number} | {order.customer_name} | {order.get_order_status_display()} | "
              f"{order.get_payment_status_display()} | {order.final_amount:,}원 | 상품 {items_count}개")

def create_test_order_with_all_fields():
    """모든 필드가 입력된 테스트 주문 생성"""
    
    customers = Customers.objects.all().first()
    if not customers:
        print("[오류] 고객 데이터가 없습니다.")
        return
    
    # 테스트 주문 생성
    order_number = 'ERP-TEST-001'
    
    # 중복 체크
    if Order.objects.filter(order_number=order_number).exists():
        print(f"[건너뜀] {order_number} - 이미 존재합니다. 삭제 후 재생성합니다.")
        Order.objects.filter(order_number=order_number).delete()
    
    order = Order.objects.create(
        order_number=order_number,
        customer_code=customers.code,
        customer_name=customers.name,
        order_source='erp_phone',
        order_status='confirmed',
        payment_status='paid',
        payment_method='transfer',
        shipping_address='테스트 주소 서울시 강남구',
        total_amount=600000,
        total_discount=50000,
        final_amount=550000,
    )
    
    # 주문 상세 생성 (모든 필드 입력)
    OrderItem.objects.create(
        order=order,
        product_code='TEST-CODE-01',
        product_name='테스트 타이어 255/55R19',
        brand='테스트브랜드',
        quantity=4,
        selected_year='2024',
        unit_price=150000,
        basic_discount_rate=5.00,
        customer_discount_rate=3.00,
        additional_discount_rate=0.00,
        dot_discount_rate=0.00,
        total_discount_rate=8.00,
        discounted_price=138000,
        final_price=552000,
    )
    
    # 결제 정보 생성
    Payment.objects.create(
        order=order,
        payment_method='transfer',
        payment_amount=550000,
        payment_status='completed',
        payment_date=datetime.now(),
        memo='테스트 결제',
    )
    
    print(f"[생성] {order.order_number} - 모든 필드 입력 테스트 주문")
    print(f"  - 상품코드: TEST-CODE-01")
    print(f"  - 상품명: 테스트 타이어 255/55R19")
    print(f"  - 브랜드: 테스트브랜드")
    print(f"  - 수량: 4")
    print(f"  - 선택년도: 2024")
    print(f"  - 단가: 150,000원")
    print(f"  - 총 할인율: 8.00%")
    print(f"  - 할인가격: 138,000원")
    print(f"  - 최종가격: 552,000원")

if __name__ == '__main__':
    # create_sample_orders()  # 이미 생성됨
    print("\n=== 테스트 주문 생성 (모든 필드 입력) ===")
    create_test_order_with_all_fields()

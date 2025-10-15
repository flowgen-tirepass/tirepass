"""
5개 샘플 ERP 전화주문 생성 스크립트

ERP 전화주문은 pythonanywhere 재고에 영향을 주지 않고,
ERP 실시간 재고 수량을 받아서 유지합니다.
"""
import os
import django
from datetime import timedelta
from decimal import Decimal

# Django 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "itire.settings")
django.setup()

from tire_data.models import Order, OrderItem, Customers, Goods
from django.utils import timezone


def create_sample_erp_orders():
    """5개 샘플 ERP 전화주문 생성"""

    # 테스트용 고객 목록
    customers_data = [
        {'code': '0-1-0001', 'name': '거라지21'},
        {'code': '0-1-0002', 'name': '고려모터스'},
    ]

    # 샘플 상품 (실제 존재하는 타이어 코드)
    sample_products = [
        'K-HP51-04',  # 금호
        'K-HP51-19',  # 금호
        'K-HP71-09',  # 금호
        'K-KL51-01',  # 금호
        'K-KU50M-03',  # 금호
    ]

    # ERP 주문 5개 생성
    order_count = 0
    for i in range(5):
        customer_idx = i % len(customers_data)
        customer_data = customers_data[customer_idx]

        try:
            # 고객 조회
            customer = Customers.objects.get(code=customer_data['code'])
        except Customers.DoesNotExist:
            print(f"⚠️  고객 {customer_data['code']} 없음 - 건너뜀")
            continue

        # 주문번호 생성 (ERP-날짜-순번)
        order_date = timezone.now() - timedelta(days=i*2)  # 2일 간격
        order_number = f"ERP-{order_date.strftime('%Y%m%d')}-{i+1:03d}"

        # 주문 생성
        order = Order.objects.create(
            order_number=order_number,
            customer_code=customer.code,
            customer_name=customer.name,
            total_amount=0,  # 아래에서 계산
            total_discount=0,
            final_amount=0,
            order_status='confirmed',  # ERP 주문은 바로 확인됨
            payment_status='paid',  # 전화주문은 대부분 나중결제
            payment_method='transfer',  # 계좌이체
            shipping_address=f'{customer.name} 본점',
            shipping_memo='전화주문 - 빠른 배송 요청',
            order_source='erp_phone',  # ⭐ ERP 전화주문
            erp_order_number=f'TEL-{order_date.strftime("%Y%m%d")}-{i+1:03d}',
            order_date=order_date,
            confirmed_date=order_date + timedelta(hours=1),
        )

        # 주문 상세 생성 (1-3개 상품)
        num_items = (i % 3) + 1  # 1, 2, 3개
        total_amount = 0

        for item_idx in range(num_items):
            product_code = sample_products[(i + item_idx) % len(sample_products)]

            try:
                # 상품 조회
                product = Goods.objects.get(code=product_code)

                quantity = 4  # 기본 수량 4개 (타이어 1세트)
                unit_price = product.fixp

                # 할인율 (ERP 전화주문도 할인 적용)
                basic_discount_rate = Decimal('10.00')  # 기본 10%
                customer_discount_rate = Decimal('5.00')  # 고객 5%
                total_discount_rate = basic_discount_rate + customer_discount_rate

                # 가격 계산
                discounted_price = int(unit_price * (1 - total_discount_rate / 100))
                final_price = discounted_price * quantity

                # 주문 상세 생성 (selected_year는 NULL로 - ERP 주문은 제조년도 관리 안함)
                OrderItem.objects.create(
                    order=order,
                    product_code=product.code,
                    product_name=product.name,
                    brand=product.bun1 or '',
                    quantity=quantity,
                    selected_year=None,  # ERP 주문은 제조년도 지정 안함
                    unit_price=unit_price,
                    basic_discount_rate=basic_discount_rate,
                    customer_discount_rate=customer_discount_rate,
                    additional_discount_rate=Decimal('0.00'),
                    dot_discount_rate=Decimal('0.00'),
                    total_discount_rate=total_discount_rate,
                    discounted_price=discounted_price,
                    final_price=final_price
                )

                total_amount += unit_price * quantity

            except Goods.DoesNotExist:
                print(f"⚠️  상품 {product_code} 없음 - 건너뜀")
                continue

        # 주문 총액 업데이트
        if total_amount > 0:
            order.total_amount = total_amount
            order.total_discount = int(total_amount * total_discount_rate / 100)
            order.final_amount = total_amount - order.total_discount
            order.save()

            order_count += 1
            print(f"✅ ERP 주문 {order_count}: {order_number}")
            print(f"   고객: {customer.name} ({customer.code})")
            print(f"   금액: {order.final_amount:,}원")
            print(f"   상품 {num_items}개, 출처: {order.get_order_source_display()}")
            print()

    print(f"\n🎉 총 {order_count}개 ERP 전화주문 생성 완료!")
    print(f"\n📌 중요:")
    print(f"   - ERP 주문은 pythonanywhere 재고를 차감하지 않습니다")
    print(f"   - ERP 실시간 재고 수량을 받아서 유지합니다")
    print(f"   - 고객이 모바일 로그인하면 자신의 모든 주문(모바일+ERP)을 볼 수 있습니다")


if __name__ == '__main__':
    create_sample_erp_orders()

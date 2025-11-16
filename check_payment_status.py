"""
주문과 결제 상태 확인 스크립트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Order, Payment

# 주문 조회
order_numbers = ['ORD20251111009', 'ORD20251111008']
orders = Order.objects.filter(order_number__in=order_numbers)

print("=" * 80)
print("주문 정보")
print("=" * 80)
for order in orders:
    print(f"주문번호: {order.order_number}")
    print(f"  - 고객: {order.customer_name} ({order.customer_code})")
    print(f"  - 주문일시: {order.created_at}")
    print(f"  - 주문상태: {order.order_status}")
    print(f"  - 결제상태: {order.payment_status}")
    print(f"  - 결제방법: {order.payment_method}")
    print(f"  - 주문금액: {order.final_amount:,}원")
    print(f"  - 배송지: {order.shipping_address}")
    print()

print("\n" + "=" * 80)
print("결제 정보")
print("=" * 80)
payments = Payment.objects.filter(order__in=orders)
for payment in payments:
    print(f"주문번호: {payment.order.order_number}")
    print(f"  - 결제상태: {payment.payment_status}")
    print(f"  - 결제금액: {payment.payment_amount:,}원")
    print(f"  - PG사: {payment.pg_name}")
    print(f"  - 토스 주문ID: {payment.order_id_toss}")
    print(f"  - 결제키: {payment.payment_key or '(없음)'}")
    print(f"  - 거래ID: {payment.transaction_id or '(없음)'}")
    print(f"  - 결제일시: {payment.payment_date or '(없음)'}")
    print(f"  - 메모: {payment.memo or '(없음)'}")
    if payment.raw_response:
        print(f"  - 응답 데이터: {payment.raw_response[:200]}...")
    print()

if not orders.exists():
    print("주문을 찾을 수 없습니다.")

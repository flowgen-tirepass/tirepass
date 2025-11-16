"""
10월 31일 결제 기록 조회 스크립트
승인번호: 47705227
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Order, Payment, OrderItem
from django.db.models import Q
import json

print("=" * 80)
print("10월 31일 결제 기록 조회")
print("=" * 80)

# 1. 승인번호로 검색
print("\n[1] 승인번호 47705227 검색...")
payments = Payment.objects.filter(
    Q(transaction_id__icontains='47705227') |
    Q(payment_key__icontains='47705227') |
    Q(memo__icontains='47705227') |
    Q(raw_response__icontains='47705227')
)

if payments.exists():
    print(f"✓ 찾았습니다! ({payments.count()}건)")
    for payment in payments:
        print(f"\n{'='*80}")
        print(f"결제 ID: {payment.id}")
        print(f"주문번호: {payment.order.order_number if payment.order else '없음'}")
        print(f"고객명: {payment.order.customer_name if payment.order else '없음'}")
        print(f"결제 상태: {payment.payment_status}")
        print(f"결제 금액: {payment.payment_amount:,}원")
        print(f"결제 일시: {payment.payment_date}")
        print(f"결제 방법: {payment.payment_method}")
        print(f"PG사: {payment.pg_name}")
        print(f"Payment Key: {payment.payment_key or '없음'}")
        print(f"Transaction ID: {payment.transaction_id or '없음'}")
        print(f"주문 ID (토스): {payment.order_id_toss or '없음'}")
        print(f"메모: {payment.memo or '없음'}")

        if payment.raw_response:
            try:
                response_data = json.loads(payment.raw_response)
                print(f"\n토스페이먼츠 응답:")
                print(f"  - approvedAt: {response_data.get('approvedAt', '없음')}")
                print(f"  - method: {response_data.get('method', '없음')}")
                print(f"  - transactionKey: {response_data.get('transactionKey', '없음')}")
                if 'card' in response_data:
                    card = response_data['card']
                    print(f"  - 카드사: {card.get('company', '없음')}")
                    print(f"  - 카드번호: {card.get('number', '없음')}")
                    print(f"  - 승인번호: {card.get('approveNo', '없음')}")
            except:
                print(f"\nRaw Response (처음 500자):")
                print(payment.raw_response[:500])

        # 주문 상품 정보
        if payment.order:
            items = payment.order.items.all()
            print(f"\n주문 상품 ({items.count()}개):")
            for item in items:
                print(f"  - {item.product_name} x {item.quantity}개 = {item.final_price:,}원")
else:
    print("✗ 승인번호 47705227을 찾을 수 없습니다.")

# 2. 10월 31일 전체 주문 조회
print("\n\n[2] 2024-10-31 전체 주문 조회...")
orders = Order.objects.filter(
    order_date__date='2024-10-31'
).order_by('-order_date')

if orders.exists():
    print(f"✓ {orders.count()}건 발견")
    for order in orders:
        print(f"\n{'='*80}")
        print(f"주문번호: {order.order_number}")
        print(f"고객명: {order.customer_name} ({order.customer_code})")
        print(f"주문일시: {order.order_date}")
        print(f"주문상태: {order.order_status}")
        print(f"결제상태: {order.payment_status}")
        print(f"결제방법: {order.payment_method}")
        print(f"주문금액: {order.final_amount:,}원")

        # 해당 주문의 결제 정보
        try:
            payment = Payment.objects.get(order=order)
            print(f"\n결제 정보:")
            print(f"  - 결제상태: {payment.payment_status}")
            print(f"  - Payment Key: {payment.payment_key or '없음'}")
            print(f"  - Transaction ID: {payment.transaction_id or '없음'}")

            if payment.raw_response and 'approveNo' in payment.raw_response:
                try:
                    response_data = json.loads(payment.raw_response)
                    if 'card' in response_data:
                        approve_no = response_data['card'].get('approveNo', '없음')
                        print(f"  - 승인번호: {approve_no}")
                        if approve_no == '47705227':
                            print(f"    ★★★ 이것이 찾는 결제입니다! ★★★")
                except:
                    pass
        except Payment.DoesNotExist:
            print(f"\n결제 정보: 없음")
        except Payment.MultipleObjectsReturned:
            print(f"\n결제 정보: 여러 개 존재 (비정상)")
else:
    print("✗ 2024-10-31 주문이 없습니다.")

# 3. 10월 한달 전체 통계
print("\n\n[3] 2024년 10월 결제 통계...")
oct_payments = Payment.objects.filter(
    payment_date__year=2024,
    payment_date__month=10,
    payment_status='completed'
)
print(f"완료된 결제: {oct_payments.count()}건")
print(f"총 결제 금액: {sum(p.payment_amount for p in oct_payments):,}원")

print("\n" + "=" * 80)
print("조회 완료")
print("=" * 80)

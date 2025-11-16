"""
10월 31일 결제 기록 조회 (비밀번호 직접 지정)
승인번호: 47705227
"""
import os
import django
import sys

# 환경변수에 DB 비밀번호 설정
os.environ.setdefault('DB_PASSWORD', '#flowgen9569yjm*')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')

django.setup()

from tire_data.models import Order, Payment, OrderItem
from django.db.models import Q
import json

print("=" * 80)
print("10월 31일 결제 기록 조회")
print("=" * 80)

try:
    # 연결 테스트
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ 데이터베이스 연결 성공!\n")
except Exception as e:
    print(f"✗ 데이터베이스 연결 실패: {e}")
    print("\nMySQL 서버가 실행 중인지 확인하세요:")
    print("  - 서비스 관리자에서 MySQL 또는 MySQL80 서비스 시작")
    print("  - 또는 관리자 권한으로: net start MySQL80")
    sys.exit(1)

# 1. 승인번호로 검색
print("[1] 승인번호 47705227 검색...")
payments = Payment.objects.filter(
    Q(transaction_id__icontains='47705227') |
    Q(payment_key__icontains='47705227') |
    Q(memo__icontains='47705227') |
    Q(raw_response__icontains='47705227')
)

if payments.exists():
    print(f"✓ 찾았습니다! ({payments.count()}건)\n")
    for payment in payments:
        print("=" * 80)
        print("★★★ 이것이 10월 31일에 성공한 결제입니다! ★★★")
        print("=" * 80)
        print(f"결제 ID: {payment.id}")
        print(f"주문번호: {payment.order.order_number if payment.order else '없음'}")
        print(f"고객명: {payment.order.customer_name if payment.order else '없음'}")
        print(f"고객코드: {payment.order.customer_code if payment.order else '없음'}")
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
                print(f"\n【 토스페이먼츠 응답 상세 】")
                print(f"  ├─ 승인일시: {response_data.get('approvedAt', '없음')}")
                print(f"  ├─ 결제방법: {response_data.get('method', '없음')}")
                print(f"  ├─ 거래키: {response_data.get('transactionKey', '없음')}")
                print(f"  ├─ 주문ID: {response_data.get('orderId', '없음')}")
                print(f"  └─ 결제키: {response_data.get('paymentKey', '없음')}")

                if 'card' in response_data:
                    card = response_data['card']
                    print(f"\n【 카드 정보 】")
                    print(f"  ├─ 카드사: {card.get('company', '없음')}")
                    print(f"  ├─ 카드번호: {card.get('number', '없음')}")
                    print(f"  ├─ 승인번호: {card.get('approveNo', '없음')} ★")
                    print(f"  ├─ 매입사: {card.get('acquirerCode', '없음')}")
                    print(f"  └─ 발급사: {card.get('issuerCode', '없음')}")

                # 빌링키 정보 확인
                if 'billing' in response_data:
                    print(f"\n【 빌링키 정보 】")
                    print(f"  └─ 빌링키: {response_data['billing']}")
                elif 'billingKey' in response_data:
                    print(f"\n【 빌링키 정보 】")
                    print(f"  └─ 빌링키: {response_data['billingKey']}")
                else:
                    print(f"\n【 빌링키 정보 】")
                    print(f"  └─ 빌링키 없음 (일반 결제)")

            except Exception as e:
                print(f"\nRaw Response 파싱 오류: {e}")
                print(f"Raw Response (처음 500자):")
                print(payment.raw_response[:500])

        # 주문 상품 정보
        if payment.order:
            items = payment.order.items.all()
            print(f"\n【 주문 상품 】 총 {items.count()}개")
            for idx, item in enumerate(items, 1):
                print(f"  {idx}. {item.product_name}")
                print(f"     └─ 수량: {item.quantity}개 / 금액: {item.final_price:,}원")

        print("\n" + "=" * 80)
else:
    print("✗ 승인번호 47705227을 찾을 수 없습니다.\n")

# 2. 10월 31일 전체 주문 조회
print("\n[2] 2024-10-31 전체 주문 조회...")
orders = Order.objects.filter(
    order_date__date='2024-10-31'
).order_by('-order_date')

if orders.exists():
    print(f"✓ {orders.count()}건 발견\n")
    for order in orders:
        print("-" * 80)
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
            print(f"  ├─ 결제상태: {payment.payment_status}")
            print(f"  ├─ Payment Key: {payment.payment_key or '없음'}")
            print(f"  └─ Transaction ID: {payment.transaction_id or '없음'}")

            if payment.raw_response and 'approveNo' in payment.raw_response:
                try:
                    response_data = json.loads(payment.raw_response)
                    if 'card' in response_data:
                        approve_no = response_data['card'].get('approveNo', '없음')
                        print(f"  └─ 승인번호: {approve_no}")
                        if approve_no == '47705227':
                            print(f"     ★★★ 찾는 결제입니다! ★★★")
                except:
                    pass
        except Payment.DoesNotExist:
            print(f"\n결제 정보: 없음 (결제 미완료)")
        except Payment.MultipleObjectsReturned:
            payments = Payment.objects.filter(order=order)
            print(f"\n결제 정보: {payments.count()}개 존재 (비정상)")

        print()
else:
    print("✗ 2024-10-31 주문이 없습니다.\n")

# 3. 11월 11일 광주 업체 미결제 주문 확인
print("\n[3] 2024-11-11 미결제 주문 확인 (광주 업체)...")
problem_orders = Order.objects.filter(
    order_date__date='2024-11-11',
    payment_status='unpaid'
).order_by('-order_date')

if problem_orders.exists():
    print(f"✓ {problem_orders.count()}건 발견\n")
    for order in problem_orders:
        print("-" * 80)
        print(f"주문번호: {order.order_number}")
        print(f"고객명: {order.customer_name} ({order.customer_code})")
        print(f"주문일시: {order.order_date}")
        print(f"주문상태: {order.order_status}")
        print(f"결제상태: {order.payment_status} ⚠️")
        print(f"결제방법: {order.payment_method}")
        print(f"주문금액: {order.final_amount:,}원")

        # Payment 정보 확인
        try:
            payment = Payment.objects.get(order=order)
            print(f"\nPayment 존재: 예")
            print(f"  ├─ 결제상태: {payment.payment_status}")
            print(f"  ├─ Payment Key: {payment.payment_key or '없음'}")
            print(f"  └─ Memo: {payment.memo or '없음'}")
        except Payment.DoesNotExist:
            print(f"\nPayment 존재: 아니오 ⚠️")
            print(f"  └─ /api/mobile/orders/create/로 생성된 주문일 가능성")

        print()
else:
    print("✗ 2024-11-11 미결제 주문이 없습니다.\n")

# 4. 10월 결제 통계
print("\n[4] 2024년 10월 전체 결제 통계...")
oct_payments = Payment.objects.filter(
    payment_date__year=2024,
    payment_date__month=10,
    payment_status='completed'
)
print(f"완료된 결제: {oct_payments.count()}건")
if oct_payments.exists():
    total_amount = sum(p.payment_amount for p in oct_payments)
    print(f"총 결제 금액: {total_amount:,}원")

print("\n" + "=" * 80)
print("조회 완료!")
print("=" * 80)

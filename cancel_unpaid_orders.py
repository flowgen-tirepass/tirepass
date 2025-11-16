"""
미결제 주문 취소 및 재고 복구 스크립트
ORD20251111008, ORD20251111009
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
django.setup()

from tire_data.models import Order, OrderItem, Payment
from tire_data.utils import update_stock

# 취소할 주문 번호
order_numbers = ['ORD20251111008', 'ORD20251111009']

print("=" * 80)
print("미결제 주문 취소 및 재고 복구")
print("=" * 80)

for order_number in order_numbers:
    try:
        order = Order.objects.get(order_number=order_number)
        print(f"\n주문번호: {order.order_number}")
        print(f"  - 고객: {order.customer_name} ({order.customer_code})")
        print(f"  - 현재 주문상태: {order.order_status}")
        print(f"  - 현재 결제상태: {order.payment_status}")
        print(f"  - 주문금액: {order.final_amount:,}원")

        # 주문 아이템 확인
        items = order.items.all()
        print(f"  - 주문 상품: {items.count()}개")

        for item in items:
            print(f"    * {item.product_name} ({item.product_code})")
            print(f"      제조년도: {item.selected_year}, 수량: {item.quantity}개")

            # 재고 복구
            if item.selected_year:
                try:
                    update_stock(
                        product_code=item.product_code,
                        year=item.selected_year,
                        quantity=item.quantity,
                        operation='add'  # 재고 복구
                    )
                    print(f"      ✅ 재고 복구 완료")
                except Exception as e:
                    print(f"      ❌ 재고 복구 실패: {e}")

        # Payment 레코드 확인
        try:
            payment = Payment.objects.get(order=order)
            print(f"  - 결제 정보: {payment.payment_status}")

            # Payment 취소 처리
            payment.payment_status = 'cancelled'
            payment.memo = '등록된 결제 수단 미구현으로 인한 시스템 취소'
            payment.save()
            print(f"  - Payment 상태 변경: cancelled")
        except Payment.DoesNotExist:
            print(f"  - Payment 레코드 없음")

        # 주문 취소
        order.order_status = 'cancelled'
        order.payment_status = 'cancelled'
        order.save()
        print(f"  ✅ 주문 취소 완료")

    except Order.DoesNotExist:
        print(f"\n주문번호 {order_number}: 찾을 수 없음")
    except Exception as e:
        print(f"\n주문번호 {order_number} 처리 중 오류: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("작업 완료")
print("=" * 80)

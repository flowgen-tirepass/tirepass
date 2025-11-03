"""
기존 주문의 깨진 customer_name을 복구하는 스크립트
PythonAnywhere Bash console에서 실행:

cd ~/1.0_tirepass
source venv/bin/activate
python manage.py shell < fix_customer_names.py
"""

from tire_data.models import Order
from tire_data.models import Customers

# 모든 주문 조회
orders = Order.objects.all()

updated_count = 0
error_count = 0

print(f"총 {orders.count()}개 주문 확인 중...")

for order in orders:
    try:
        # customer_code로 고객 정보 조회
        customer = Customers.objects.get(code=order.customer_code)

        # 현재 customer_name이 깨져있거나 비어있으면 업데이트
        if not order.customer_name or len(order.customer_name.encode('utf-8', errors='ignore')) != len(order.customer_name):
            old_name = order.customer_name
            order.customer_name = customer.name
            order.save(update_fields=['customer_name'])
            updated_count += 1
            print(f"✓ 주문 {order.order_number}: '{old_name}' → '{customer.name}'")
    except Customers.DoesNotExist:
        error_count += 1
        print(f"✗ 주문 {order.order_number}: 고객 {order.customer_code} 정보 없음")
    except Exception as e:
        error_count += 1
        print(f"✗ 주문 {order.order_number}: 오류 - {str(e)}")

print(f"\n완료!")
print(f"업데이트: {updated_count}개")
print(f"오류: {error_count}개")

"""
ERP 전화주문 동기화 모듈

ERP 시스템에서 전화주문 내역을 가져와서 Django Order 모델로 변환
현재는 기능만 구현되어 있으며, 실제 화면 출력은 비활성화 상태
"""

from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
import requests
from django.conf import settings


def fetch_erp_phone_orders(start_date=None, end_date=None):
    """
    ERP에서 전화주문 내역 가져오기

    Args:
        start_date: 조회 시작일 (기본: 오늘)
        end_date: 조회 종료일 (기본: 오늘)

    Returns:
        list: ERP 주문 데이터 리스트

    Note:
        - 실제 화면에는 출력되지 않음
        - 백그라운드 동기화 기능용
        - 필요 시 활성화하여 사용
    """

    if start_date is None:
        start_date = timezone.now().date()
    if end_date is None:
        end_date = timezone.now().date()

    # ========================================
    # 실제 구현 시 활성화할 부분 (현재 비활성화)
    # ========================================

    # try:
    #     # TgenAI Gateway API 호출
    #     api_url = getattr(settings, 'ERP_SYNC_API_URL', 'http://itire2.iptime.org:8000')
    #     response = requests.get(
    #         f"{api_url}/orders/phone",
    #         params={
    #             'start_date': start_date.strftime('%Y-%m-%d'),
    #             'end_date': end_date.strftime('%Y-%m-%d'),
    #         },
    #         timeout=30
    #     )
    #
    #     if response.status_code == 200:
    #         orders = response.json().get('orders', [])
    #         return orders
    #     else:
    #         print(f"[오류] ERP API 호출 실패: {response.status_code}")
    #         return []
    #
    # except Exception as e:
    #     print(f"[오류] ERP 주문 조회 중 오류 발생: {e}")
    #     return []

    # 현재는 빈 리스트 반환 (기능만 구현)
    print(f"[정보] ERP 전화주문 조회 기능 (비활성화 상태)")
    print(f"       조회 기간: {start_date} ~ {end_date}")
    print(f"       실제 구현 시 활성화 필요")

    return []


def sync_erp_order_to_django(erp_order):
    """
    ERP 주문 데이터를 Django Order 모델로 변환 및 저장

    Args:
        erp_order (dict): ERP 주문 데이터

    Returns:
        Order: 생성 또는 업데이트된 Order 객체

    Note:
        - ERP 주문번호(erp_order_number)를 기준으로 중복 체크
        - 이미 존재하면 업데이트, 없으면 신규 생성
    """
    from tire_data.models_shopping import Order, OrderItem

    # ERP 주문 데이터 파싱
    erp_order_number = erp_order.get('order_number')
    customer_code = erp_order.get('customer_code')
    customer_name = erp_order.get('customer_name')
    total_amount = erp_order.get('total_amount', 0)
    order_date_str = erp_order.get('order_date')
    items = erp_order.get('items', [])

    # 주문일시 파싱
    if order_date_str:
        order_date = timezone.datetime.fromisoformat(order_date_str)
    else:
        order_date = timezone.now()

    # 주문번호 생성 (ERP 주문번호 기반)
    order_number = f"ERP-{erp_order_number}"

    # 기존 주문 확인
    order, created = Order.objects.get_or_create(
        erp_order_number=erp_order_number,
        defaults={
            'order_number': order_number,
            'customer_code': customer_code,
            'customer_name': customer_name,
            'total_amount': total_amount,
            'total_discount': 0,
            'final_amount': total_amount,
            'order_status': 'confirmed',  # ERP 주문은 이미 확인됨
            'payment_status': 'paid',  # ERP 주문은 결제 완료로 간주
            'order_source': 'erp_phone',  # 전화주문
            'order_date': order_date,
        }
    )

    if created:
        # 주문 상세 생성
        for item in items:
            OrderItem.objects.create(
                order=order,
                product_code=item.get('product_code'),
                product_name=item.get('product_name'),
                brand=item.get('brand', ''),
                quantity=item.get('quantity', 1),
                unit_price=item.get('unit_price', 0),
                total_discount_rate=Decimal(str(item.get('discount_rate', 0))),
                discounted_price=item.get('discounted_price', 0),
                final_price=item.get('final_price', 0),
            )

        print(f"[생성] 새 ERP 주문: {order_number}")
    else:
        print(f"[스킵] 이미 존재하는 주문: {order_number}")

    return order


def sync_today_erp_orders():
    """
    오늘 날짜 ERP 전화주문 동기화

    Note:
        - 매일 정기적으로 실행 가능 (크론탭 등)
        - 현재는 비활성화 상태
    """
    today = timezone.now().date()

    print(f"\n{'='*70}")
    print(f"  ERP 전화주문 동기화")
    print(f"  날짜: {today}")
    print(f"{'='*70}\n")

    # ERP에서 주문 조회
    erp_orders = fetch_erp_phone_orders(start_date=today, end_date=today)

    if not erp_orders:
        print("[정보] 동기화할 ERP 주문이 없습니다.")
        return

    # Django Order로 변환 및 저장
    synced_count = 0
    for erp_order in erp_orders:
        try:
            sync_erp_order_to_django(erp_order)
            synced_count += 1
        except Exception as e:
            print(f"[오류] 주문 동기화 실패: {e}")

    print(f"\n[완료] {synced_count}개 주문 동기화 완료")


# ========================================
# Django Management Command에서 호출 가능
# ========================================

def main():
    """테스트 실행용"""
    sync_today_erp_orders()


if __name__ == '__main__':
    import os
    import sys
    import django

    # Django 설정
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itire.settings')
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    django.setup()

    main()

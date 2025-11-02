"""
모바일 웹 뷰
"""
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import Goods, Order, Payment, ShoppingCart
from .erp_api_client import ERPAPIClient
import logging
import requests
import base64

logger = logging.getLogger(__name__)

def mobile_intro(request):
    """모바일 인트로"""
    # FastAPI를 통해 ERP에서 실시간 상품 개수 조회
    total_products = ERPAPIClient.get_goods_count()

    # API 연결 실패 시 MySQL 데이터로 폴백
    if total_products == 0:
        logger.warning("ERP API unavailable, using MySQL fallback")
        total_products = Goods.objects.count()

    return render(request, 'mobile/intro.html', {
        'total_products': total_products
    })

def mobile_home(request):
    """모바일 홈"""
    return render(request, 'mobile/home.html')

def mobile_login(request):
    """로그인 페이지"""
    return render(request, 'mobile/login.html')

def mobile_register(request):
    """회원가입 페이지"""
    return render(request, 'mobile/register.html')

def mobile_register_payment(request):
    """회원가입 후 결제 수단 등록 페이지"""
    return render(request, 'mobile/register_payment.html', {
        'settings': settings
    })

def mobile_products(request):
    """상품 목록 페이지"""
    return render(request, 'mobile/products.html')

def mobile_product_detail(request, code):
    """상품 상세 페이지"""
    return render(request, 'mobile/product_detail.html', {'product_code': code})

def mobile_cart(request):
    """장바구니 페이지"""
    return render(request, 'mobile/cart.html')

def mobile_orders(request):
    """주문 내역 페이지"""
    return render(request, 'mobile/orders.html')

def mobile_order_detail(request, order_id):
    """주문 상세 페이지"""
    return render(request, 'mobile/order_detail.html', {'order_id': order_id})

def mobile_profile(request):
    """프로필 페이지"""
    return render(request, 'mobile/profile.html', {
        'settings': settings
    })

def mobile_quote(request):
    """견적서 작성 페이지"""
    return render(request, 'mobile/quote.html')

def mobile_addresses(request):
    """배송지 관리 페이지"""
    return render(request, 'mobile/addresses.html')

def mobile_terms(request):
    """이용약관 페이지"""
    return render(request, 'mobile/terms.html')

def mobile_privacy(request):
    """개인정보처리방침 페이지"""
    return render(request, 'mobile/privacy.html')

def mobile_payment_success(request):
    """결제 성공 페이지 (토스페이먼츠 리다이렉트)"""
    # 토스페이먼츠에서 전달하는 쿼리 파라미터
    payment_key = request.GET.get('paymentKey')
    order_id = request.GET.get('orderId')
    amount = request.GET.get('amount')

    if not all([payment_key, order_id, amount]):
        logger.error("결제 성공 콜백: 필수 파라미터 누락")
        return render(request, 'mobile/payment_success.html', {
            'success': False,
            'message': '결제 정보가 올바르지 않습니다.'
        })

    try:
        # 1. 주문 확인
        order = Order.objects.get(order_number=order_id)
        payment = Payment.objects.get(order=order)

        # 2. 토스페이먼츠 승인 API 호출
        secret_key = settings.TOSS_PAYMENTS_SECRET_KEY
        encoded_key = base64.b64encode(f"{secret_key}:".encode()).decode()

        response = requests.post(
            f"{settings.TOSS_PAYMENTS_API_URL}/payments/confirm",
            headers={
                "Authorization": f"Basic {encoded_key}",
                "Content-Type": "application/json"
            },
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": int(amount)
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
        elif response.status_code == 400:
            # ALREADY_PROCESSED_PAYMENT 에러 처리
            error_data = response.json()
            if error_data.get('code') == 'ALREADY_PROCESSED_PAYMENT':
                logger.info(f"이미 승인된 결제, 조회 API로 확인: {order_id}")

                # orderId로 결제 조회
                check_response = requests.get(
                    f"{settings.TOSS_PAYMENTS_API_URL}/payments/orders/{order_id}",
                    headers={"Authorization": f"Basic {encoded_key}"},
                    timeout=10
                )

                if check_response.status_code == 200:
                    result = check_response.json()
                    if result.get('status') == 'DONE':
                        logger.info(f"이미 승인 완료된 결제 확인: {order_id}")
                    else:
                        logger.error(f"결제 상태가 DONE이 아님: {result.get('status')}")
                        return render(request, 'mobile/payment_success.html', {
                            'success': False,
                            'message': '결제가 정상적으로 완료되지 않았습니다.'
                        })
                else:
                    logger.error(f"결제 조회 실패: {check_response.status_code}")
                    return render(request, 'mobile/payment_success.html', {
                        'success': False,
                        'message': '결제 확인에 실패했습니다.'
                    })
            else:
                logger.error(f"토스 승인 실패: {error_data}")
                payment.payment_status = 'failed'
                payment.save()
                return render(request, 'mobile/payment_success.html', {
                    'success': False,
                    'message': error_data.get('message', '결제 승인에 실패했습니다.')
                })
        else:
            error_data = response.json()
            logger.error(f"토스 승인 실패: {error_data}")
            payment.payment_status = 'failed'
            payment.save()
            return render(request, 'mobile/payment_success.html', {
                'success': False,
                'message': error_data.get('message', '결제 승인에 실패했습니다.')
            })

        # 3. Payment 업데이트
        payment.payment_key = payment_key
        payment.payment_status = 'completed'
        payment.pg_transaction_id = result.get('transactionKey', '')
        payment.save()

        # 4. Order 상태 업데이트
        order.payment_status = 'paid'
        order.order_status = 'confirmed'
        order.save()

        # 5. 장바구니 삭제 (주문한 상품과 일치하는 장바구니 항목)
        order_product_codes = order.items.values_list('product_code', flat=True)
        deleted_count = ShoppingCart.objects.filter(
            customer_code=order.customer_code,
            product_code__in=order_product_codes
        ).delete()[0]

        logger.info(f"장바구니 {deleted_count}개 항목 삭제")
        logger.info(f"결제 승인 성공: {order_id}, paymentKey: {payment_key}")

        return render(request, 'mobile/payment_success.html', {
            'success': True,
            'order': order,
            'payment': payment
        })

    except Order.DoesNotExist:
        logger.error(f"주문을 찾을 수 없음: {order_id}")
        return render(request, 'mobile/payment_success.html', {
            'success': False,
            'message': '주문 정보를 찾을 수 없습니다.'
        })
    except Exception as e:
        logger.error(f"결제 승인 처리 오류: {str(e)}")
        return render(request, 'mobile/payment_success.html', {
            'success': False,
            'message': '결제 처리 중 오류가 발생했습니다.'
        })

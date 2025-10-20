"""
모바일 웹 뷰
"""
from django.shortcuts import render
from django.http import HttpResponse
from .models import Goods
from .erp_api_client import ERPAPIClient
import logging

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
    return render(request, 'mobile/profile.html')

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
    return render(request, 'mobile/payment_success.html')

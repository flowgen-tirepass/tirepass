"""
모바일 웹 뷰
"""
from django.shortcuts import render
from django.http import HttpResponse
from .models import Goods

def mobile_intro(request):
    """모바일 인트로"""
    # ERP에서 실시간 상품 개수 조회
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

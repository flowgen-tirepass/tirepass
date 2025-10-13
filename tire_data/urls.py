from django.urls import path
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from . import views, api_views, mobile_views, views_sync_api
# from . import api_views_mobile  # 임시 비활성화 (인코딩 이슈)


def admin_logout_view(request):
    """Admin 로그아웃 핸들러 - admin 로그인 페이지로 리다이렉트"""
    auth_logout(request)
    return redirect('/admin/login/')


urlpatterns = [
    # Admin 로그아웃 오버라이드
    path('admin/logout/', admin_logout_view, name='admin_logout'),

    # Mobile Web URLs
    path('mobile/', mobile_views.mobile_intro, name='mobile_intro'),
    path('mobile/home/', mobile_views.mobile_home, name='mobile_home'),
    path('mobile/login/', mobile_views.mobile_login, name='mobile_login'),
    path('mobile/register/', mobile_views.mobile_register, name='mobile_register'),
    path('mobile/products/', mobile_views.mobile_products, name='mobile_products'),
    path('mobile/products/<str:code>/', mobile_views.mobile_product_detail, name='mobile_product_detail'),
    path('mobile/cart/', mobile_views.mobile_cart, name='mobile_cart'),
    path('mobile/orders/', mobile_views.mobile_orders, name='mobile_orders'),
    path('mobile/orders/<int:order_id>/', mobile_views.mobile_order_detail, name='mobile_order_detail'),
    path('mobile/profile/', mobile_views.mobile_profile, name='mobile_profile'),
    path('mobile/addresses/', mobile_views.mobile_addresses, name='mobile_addresses'),
    path('mobile/quote/', mobile_views.mobile_quote, name='mobile_quote'),

    # Dashboard URLs
    path('', views.index, name='index'),
    path('goods/', views.goods_list, name='goods_list'),
    path('goods/<str:code>/', views.goods_detail, name='goods_detail'),
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/<str:code>/', views.customers_detail, name='customers_detail'),
    path('api/save-year-allocation/', views.save_year_allocation, name='save_year_allocation'),
    path('api/save-discount-rate/', views.save_discount_rate, name='save_discount_rate'),

    # Mobile API URLs
    path('api/mobile/', api_views.api_index, name='api_index'),

    # 상품 API (임시로 MySQL 사용, ERP 연동은 추후 재적용)
    path('api/mobile/products/', api_views.api_products_list, name='api_products_list'),
    path('api/mobile/products/<str:code>/', api_views.api_product_detail, name='api_product_detail'),

    # 장바구니 API
    path('api/mobile/cart/', api_views.api_cart_list, name='api_cart_list'),
    path('api/mobile/cart/add/', api_views.api_cart_add, name='api_cart_add'),
    path('api/mobile/cart/<int:cart_id>/update/', api_views.api_cart_update, name='api_cart_update'),
    path('api/mobile/cart/<int:cart_id>/remove/', api_views.api_cart_remove, name='api_cart_remove'),

    # 주문 API
    path('api/mobile/orders/', api_views.api_order_list, name='api_order_list'),
    path('api/mobile/orders/create/', api_views.api_order_create, name='api_order_create'),
    path('api/mobile/orders/<int:order_id>/', api_views.api_order_detail, name='api_order_detail'),
    path('api/mobile/orders/<int:order_id>/cancel/', api_views.api_order_cancel, name='api_order_cancel'),

    # 가격 계산 API
    path('api/mobile/calculate-price/', api_views.api_calculate_price, name='api_calculate_price'),
    path('api/mobile/calculate-quote/', api_views.api_calculate_quote, name='api_calculate_quote'),

    # 인증 API
    path('api/mobile/auth/register/', api_views.api_auth_register, name='api_auth_register'),
    path('api/mobile/auth/login/', api_views.api_auth_login, name='api_auth_login'),
    path('api/mobile/auth/logout/', api_views.api_auth_logout, name='api_auth_logout'),
    path('api/mobile/auth/profile/', api_views.api_auth_profile, name='api_auth_profile'),
    path('api/mobile/auth/change-password/', api_views.api_auth_change_password, name='api_auth_change_password'),

    # 결제 API (토스페이먼츠 - 임시로 기존 API 사용)
    path('api/mobile/payment/prepare/', api_views.api_payment_prepare, name='api_payment_prepare'),
    path('api/mobile/payment/confirm/', api_views.api_payment_confirm, name='api_payment_confirm'),
    path('api/mobile/payment/cancel/', api_views.api_payment_cancel, name='api_payment_cancel'),
    path('api/mobile/payment/status/<str:payment_key>/', api_views.api_payment_status, name='api_payment_status'),

    # 배송지 주소 API
    path('api/mobile/shipping-addresses/', api_views.api_shipping_addresses_list, name='api_shipping_addresses_list'),
    path('api/mobile/shipping-addresses/add/', api_views.api_shipping_address_add, name='api_shipping_address_add'),
    path('api/mobile/shipping-addresses/<int:address_id>/update/', api_views.api_shipping_address_update, name='api_shipping_address_update'),
    path('api/mobile/shipping-addresses/<int:address_id>/delete/', api_views.api_shipping_address_delete, name='api_shipping_address_delete'),
    path('api/mobile/shipping-addresses/<int:address_id>/set-default/', api_views.api_shipping_address_set_default, name='api_shipping_address_set_default'),

    # ERP 실시간 동기화 API
    path('api/sync/customer/', views_sync_api.sync_customer, name='sync_customer'),
    path('api/sync/goods/', views_sync_api.sync_goods, name='sync_goods'),
    path('api/sync/status/', views_sync_api.sync_status, name='sync_status'),
]
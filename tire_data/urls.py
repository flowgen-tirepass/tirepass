from django.urls import path
from . import views, api_views, mobile_views

urlpatterns = [
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

    # 상품 API
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

    # 가격 계산 API
    path('api/mobile/calculate-price/', api_views.api_calculate_price, name='api_calculate_price'),
    path('api/mobile/calculate-quote/', api_views.api_calculate_quote, name='api_calculate_quote'),

    # 인증 API
    path('api/mobile/auth/register/', api_views.api_auth_register, name='api_auth_register'),
    path('api/mobile/auth/login/', api_views.api_auth_login, name='api_auth_login'),
    path('api/mobile/auth/logout/', api_views.api_auth_logout, name='api_auth_logout'),
    path('api/mobile/auth/profile/', api_views.api_auth_profile, name='api_auth_profile'),
    path('api/mobile/auth/change-password/', api_views.api_auth_change_password, name='api_auth_change_password'),

    # 결제 API (토스페이먼츠)
    path('api/mobile/payment/prepare/', api_views.api_payment_prepare, name='api_payment_prepare'),
    path('api/mobile/payment/confirm/', api_views.api_payment_confirm, name='api_payment_confirm'),
    path('api/mobile/payment/cancel/', api_views.api_payment_cancel, name='api_payment_cancel'),
    path('api/mobile/payment/status/<str:payment_key>/', api_views.api_payment_status, name='api_payment_status'),
]
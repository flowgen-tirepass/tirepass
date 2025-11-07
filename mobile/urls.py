from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # 기본 페이지
    path('', views.mobile_intro, name='mobile_intro'),  # 인트로 페이지로 변경
    path('home/', views.mobile_index, name='mobile_index'),  # 기존 인덱스는 home으로 이동
    path('search/', views.mobile_search, name='mobile_search'),
    path('login/', views.mobile_login, name='mobile_login'),
    path('logout/', views.mobile_logout, name='mobile_logout'),
    path('change-password/', views.mobile_change_password, name='mobile_change_password'),

    # 긴급 수정 페이지
    path('fix-storage/', views.fix_storage, name='mobile_fix_storage'),

    # 상품 상세
    path('product/<str:product_code>/', views.product_detail, name='product_detail'),

    # 장바구니 페이지
    path('cart/', views.cart_view, name='mobile_cart'),

    # 주문/결제 페이지
    path('checkout/', views.checkout_view, name='mobile_checkout'),
    path('order/complete/<int:order_id>/', views.order_complete_view, name='payment_complete'),

    # 주문 내역
    path('orders/', views.orders_view, name='mobile_orders'),
    path('order/<int:order_id>/', views.order_detail_view, name='mobile_order_detail'),

    # 장바구니 API
    path('api/cart/add', api_views.cart_add, name='api_cart_add'),
    path('api/cart', api_views.cart_list, name='api_cart_list'),
    path('api/cart/<int:cart_id>', api_views.cart_update, name='api_cart_update'),
    path('api/cart/<int:cart_id>/delete', api_views.cart_delete, name='api_cart_delete'),

    # 주문 API
    path('api/order/create', api_views.order_create, name='api_order_create'),
    path('api/orders', api_views.orders_list, name='api_orders_list'),
    path('api/orders/<int:order_id>/reorder', api_views.order_reorder, name='api_order_reorder'),

    # 결제 API (토스페이먼츠 콜백)
    path('payment/success', api_views.payment_success, name='payment_success'),
    path('payment/fail', api_views.payment_fail, name='payment_fail'),

    # 고객 정보 API
    path('api/customer/info/', api_views.customer_info, name='api_customer_info'),
]
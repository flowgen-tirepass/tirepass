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

    # 장바구니 API
    path('api/cart/add', api_views.cart_add, name='api_cart_add'),
    path('api/cart', api_views.cart_list, name='api_cart_list'),
    path('api/cart/<int:cart_id>', api_views.cart_update, name='api_cart_update'),
    path('api/cart/<int:cart_id>/delete', api_views.cart_delete, name='api_cart_delete'),

    # 주문 API
    path('api/order/create', api_views.order_create, name='api_order_create'),

    # 결제 API (토스페이먼츠 콜백)
    path('payment/success', api_views.payment_success, name='payment_success'),
    path('payment/fail', api_views.payment_fail, name='payment_fail'),
]
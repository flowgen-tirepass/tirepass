from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_selection, name='customer_selection'),
    path('goods/', views.goods_list, name='goods_list'),
    path('goods/<str:code>/', views.goods_detail, name='goods_detail'),
    path('customers/', views.customers_list, name='customers_list'),  # 새 테이블 사용
    path('customers/<str:code>/', views.customers_detail, name='customers_detail'),
    path('api/save-year-allocation/', views.save_year_allocation, name='save_year_allocation'),
    path('api/save-discount-rate/', views.save_discount_rate, name='save_discount_rate'),
]
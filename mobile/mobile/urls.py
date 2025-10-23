from django.urls import path
from . import views

urlpatterns = [
    path('', views.mobile_intro, name='mobile_intro'),  # 인트로 페이지로 변경
    path('home/', views.mobile_index, name='mobile_index'),  # 기존 인덱스는 home으로 이동
    path('search/', views.mobile_search, name='mobile_search'),
    path('login/', views.mobile_login, name='mobile_login'),
    path('logout/', views.mobile_logout, name='mobile_logout'),
    path('change-password/', views.mobile_change_password, name='mobile_change_password'),
]
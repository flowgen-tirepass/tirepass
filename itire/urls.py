"""
URL configuration for itire project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tire_data.admin_forms import CustomAdminAuthenticationForm
from tire_data.admin import custom_admin_site  # 커스텀 Admin Site 임포트

# 커스텀 로그인 폼 적용 (커스텀 사이트에 적용)
custom_admin_site.login_form = CustomAdminAuthenticationForm
custom_admin_site.login_template = 'admin/login.html'

urlpatterns = [
    path('admin/', custom_admin_site.urls),  # 기본 admin.site 대신 custom_admin_site 사용
    # path('mobile/', include('mobile.urls')),  # 기존 mobile 앱 비활성화
    path('', include('tire_data.urls')),  # admin/logout/ 오버라이드 포함
]

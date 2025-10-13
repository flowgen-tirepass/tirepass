# PythonAnywhere 에러 확인 방법

## 1. Bash Console에서 에러 로그 확인:

```bash
# 에러 로그 확인 (최근 50줄)
tail -50 /var/log/tirepass.pythonanywhere.com.error.log

# 서버 로그 확인
tail -50 /var/log/tirepass.pythonanywhere.com.server.log
```

## 2. Python 문법 체크:

```bash
cd ~/tirepass
python -m py_compile tire_data/api_views_mobile.py
```

## 3. 임시 수정 (API 비활성화):

만약 api_views_mobile.py에 문제가 있다면:

```bash
cd ~/tirepass
nano tire_data/urls.py
```

다음 부분을 주석 처리:

```python
# from . import views, api_views, api_views_mobile, mobile_views, views_sync_api
from . import views, api_views, mobile_views, views_sync_api

# 상품 API (ERP 실시간 연동) - 주석 처리
# path('api/mobile/products/', api_views_mobile.api_products_erp, name='api_products_list'),
# path('api/mobile/products/<str:code>/', api_views_mobile.api_product_detail_erp, name='api_product_detail'),
path('api/mobile/products/', api_views.api_products_list, name='api_products_list'),
path('api/mobile/products/<str:code>/', api_views.api_product_detail, name='api_product_detail'),

# 결제 API 원래대로
# path('api/mobile/payment/prepare/', api_views_mobile.api_payment_prepare_toss, name='api_payment_prepare'),
# path('api/mobile/payment/confirm/', api_views_mobile.api_payment_confirm_toss, name='api_payment_confirm'),
path('api/mobile/payment/prepare/', api_views.api_payment_prepare, name='api_payment_prepare'),
path('api/mobile/payment/confirm/', api_views.api_payment_confirm, name='api_payment_confirm'),
```

**Ctrl+O** (저장), **Enter**, **Ctrl+X** (종료)

그리고 Web Reload

## 4. 에러 로그를 여기에 붙여넣으면 해결책 제시 가능

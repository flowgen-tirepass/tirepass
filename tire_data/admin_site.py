"""
커스텀 Admin Site - 메뉴 그룹화
"""
from django.contrib import admin
from django.contrib.admin import AdminSite


class TirePassAdminSite(AdminSite):
    """
    TirePASS 커스텀 Admin Site

    메뉴 구조:
    - 판매 관리
    - 할인 관리
    - 설정
    """
    site_header = 'TirePASS 관리자'
    site_title = 'TirePASS Admin'
    index_title = '타이어패스 관리 시스템'

    def get_app_list(self, request, app_label=None):
        """
        앱 목록을 커스텀 그룹으로 재구성
        """
        app_dict = self._build_app_dict(request, app_label)

        # 원본 앱 리스트
        original_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # tire_data 앱의 모델들 추출
        tire_data_models = {}
        for app in original_list:
            if app['app_label'] == 'tire_data':
                for model in app['models']:
                    tire_data_models[model['object_name']] = model

        # 커스텀 그룹 구성
        custom_groups = [
            # 📊 판매 관리
            {
                'name': '📊 판매 관리',
                'app_label': 'sales',
                'app_url': '/admin/',
                'has_module_perms': True,
                'models': [
                    tire_data_models.get('Goods'),
                    tire_data_models.get('Customers'),
                    tire_data_models.get('Order'),
                    tire_data_models.get('OrderItem'),
                    tire_data_models.get('ShoppingCart'),
                    tire_data_models.get('Payment'),
                    tire_data_models.get('ShippingAddress'),
                ]
            },
            # 💰 할인 관리
            {
                'name': '💰 할인 관리',
                'app_label': 'discount',
                'app_url': '/admin/',
                'has_module_perms': True,
                'models': [
                    tire_data_models.get('BrandGroup'),
                    tire_data_models.get('BrandGroupPattern'),
                    tire_data_models.get('CustomerDiscount'),
                    tire_data_models.get('CustomerProductDiscount'),
                    tire_data_models.get('DiscountHistory'),
                ]
            },
            # ⚙️ 설정
            {
                'name': '⚙️ 설정',
                'app_label': 'settings',
                'app_url': '/admin/',
                'has_module_perms': True,
                'models': [
                    tire_data_models.get('GoodsPerformanceTag'),  # 주 메뉴
                    tire_data_models.get('PerformanceCategory'),
                    tire_data_models.get('PerformanceTag'),
                    tire_data_models.get('GoodsDisplayName'),
                    tire_data_models.get('YearAllocation'),
                    tire_data_models.get('ERPSnapshot'),
                    tire_data_models.get('CustomersFull'),  # ERP 고객 목록
                ]
            },
        ]

        # None 값 제거
        for group in custom_groups:
            group['models'] = [m for m in group['models'] if m is not None]

        # 다른 앱들 (auth 등) 추가
        other_apps = [app for app in original_list if app['app_label'] != 'tire_data']

        return custom_groups + other_apps


# 커스텀 admin site 인스턴스 생성
tire_admin_site = TirePassAdminSite(name='tire_admin')

"""
tire_data 앱의 폼 정의
"""
from django import forms
from .models import CustomerBrandDiscount, BrandPattern


class BulkDiscountForm(forms.Form):
    """상품 할인율 일괄 적용 폼"""
    discount_rate = forms.DecimalField(
        label='할인율 (%)',
        min_value=0,
        max_value=100,
        decimal_places=2,
        initial=20.00,
        help_text='적용할 할인율을 입력하세요 (0~100)',
        widget=forms.NumberInput(attrs={
            'class': 'vTextField',
            'step': '0.01',
            'style': 'width: 200px;'
        })
    )


class CustomerBrandDiscountForm(forms.ModelForm):
    """고객별 브랜드 할인 폼 - 브랜드 선택 시 패턴 필터링"""

    class Meta:
        model = CustomerBrandDiscount
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 기존 인스턴스가 있으면 해당 브랜드의 패턴만 표시
        if self.instance and self.instance.pk and self.instance.brand:
            self.fields['pattern'].queryset = BrandPattern.objects.filter(
                brand=self.instance.brand,
                is_active=True
            ).order_by('display_order', 'pattern_name')
        else:
            # 새로 추가할 때는 빈 queryset (브랜드 선택 전)
            self.fields['pattern'].queryset = BrandPattern.objects.none()
            self.fields['pattern'].help_text = '먼저 브랜드를 선택하세요'

        # JavaScript로 동적 필터링
        self.fields['pattern'].widget.attrs.update({
            'data-filter-by': 'brand',
        })

    class Media:
        js = ('admin/js/brand_pattern_filter.js',)

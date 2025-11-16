"""
tire_data 앱의 폼 정의
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomerBrandDiscount, BrandPattern, CustomerProductDiscount


class BulkDiscountForm(forms.Form):
    """상품 할인율 일괄 적용 폼"""
    discount_rate = forms.DecimalField(
        label='할인율 (%)',
        min_value=0,
        max_value=100,
        decimal_places=2,
        initial=20.00,
        help_text='적용할 할인율을 입력하세요 (0~100, 음수 입력 불가)',
        widget=forms.NumberInput(attrs={
            'class': 'vTextField',
            'min': '0',
            'max': '100',
            'step': '0.01',
            'style': 'width: 200px;'
        })
    )

    def clean_discount_rate(self):
        """할인율 음수 검증"""
        discount_rate = self.cleaned_data.get('discount_rate')
        if discount_rate is not None and discount_rate < 0:
            raise ValidationError('할인율은 0 이상이어야 합니다. 음수는 입력할 수 없습니다.')
        return discount_rate


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

        # 할인율 필드에 음수 방지 속성 추가
        self.fields['discount_rate'].widget.attrs.update({
            'min': '0',
            'step': '0.01',
        })
        self.fields['discount_rate'].help_text = '할인율은 0 이상이어야 합니다 (음수 입력 불가)'

    def clean_discount_rate(self):
        """할인율 음수 검증"""
        discount_rate = self.cleaned_data.get('discount_rate')
        if discount_rate is not None and discount_rate < 0:
            raise ValidationError('할인율은 0 이상이어야 합니다. 음수는 입력할 수 없습니다.')
        return discount_rate

    class Media:
        js = ('admin/js/brand_pattern_filter.js',)


class CustomerProductDiscountForm(forms.ModelForm):
    """고객별 개별 상품 할인 폼"""

    class Meta:
        model = CustomerProductDiscount
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 할인율 필드에 음수 방지 속성 추가
        self.fields['additional_discount_rate'].widget.attrs.update({
            'min': '0',
            'step': '0.01',
        })
        self.fields['additional_discount_rate'].help_text = '추가 할인율은 0 이상이어야 합니다 (음수 입력 불가)'

    def clean_additional_discount_rate(self):
        """할인율 음수 검증"""
        discount_rate = self.cleaned_data.get('additional_discount_rate')
        if discount_rate is not None and discount_rate < 0:
            raise ValidationError('추가 할인율은 0 이상이어야 합니다. 음수는 입력할 수 없습니다.')
        return discount_rate

"""
tire_data 앱의 폼 정의
"""
from django import forms


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

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

        # 패턴 필드는 선택 사항
        self.fields['pattern'].required = False

        # 기존 인스턴스가 있으면 해당 브랜드의 패턴만 표시
        if self.instance and self.instance.pk and self.instance.brand:
            self.fields['pattern'].queryset = BrandPattern.objects.filter(
                brand=self.instance.brand,
                is_active=True
            ).order_by('display_order', 'pattern_name')
        else:
            # 새로 추가할 때는 모든 패턴 표시 (JavaScript가 필터링함)
            self.fields['pattern'].queryset = BrandPattern.objects.filter(is_active=True)
            self.fields['pattern'].help_text = '브랜드를 선택하면 해당 브랜드의 패턴만 표시됩니다'

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

        # 고객 코드 필드 설정
        self.fields['customer_code'].widget.attrs.update({
            'placeholder': 'ERP 고객코드',
            'style': 'width: 150px;',
        })
        self.fields['customer_code'].help_text = (
            '⚠️ ERP 고객코드를 입력하세요 (예: 0-0-0002, 1-60, 0-4-879). '
            '사업자번호(10자리)가 아닙니다!'
        )

        # 고객명 필드 설정
        self.fields['customer_name'].widget.attrs.update({
            'placeholder': '상호명 입력',
            'style': 'width: 200px;',
        })
        self.fields['customer_name'].help_text = '고객의 상호명을 입력하세요 (확인용)'

        # 할인율 필드에 음수 방지 속성 추가
        self.fields['additional_discount_rate'].widget.attrs.update({
            'min': '0',
            'step': '0.01',
        })
        self.fields['additional_discount_rate'].help_text = '추가 할인율은 0 이상이어야 합니다 (음수 입력 불가)'

    def clean_customer_code(self):
        """고객 코드 형식 검증 - 사업자번호 입력 방지"""
        import re
        customer_code = self.cleaned_data.get('customer_code')

        if not customer_code:
            raise ValidationError('고객 코드를 입력해주세요.')

        # 사업자번호 패턴 감지 (10자리 연속 숫자 또는 000-00-00000 형식)
        cleaned_code = customer_code.replace('-', '')
        if len(cleaned_code) == 10 and cleaned_code.isdigit():
            raise ValidationError(
                f'⚠️ 사업자번호가 아닌 ERP 고객코드를 입력해주세요!\n'
                f'입력값: "{customer_code}" (사업자번호 형식으로 보입니다)\n'
                f'ERP 고객코드 예시: 0-0-0002, 1-60, 0-4-879, 00000228 등'
            )

        return customer_code

    def clean_additional_discount_rate(self):
        """할인율 음수 검증"""
        discount_rate = self.cleaned_data.get('additional_discount_rate')
        if discount_rate is not None and discount_rate < 0:
            raise ValidationError('추가 할인율은 0 이상이어야 합니다. 음수는 입력할 수 없습니다.')
        return discount_rate


# BrandPatternPerformance 모델은 삭제되었습니다 (BrandPattern에 통합됨)
# 아래는 성능표시 선택 옵션 (향후 필요시 사용 가능)
# CLASSIFICATION_CHOICES = [('전체', '전체'), ('승용세단', '승용세단'), ('승용SUV/RV', '승용SUV/RV'), ('트럭/밴', '트럭/밴'), ('스포츠카', '스포츠카')]
# GRADE_CHOICES = [('전체', '전체'), ('가성비', '가성비'), ('고급형', '고급형'), ('최고급형', '최고급형'), ('OE용타이어', 'OE용타이어'), ('전기차', '전기차')]
# PERFORMANCE_CHOICES = [('전체', '전체'), ('스탠다드', '스탠다드'), ('컴포트', '컴포트'), ('스포츠', '스포츠'), ('프리미엄스포츠', '프리미엄스포츠')]
# SEASON_CHOICES = [('사계절용', '사계절용'), ('올웨더', '올웨더'), ('겨울용', '겨울용'), ('여름용', '여름용')]
# ROAD_TYPE_CHOICES = [('오프로드(MT)', '오프로드(MT)'), ('온오프로드(AT)', '온오프로드(AT)'), ('온로드(HT)', '온로드(HT)')]

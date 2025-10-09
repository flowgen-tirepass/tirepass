from django.db import models

class Goods(models.Model):
    """상품(타이어) 정보 모델"""
    code = models.CharField(max_length=20, primary_key=True, verbose_name='상품코드', db_column='CODE')
    name = models.CharField(max_length=100, verbose_name='상품명', db_column='NAME')
    bun1 = models.CharField(max_length=50, null=True, blank=True, verbose_name='브랜드', db_column='BUN1')
    jaego = models.IntegerField(default=0, verbose_name='재고수량', db_column='JAEGO')
    fixp = models.BigIntegerField(default=0, verbose_name='고정가격', db_column='FIXP')

    class Meta:
        db_table = 'goods'
        managed = False  # 기존 테이블 사용
        verbose_name = '상품'
        verbose_name_plural = '상품목록'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def brand(self):
        """브랜드 추출 (코드에서)"""
        return self.extracted_brand

    @property
    def is_tire(self):
        """타이어 여부"""
        return self.check_is_tire()

    @property
    def discount_rate(self):
        """기본 할인율 (기본값 0)"""
        return 0.00

    @property
    def formatted_price(self):
        """가격을 천단위 콤마로 포맷"""
        return f"{self.fixp:,}"

    @property
    def discounted_price(self):
        """할인된 가격 계산"""
        if self.discount_rate and self.discount_rate > 0:
            discount_amount = self.fixp * (float(self.discount_rate) / 100)
            return int(self.fixp - discount_amount)
        return self.fixp

    @property
    def formatted_discounted_price(self):
        """할인된 가격을 천단위 콤마로 포맷"""
        return f"{self.discounted_price:,}"

    @property
    def extracted_brand(self):
        """코드에서 브랜드 추출"""
        code = self.code.upper()

        # 브랜드 식별 패턴
        brand_patterns = {
            'K-': '금호',
            'KUMHO': '금호',
            'H-': '한국',
            'HANKOOK': '한국',
            'M-': '미쉐린',
            'MICHELIN': '미쉐린',
            'N-': '넥센',
            'NEXEN': '넥센',
            'P-': '피렐리',
            'PIRELLI': '피렐리',
            'BS-': '브리지스톤',
            'BRIDGESTONE': '브리지스톤',
            'CT-': '콘티넨탈',
            'CONTINENTAL': '콘티넨탈',
            'D-': '던롭',
            'DUNLOP': '던롭',
            'Y-': '요코하마',
            'YOKOHAMA': '요코하마',
            'F-': '팔켄',
            'FALKEN': '팔켄',
            'T-': '도요',
            'TOYO': '도요',
            'G-': 'GITI',
            'BFG': 'BFG',
        }

        # 코드 앞자리로 매칭
        for pattern, brand in brand_patterns.items():
            if code.startswith(pattern):
                return brand

        # bun1 필드에서 확인
        if self.bun1:
            bun1_upper = self.bun1.upper()
            for pattern, brand in brand_patterns.items():
                if pattern in bun1_upper:
                    return brand

        # name 필드에서 확인
        if self.name:
            name_upper = self.name.upper()
            for pattern, brand in brand_patterns.items():
                if len(pattern) > 2 and pattern in name_upper:
                    return brand

        return self.bun1  # 못 찾으면 기존 bun1 반환

    def check_is_tire(self):
        """타이어 여부 확인"""
        # 코드가 타이어 브랜드 패턴으로 시작하거나
        # 이름에 타이어 관련 단어가 있으면 타이어로 판단
        tire_keywords = ['타이어', 'TIRE', '/', 'R', 'ZR']
        code_patterns = ['K-', 'H-', 'M-', 'N-', 'P-', 'BS-', 'CT-', 'D-', 'Y-', 'F-', 'T-', 'G-', 'BFG']

        # 코드 체크
        code_upper = self.code.upper()
        for pattern in code_patterns:
            if code_upper.startswith(pattern):
                return True

        # 이름 체크 (예: 235/55R19 같은 타이어 사이즈 패턴)
        if self.name:
            import re
            # 타이어 사이즈 패턴: 숫자/숫자R숫자
            if re.search(r'\d+/\d+R\d+', self.name):
                return True
            # 타이어 키워드 체크
            for keyword in tire_keywords[:2]:  # '타이어', 'TIRE'만 체크
                if keyword in self.name.upper():
                    return True

        return False


class CustomersFull(models.Model):
    """ERP 서버 전체 고객 목록 (읽기 전용, 실시간 동기화)"""
    code = models.CharField(max_length=10, primary_key=True, verbose_name='고객코드', db_column='CODE')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='상호', db_column='NAME')
    rep = models.CharField(max_length=50, null=True, blank=True, verbose_name='대표자', db_column='REP')
    tel1 = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화1', db_column='TEL1')
    tel3 = models.CharField(max_length=20, null=True, blank=True, verbose_name='휴대전화', db_column='TEL3')
    tel4 = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화4', db_column='TEL4')
    enno = models.CharField(max_length=20, null=True, blank=True, verbose_name='사업자번호', db_column='ENNO')
    address1 = models.CharField(max_length=255, null=True, blank=True, verbose_name='주소', db_column='ADDRESS1')
    last_sync = models.DateTimeField(null=True, blank=True, verbose_name='최종동기화', db_column='LAST_SYNC')

    class Meta:
        db_table = 'customers'
        managed = False  # ERP 서버가 관리
        verbose_name = 'ERP 고객'
        verbose_name_plural = 'ERP 고객목록'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_real_customer(self):
        """실제 고객인지 확인 (Z로 시작하지 않는 코드)"""
        return not self.code.startswith('Z')


class Customers(models.Model):
    """모바일 회원가입 고객 (pythonanywhere 관리)"""
    code = models.CharField(max_length=10, primary_key=True, verbose_name='고객코드', db_column='code')
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name='상호', db_column='name')
    rep = models.CharField(max_length=20, null=True, blank=True, verbose_name='대표자', db_column='rep')
    tel1 = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화1', db_column='tel1')
    tel3 = models.CharField(max_length=20, null=True, blank=True, verbose_name='휴대전화', db_column='tel3')
    enno = models.CharField(max_length=20, null=True, blank=True, verbose_name='사업자번호', db_column='enno')
    password = models.CharField(max_length=255, null=True, blank=True, verbose_name='비밀번호', db_column='password')

    # 회원가입 관련 필드
    is_registered = models.BooleanField(default=False, verbose_name='회원가입여부', db_column='is_registered')
    user_id = models.IntegerField(null=True, blank=True, verbose_name='사용자ID', db_column='user_id')
    must_change_password = models.BooleanField(default=True, verbose_name='비밀번호변경필요', db_column='must_change_password')

    class Meta:
        db_table = 'customers_simple'
        managed = True  # pythonanywhere가 관리
        verbose_name = '회원'
        verbose_name_plural = '회원목록'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_real_customer(self):
        """실제 고객인지 확인 (Z로 시작하지 않는 코드)"""
        return not self.code.startswith('Z')


class YearAllocation(models.Model):
    """상품별 연도별 재고 할당 및 DOT 할인 모델"""
    goods_code = models.CharField(max_length=20, verbose_name='상품코드')
    year_2025 = models.IntegerField(default=0, verbose_name='2025년 수량')
    year_2024 = models.IntegerField(default=0, verbose_name='2024년 수량')
    year_2023 = models.IntegerField(default=0, verbose_name='2023년 수량')
    year_2022 = models.IntegerField(default=0, verbose_name='2022년 수량')
    year_2021_before = models.IntegerField(default=0, verbose_name='2021년 이전 수량')
    year_2024_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='2024년 할인율(%)')
    year_2023_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='2023년 할인율(%)')
    year_2022_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='2022년 할인율(%)')
    year_2021_before_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='2021년 이전 할인율(%)')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='최종수정')

    class Meta:
        db_table = 'year_allocations'
        managed = True  # Django가 관리하는 테이블
        verbose_name = '연도별 할당'
        verbose_name_plural = '연도별 할당목록'
        unique_together = ['goods_code']  # 상품코드별로 유일

    def __str__(self):
        return f"{self.goods_code} 연도별 할당"

    @property
    def total_allocated(self):
        """할당된 총 수량"""
        return (self.year_2025 + self.year_2024 + self.year_2023 +
                self.year_2022 + self.year_2021_before)


class BrandGroup(models.Model):
    """브랜드별 그룹 관리 모델"""
    brand = models.CharField(max_length=50, verbose_name='브랜드명')
    group_name = models.CharField(max_length=100, verbose_name='그룹명')
    group_order = models.IntegerField(default=0, verbose_name='그룹 순서')
    description = models.TextField(null=True, blank=True, verbose_name='그룹 설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'brand_groups'
        managed = True
        verbose_name = '브랜드 그룹'
        verbose_name_plural = '브랜드 그룹 목록'
        ordering = ['brand', 'group_order', 'group_name']
        unique_together = ['brand', 'group_name']

    def __str__(self):
        return f"{self.brand} - {self.group_name}"


class BrandGroupPattern(models.Model):
    """그룹에 속한 패턴 매핑 모델"""
    group = models.ForeignKey(BrandGroup, on_delete=models.CASCADE,
                             related_name='patterns', verbose_name='그룹')
    pattern = models.CharField(max_length=100, verbose_name='패턴명')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'brand_group_patterns'
        managed = True
        verbose_name = '그룹 패턴'
        verbose_name_plural = '그룹 패턴 목록'
        ordering = ['group', 'pattern']
        unique_together = ['group', 'pattern']

    def __str__(self):
        return f"{self.group.brand} - {self.group.group_name} - {self.pattern}"


class CustomerDiscount(models.Model):
    """고객별 브랜드/그룹 할인율 모델"""
    customer_code = models.CharField(max_length=10, verbose_name='고객 코드')
    brand = models.CharField(max_length=50, verbose_name='브랜드명')
    group = models.ForeignKey(BrandGroup, on_delete=models.SET_NULL,
                             null=True, blank=True,
                             related_name='customer_discounts',
                             verbose_name='그룹')
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2,
                                       default=0.00, verbose_name='할인율(%)')
    priority = models.IntegerField(default=0, verbose_name='우선순위')
    start_date = models.DateField(null=True, blank=True, verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    memo = models.TextField(null=True, blank=True, verbose_name='메모')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    created_by = models.CharField(max_length=50, null=True, blank=True,
                                 verbose_name='생성자')
    updated_by = models.CharField(max_length=50, null=True, blank=True,
                                 verbose_name='수정자')

    class Meta:
        db_table = 'customer_discounts'
        managed = True
        verbose_name = '고객 할인'
        verbose_name_plural = '고객 할인 목록'
        ordering = ['customer_code', 'brand', '-priority']
        unique_together = ['customer_code', 'brand', 'group']

    def __str__(self):
        group_name = self.group.group_name if self.group else '전체'
        return f"{self.customer_code} - {self.brand}/{group_name} - {self.discount_rate}%"

    @property
    def is_valid(self):
        """현재 유효한 할인인지 확인"""
        from datetime import date
        today = date.today()

        if not self.is_active:
            return False

        if self.start_date and today < self.start_date:
            return False

        if self.end_date and today > self.end_date:
            return False

        return True


class DiscountHistory(models.Model):
    """할인 적용 이력 모델"""
    customer_code = models.CharField(max_length=10, verbose_name='고객 코드')
    product_code = models.CharField(max_length=50, verbose_name='상품 코드')
    brand = models.CharField(max_length=50, null=True, blank=True,
                            verbose_name='브랜드')
    group = models.ForeignKey(BrandGroup, on_delete=models.SET_NULL,
                             null=True, blank=True, verbose_name='그룹')
    basic_discount = models.DecimalField(max_digits=5, decimal_places=2,
                                        null=True, blank=True,
                                        verbose_name='기본 할인율')
    customer_discount = models.DecimalField(max_digits=5, decimal_places=2,
                                           null=True, blank=True,
                                           verbose_name='고객 할인율')
    applied_discount = models.DecimalField(max_digits=5, decimal_places=2,
                                          null=True, blank=True,
                                          verbose_name='적용 할인율')
    original_price = models.DecimalField(max_digits=10, decimal_places=2,
                                        null=True, blank=True,
                                        verbose_name='원가')
    final_price = models.DecimalField(max_digits=10, decimal_places=2,
                                     null=True, blank=True,
                                     verbose_name='최종가격')
    transaction_date = models.DateTimeField(auto_now_add=True,
                                           verbose_name='거래일시')

    class Meta:
        db_table = 'discount_history'
        managed = True
        verbose_name = '할인 이력'
        verbose_name_plural = '할인 이력 목록'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.customer_code} - {self.product_code} - {self.transaction_date}"


class CustomerProductDiscount(models.Model):
    """고객별 개별 상품 추가 할인율 모델"""
    customer_code = models.CharField(max_length=10, verbose_name='고객 코드')
    product_code = models.CharField(max_length=20, verbose_name='상품 코드')
    brand = models.CharField(max_length=100, null=True, blank=True, verbose_name='브랜드')
    additional_discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        verbose_name='추가 할인율(%)'
    )
    start_date = models.DateField(null=True, blank=True, verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    memo = models.TextField(null=True, blank=True, verbose_name='메모')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    priority = models.IntegerField(default=0, verbose_name='우선순위')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    created_by = models.CharField(max_length=50, null=True, blank=True,
                                 verbose_name='생성자')
    updated_by = models.CharField(max_length=50, null=True, blank=True,
                                 verbose_name='수정자')

    class Meta:
        db_table = 'customer_product_discounts'
        managed = True
        verbose_name = '고객별 상품 할인'
        verbose_name_plural = '고객별 상품 할인 목록'
        ordering = ['customer_code', 'product_code', '-priority']
        unique_together = ['customer_code', 'product_code']

    def __str__(self):
        return f"{self.customer_code} - {self.product_code} - {self.additional_discount_rate}%"

    @property
    def is_valid(self):
        """현재 유효한 할인인지 확인"""
        from datetime import date
        today = date.today()

        if not self.is_active:
            return False

        if self.start_date and today < self.start_date:
            return False

        if self.end_date and today > self.end_date:
            return False

        return True

    @property
    def customer_name(self):
        """고객명 조회"""
        try:
            customer = Customers.objects.get(code=self.customer_code)
            return customer.name
        except Customers.DoesNotExist:
            return None

    @property
    def product_name(self):
        """상품명 조회"""
        try:
            product = Goods.objects.get(code=self.product_code)
            return product.name
        except Goods.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """저장 시 상품 코드로부터 브랜드 자동 설정"""
        if self.product_code and not self.brand:
            try:
                product = Goods.objects.get(code=self.product_code)
                self.brand = product.brand
            except Goods.DoesNotExist:
                pass
        super().save(*args, **kwargs)


# ============================================
# 쇼핑/주문 관련 모델
# ============================================
from .models_shopping import ShoppingCart, Order, OrderItem, Payment
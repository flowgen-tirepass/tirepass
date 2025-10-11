from django.db import models

class Goods(models.Model):
    """상품(타이어) 정보 모델"""
    code = models.CharField(max_length=20, primary_key=True, verbose_name='상품코드', db_column='CODE')
    name = models.CharField(max_length=100, verbose_name='상품명', db_column='NAME')
    bun1 = models.CharField(max_length=50, null=True, blank=True, verbose_name='브랜드', db_column='BUN1')
    brand = models.CharField(max_length=50, null=True, blank=True, verbose_name='추출브랜드', db_column='brand')  # New field
    is_tire = models.BooleanField(default=False, verbose_name='타이어여부', db_column='is_tire')  # New field
    jaego = models.IntegerField(default=0, verbose_name='재고수량', db_column='JAEGO')
    fixp = models.BigIntegerField(default=0, verbose_name='고정가격', db_column='FIXP')
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='할인율(%)', db_column='discount_rate')  # New field
    last_sync = models.DateTimeField(auto_now=True, verbose_name='최종동기화', db_column='LAST_SYNC')

    class Meta:
        db_table = 'goods'
        managed = False  # 기존 테이블 사용
        verbose_name = '상품'
        verbose_name_plural = '상품목록'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

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


class Customers(models.Model):
    """고객 정보 모델 (간소화 버전)"""
    code = models.CharField(max_length=10, primary_key=True, verbose_name='고객코드', db_column='code')
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name='상호', db_column='name')
    rep = models.CharField(max_length=20, null=True, blank=True, verbose_name='대표자', db_column='rep')
    tel1 = models.CharField(max_length=20, null=True, blank=True, verbose_name='전화1', db_column='tel1')
    tel3 = models.CharField(max_length=20, null=True, blank=True, verbose_name='휴대전화', db_column='tel3')
    enno = models.CharField(max_length=20, null=True, blank=True, verbose_name='사업자번호', db_column='enno')

    # 회원가입 관련 필드
    is_registered = models.BooleanField(default=False, verbose_name='회원가입여부', db_column='is_registered')
    user_id = models.IntegerField(null=True, blank=True, verbose_name='사용자ID', db_column='user_id')
    must_change_password = models.BooleanField(default=True, verbose_name='비밀번호변경필요', db_column='must_change_password')

    # 제거된 필드들 (성능 문제로 인해)
    # tel2, address1, email, last_sync

    class Meta:
        db_table = 'customers_simple'  # 새로운 간소화 테이블 사용
        managed = False  # 기존 테이블 사용
        verbose_name = '고객'
        verbose_name_plural = '고객목록'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_real_customer(self):
        """실제 고객인지 확인 (Z로 시작하지 않는 코드)"""
        return not self.code.startswith('Z')


class YearAllocation(models.Model):
    """상품별 연도별 재고 할당 모델"""
    goods_code = models.CharField(max_length=20, verbose_name='상품코드')
    year_2025 = models.IntegerField(default=0, verbose_name='2025년')
    year_2024 = models.IntegerField(default=0, verbose_name='2024년')
    year_2023 = models.IntegerField(default=0, verbose_name='2023년')
    year_2022 = models.IntegerField(default=0, verbose_name='2022년')
    year_2021_before = models.IntegerField(default=0, verbose_name='2021년 이전')
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
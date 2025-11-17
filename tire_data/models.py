from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class GoodsDisplayName(models.Model):
    """상품 표시명 (한글/영문) 모델"""
    goods_code = models.CharField(max_length=20, primary_key=True, verbose_name='상품코드')
    korean_name = models.CharField(max_length=200, verbose_name='한글 상품명')
    english_name = models.CharField(max_length=200, verbose_name='영문 상품명')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'goods_display_names'
        managed = True
        verbose_name = '상품 표시명'
        verbose_name_plural = 'C. ⚙️ 설정 | 01. 상품 표시명'

    def __str__(self):
        return f"{self.goods_code} - {self.korean_name}"


class ExcludedGoods(models.Model):
    """ERP 동기화에서 제외할 상품 목록"""
    code = models.CharField(max_length=20, primary_key=True, verbose_name='상품코드')
    reason = models.CharField(max_length=200, verbose_name='제외 사유')
    excluded_at = models.DateTimeField(auto_now_add=True, verbose_name='제외일시')
    excluded_by = models.CharField(max_length=50, default='admin', verbose_name='제외자')

    class Meta:
        db_table = 'excluded_goods'
        managed = True
        verbose_name = '제외 상품'
        verbose_name_plural = 'Z. 🗄️ 미사용 | ERP 동기화 제외 상품 (개발용)'

    def __str__(self):
        return f"{self.code} - {self.reason}"


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
        verbose_name_plural = 'A. 📊 판매 | 01. 상품'
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

    # 멤버십 관련 필드 (방안 2: 간편결제 기반)
    membership_tier = models.CharField(
        max_length=20,
        default='regular',
        verbose_name='회원등급',
        db_column='membership_tier',
        choices=[
            ('regular', '🎫 일반 회원'),
            ('premium', '⭐ 프리미엄 회원'),
        ],
        help_text='간편결제 사용 시 프리미엄 회원으로 자동 승급'
    )
    tier_updated_at = models.DateTimeField(null=True, blank=True, verbose_name='등급갱신일', db_column='tier_updated_at')

    class Meta:
        db_table = 'customers_simple'
        managed = True  # pythonanywhere가 관리
        verbose_name = '고객'
        verbose_name_plural = 'A. 📊 판매 | 02. 고객'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_real_customer(self):
        """실제 고객인지 확인 (Z로 시작하지 않는 코드)"""
        return not self.code.startswith('Z')

    @property
    def membership_discount_rate(self):
        """멤버십 등급별 추가 할인율 반환"""
        if self.membership_tier == 'premium':
            return 2.0  # 프리미엄 회원 2% 추가 할인
        return 0.0  # 일반 회원 할인 없음

    def upgrade_to_premium(self):
        """프리미엄 회원으로 승급"""
        from django.utils import timezone
        if self.membership_tier != 'premium':
            self.membership_tier = 'premium'
            self.tier_updated_at = timezone.now()
            self.save(update_fields=['membership_tier', 'tier_updated_at'])
            return True
        return False

    @property
    def point_balance(self):
        """현재 포인트 잔액"""
        try:
            return self.customer_points.balance
        except:
            return 0


# ============================================
# 포인트 시스템
# ============================================

class CustomerPoint(models.Model):
    """고객별 포인트 잔액"""
    customer = models.OneToOneField(
        Customers,
        on_delete=models.CASCADE,
        related_name='customer_points',
        verbose_name='고객'
    )
    balance = models.IntegerField(default=0, verbose_name='포인트 잔액')
    total_earned = models.IntegerField(default=0, verbose_name='누적 적립 포인트')
    total_used = models.IntegerField(default=0, verbose_name='누적 사용 포인트')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='최종 업데이트')

    class Meta:
        db_table = 'customer_points'
        managed = True
        verbose_name = '고객 포인트'
        verbose_name_plural = 'C. ⚙️ 설정 | 03. 고객 포인트'

    def __str__(self):
        return f"{self.customer.name} - {self.balance:,}P"

    def add_points(self, amount, transaction_type, description, order_code=None):
        """포인트 적립"""
        if amount <= 0:
            return False

        self.balance += amount
        self.total_earned += amount
        self.save()

        # 트랜잭션 기록
        PointTransaction.objects.create(
            customer=self.customer,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.balance,
            description=description,
            order_code=order_code
        )
        return True

    def use_points(self, amount, description, order_code=None):
        """포인트 사용"""
        if amount <= 0 or amount > self.balance:
            return False

        self.balance -= amount
        self.total_used += amount
        self.save()

        # 트랜잭션 기록
        PointTransaction.objects.create(
            customer=self.customer,
            transaction_type='USE',
            amount=-amount,
            balance_after=self.balance,
            description=description,
            order_code=order_code
        )
        return True


class PointTransaction(models.Model):
    """포인트 적립/사용 내역"""
    TRANSACTION_TYPE_CHOICES = [
        ('EARN_ORDER', '주문 적립'),
        ('EARN_SIGNUP', '회원가입 적립'),
        ('EARN_EVENT', '이벤트 적립'),
        ('EARN_ADMIN', '관리자 지급'),
        ('USE', '포인트 사용'),
        ('EXPIRE', '포인트 만료'),
        ('CANCEL', '적립 취소'),
    ]

    customer = models.ForeignKey(
        Customers,
        on_delete=models.CASCADE,
        related_name='point_transactions',
        verbose_name='고객'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name='거래 유형'
    )
    amount = models.IntegerField(verbose_name='포인트 금액')
    balance_after = models.IntegerField(verbose_name='거래 후 잔액')
    description = models.CharField(max_length=200, verbose_name='설명')
    order_code = models.CharField(max_length=50, null=True, blank=True, verbose_name='주문번호')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='거래일시')
    expires_at = models.DateField(null=True, blank=True, verbose_name='만료일')

    class Meta:
        db_table = 'point_transactions'
        managed = True
        verbose_name = '포인트 거래 내역'
        verbose_name_plural = 'C. ⚙️ 설정 | 04. 포인트 거래 내역'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['order_code']),
        ]

    def __str__(self):
        return f"{self.customer.name} - {self.get_transaction_type_display()} {self.amount:,}P"


class PointPolicy(models.Model):
    """포인트 정책 설정"""
    name = models.CharField(max_length=100, unique=True, verbose_name='정책명')
    earn_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name='적립률 (%)',
        help_text='결제 금액의 몇 %를 포인트로 적립할지 (예: 1.0 = 1%)'
    )
    min_order_amount = models.IntegerField(
        default=0,
        verbose_name='최소 주문 금액',
        help_text='이 금액 이상 주문 시에만 포인트 적립'
    )
    signup_bonus = models.IntegerField(
        default=0,
        verbose_name='회원가입 보너스',
        help_text='회원가입 시 지급할 포인트'
    )
    point_validity_days = models.IntegerField(
        default=365,
        verbose_name='포인트 유효기간 (일)',
        help_text='포인트 적립 후 며칠간 사용 가능한지'
    )
    min_use_amount = models.IntegerField(
        default=1000,
        verbose_name='최소 사용 포인트',
        help_text='한 번에 사용 가능한 최소 포인트'
    )
    max_use_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100.0,
        verbose_name='최대 사용 비율 (%)',
        help_text='주문 금액의 최대 몇 %까지 포인트로 결제 가능한지'
    )
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'point_policies'
        managed = True
        verbose_name = '포인트 정책'
        verbose_name_plural = 'C. ⚙️ 설정 | 05. 포인트 정책'

    def __str__(self):
        return f"{self.name} (적립 {self.earn_rate}%)"

    @classmethod
    def get_active_policy(cls):
        """활성화된 포인트 정책 반환"""
        return cls.objects.filter(is_active=True).first()


class PaymentMethod(models.Model):
    """고객 결제 수단 (카드/계좌)"""
    PAYMENT_TYPE_CHOICES = [
        ('CARD', '신용/체크카드'),
        ('ACCOUNT', '계좌이체'),
    ]

    customer_code = models.CharField(
        max_length=10,
        verbose_name='고객코드',
        db_column='customer_code',
        db_index=True
    )

    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_TYPE_CHOICES,
        verbose_name='결제수단유형',
        db_column='payment_type'
    )

    # 토스페이먼츠 빌링키 (카드번호 대신 저장)
    billing_key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='빌링키',
        db_column='billing_key',
        null=True,
        blank=True
    )

    # 카드 정보 (마스킹된 정보만 저장)
    card_company = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='카드사',
        db_column='card_company'
    )
    card_last4 = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name='카드끝4자리',
        db_column='card_last4'
    )
    card_type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='카드종류',
        db_column='card_type',
        help_text='신용/체크/법인'
    )

    # 계좌 정보 (암호화하여 저장)
    account_bank = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='은행',
        db_column='account_bank'
    )
    account_number_encrypted = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='계좌번호암호화',
        db_column='account_number_encrypted'
    )
    account_last4 = models.CharField(
        max_length=4,
        null=True,
        blank=True,
        verbose_name='계좌끝4자리',
        db_column='account_last4'
    )
    account_holder = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='예금주',
        db_column='account_holder'
    )

    # 사용자 설정
    nickname = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='별칭',
        db_column='nickname',
        help_text='예: 회사 법인카드, 개인 신한카드'
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name='기본결제수단',
        db_column='is_default'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성화',
        db_column='is_active'
    )

    # 메타 정보
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='등록일시',
        db_column='created_at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시',
        db_column='updated_at'
    )

    class Meta:
        db_table = 'payment_methods'
        managed = True
        verbose_name = '결제수단'
        verbose_name_plural = 'A. 📊 판매 | 03. 결제수단'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        customer_name = self.customer_name or self.customer_code
        if self.payment_type == 'CARD':
            return f"{customer_name} - {self.card_company} {self.card_last4}"
        else:
            return f"{customer_name} - {self.account_bank} {self.account_last4}"

    @property
    def customer(self):
        """고객 객체 조회"""
        try:
            return Customers.objects.get(code=self.customer_code)
        except Customers.DoesNotExist:
            return None

    @property
    def customer_name(self):
        """고객명 조회"""
        customer = self.customer
        return customer.name if customer else None

    def save(self, *args, **kwargs):
        # 기본 결제 수단으로 설정 시, 다른 결제 수단의 is_default를 False로
        if self.is_default:
            PaymentMethod.objects.filter(
                customer_code=self.customer_code,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

        # 간편결제(빌링키) 등록 시 프리미엄 회원으로 자동 승급
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.billing_key:
            # 새로 등록된 빌링키가 있는 경우, 고객을 프리미엄으로 승급
            customer = self.customer
            if customer:
                customer.upgrade_to_premium()

    @property
    def masked_info(self):
        """마스킹된 결제 정보 반환"""
        if self.payment_type == 'CARD':
            return f"{self.card_company} **** **** **** {self.card_last4}"
        else:
            return f"{self.account_bank} ****{self.account_last4} ({self.account_holder})"


class YearAllocation(models.Model):
    """상품별 연도별 재고 할당 및 DOT 할인 모델"""
    goods_code = models.CharField(max_length=20, verbose_name='상품코드')
    year_2025 = models.IntegerField(
        default=0,
        verbose_name='2025년 수량',
        validators=[MinValueValidator(0)]
    )
    year_2024 = models.IntegerField(
        default=0,
        verbose_name='2024년 수량',
        validators=[MinValueValidator(0)]
    )
    year_2023 = models.IntegerField(
        default=0,
        verbose_name='2023년 수량',
        validators=[MinValueValidator(0)]
    )
    year_2022 = models.IntegerField(
        default=0,
        verbose_name='2022년 수량',
        validators=[MinValueValidator(0)]
    )
    year_2021_before = models.IntegerField(
        default=0,
        verbose_name='2021년 이전 수량',
        validators=[MinValueValidator(0)]
    )
    year_2024_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='2024년 할인율(%)',
        validators=[MinValueValidator(0.00)]
    )
    year_2023_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='2023년 할인율(%)',
        validators=[MinValueValidator(0.00)]
    )
    year_2022_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='2022년 할인율(%)',
        validators=[MinValueValidator(0.00)]
    )
    year_2021_before_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='2021년 이전 할인율(%)',
        validators=[MinValueValidator(0.00)]
    )
    base_discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        verbose_name='상품기본할인(%)',
        validators=[MinValueValidator(0.00)]
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name='최종수정')

    class Meta:
        db_table = 'year_allocations'
        managed = True  # Django가 관리하는 테이블
        verbose_name = '연식 할인율'
        verbose_name_plural = 'C. ⚙️ 설정 | 02. 연도 할당률 (DOT)'
        unique_together = ['goods_code']  # 상품코드별로 유일

    def __str__(self):
        return f"{self.goods_code} 연도별 할당"

    @property
    def total_allocated(self):
        """할당된 총 수량"""
        return (self.year_2025 + self.year_2024 + self.year_2023 +
                self.year_2022 + self.year_2021_before)

    def clean(self):
        """연도별 수량 합계가 재고수량을 초과하지 않는지 검증"""
        from django.core.exceptions import ValidationError

        # Goods 테이블에서 실제 재고수량 조회
        try:
            goods = Goods.objects.get(code=self.goods_code)
            stock_quantity = int(goods.jaego)
        except Goods.DoesNotExist:
            raise ValidationError({'goods_code': '존재하지 않는 상품코드입니다.'})
        except (ValueError, TypeError):
            stock_quantity = 0

        # 연도별 수량 합계 계산
        total = (self.year_2025 + self.year_2024 + self.year_2023 +
                self.year_2022 + self.year_2021_before)

        # 재고수량 초과 검증
        if total > stock_quantity:
            raise ValidationError({
                '__all__': f'연도별 수량 합계({total})가 재고수량({stock_quantity})을 초과할 수 없습니다.'
            })

    def save(self, *args, **kwargs):
        """
        YearAllocation 저장

        ⚠️ 중요: Goods.jaego는 ERP 참고용이므로 절대 수정하지 않음!
        - Goods.jaego: ERP 동기화로만 업데이트 (읽기 전용)
        - YearAllocation: 모바일 판매 재고 (관리자가 수정 가능)
        - 두 재고는 독립적으로 관리됨
        """
        import logging
        logger = logging.getLogger(__name__)

        # 기존 데이터가 있으면 이전 total_allocated 계산
        old_total = 0
        if self.pk:
            try:
                old_obj = YearAllocation.objects.get(pk=self.pk)
                old_total = old_obj.total_allocated
            except YearAllocation.DoesNotExist:
                old_total = 0

        # 새로운 total_allocated 계산
        new_total = self.total_allocated

        # 변경량 계산
        change = new_total - old_total

        # 모델 저장
        super().save(*args, **kwargs)

        # 변경사항 로깅 (Goods.jaego는 수정하지 않음!)
        if change != 0:
            logger.info(f"✓ YearAllocation 업데이트: {self.goods_code} | 모바일 판매 가능: {old_total}→{new_total} (변경: {change:+d})")
        else:
            logger.debug(f"YearAllocation 저장: {self.goods_code} | 모바일 판매 가능: {new_total} (변경 없음)")


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
        verbose_name_plural = 'Z. 🗄️ 미사용 | 01. 브랜드 그룹 (구)'
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
        verbose_name_plural = 'Z. 🗄️ 미사용 | 02. 그룹 패턴 (구)'
        ordering = ['group', 'pattern']
        unique_together = ['group', 'pattern']

    def __str__(self):
        return f"{self.group.brand} - {self.group.group_name} - {self.pattern}"


class CustomerDiscount(models.Model):
    """고객별 브랜드/그룹 할인율 모델"""
    customer_code = models.CharField(max_length=10, verbose_name='고객 코드 (구버전, 사업자번호)')
    customer = models.ForeignKey(
        Customers,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        to_field='code',
        related_name='discounts',
        verbose_name='고객'
    )
    brand = models.CharField(max_length=50, verbose_name='브랜드명')
    group = models.ForeignKey(BrandGroup, on_delete=models.SET_NULL,
                             null=True, blank=True,
                             related_name='customer_discounts',
                             verbose_name='그룹')
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2,
                                       default=0.00, verbose_name='할인율(%)',
                                       validators=[MinValueValidator(0.00)])
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
        verbose_name_plural = 'Z. 🗄️ 미사용 | 03. 고객별 할인 (구)'
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
                                        verbose_name='기본 할인율',
                                        validators=[MinValueValidator(0.00)])
    customer_discount = models.DecimalField(max_digits=5, decimal_places=2,
                                           null=True, blank=True,
                                           verbose_name='고객 할인율',
                                           validators=[MinValueValidator(0.00)])
    applied_discount = models.DecimalField(max_digits=5, decimal_places=2,
                                          null=True, blank=True,
                                          verbose_name='적용 할인율',
                                          validators=[MinValueValidator(0.00)])
    original_price = models.DecimalField(max_digits=10, decimal_places=2,
                                        null=True, blank=True,
                                        verbose_name='원가',
                                        validators=[MinValueValidator(0.00)])
    final_price = models.DecimalField(max_digits=10, decimal_places=2,
                                     null=True, blank=True,
                                     verbose_name='최종가격',
                                     validators=[MinValueValidator(0.00)])
    transaction_date = models.DateTimeField(auto_now_add=True,
                                           verbose_name='거래일시')

    class Meta:
        db_table = 'discount_history'
        managed = True
        verbose_name = '할인 이력'
        verbose_name_plural = 'B. 💰 할인 | 05. 할인 이력'
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
        verbose_name='추가 할인율(%)',
        validators=[MinValueValidator(0.00)]
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
        verbose_name_plural = 'B. 💰 할인 | 04. 개별 상품 할인'
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
        # customer_code는 실제로 사업자번호(enno)를 저장
        customer = Customers.objects.filter(enno=self.customer_code).first()
        return customer.name if customer else None

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
# 성능 표기 관련 모델
# ============================================

class PerformanceCategory(models.Model):
    """성능 표기 카테고리 (Section)"""
    name = models.CharField(max_length=50, unique=True, verbose_name='카테고리명')
    display_name = models.CharField(max_length=50, verbose_name='표시명')
    order = models.IntegerField(default=0, verbose_name='정렬순서')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'performance_categories'
        managed = True
        verbose_name = '성능표기 카테고리'
        verbose_name_plural = 'Z. 🗄️ 미사용 | 성능표기 카테고리 (구)'
        ordering = ['order', 'name']

    def __str__(self):
        return self.display_name


class PerformanceTag(models.Model):
    """성능 표기 태그 (Key)"""
    category = models.ForeignKey(
        PerformanceCategory,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='카테고리'
    )
    name = models.CharField(max_length=50, verbose_name='태그명')
    order = models.IntegerField(default=0, verbose_name='정렬순서')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'performance_tags'
        managed = True
        verbose_name = '성능표기 태그'
        verbose_name_plural = 'Z. 🗄️ 미사용 | 성능표기 태그 (구)'
        ordering = ['category__order', 'category', 'order', 'name']
        unique_together = ['category', 'name']

    def __str__(self):
        return f"{self.category.display_name} - {self.name}"


class GoodsPerformanceTag(models.Model):
    """상품별 성능 표기 배정"""
    goods_code = models.CharField(max_length=20, verbose_name='상품코드', db_index=True)
    tag = models.ForeignKey(
        PerformanceTag,
        on_delete=models.CASCADE,
        related_name='goods_tags',
        verbose_name='성능표기'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'goods_performance_tags'
        managed = True
        verbose_name = '상품 성능표기'
        verbose_name_plural = 'Z. 🗄️ 미사용 | 상품 성능표기 (구)'
        unique_together = ['goods_code', 'tag']
        ordering = ['goods_code', 'tag__category__order', 'tag__order']

    def __str__(self):
        return f"{self.goods_code} - {self.tag}"

    def goods_name(self):
        """상품명 조회"""
        try:
            goods = Goods.objects.get(code=self.goods_code)
            return goods.name
        except Goods.DoesNotExist:
            return None
    goods_name.short_description = '상품명'


# ============================================
# ERP 상태 스냅샷 모델
# ============================================

class ERPSnapshot(models.Model):
    """
    ERP 시스템 상태 스냅샷 (매시간 기록)

    사용 사례:
    - 특정 시점의 상품 수 조회
    - ERP 성능 추이 분석
    - 연결 안정성 모니터링
    - 장애 발생 시점 추적
    """
    timestamp = models.DateTimeField(verbose_name='기록 시간', db_index=True)
    status = models.CharField(
        max_length=20,
        verbose_name='상태',
        choices=[
            ('connected', '연결됨'),
            ('disconnected', '연결 끊김'),
            ('timeout', '타임아웃'),
            ('connection_error', '연결 오류'),
        ],
        db_index=True
    )
    response_time_ms = models.FloatField(
        null=True,
        blank=True,
        verbose_name='응답 시간(ms)'
    )
    erp_goods_count = models.IntegerField(
        default=0,
        verbose_name='ERP 상품 수'
    )
    database_status = models.CharField(
        max_length=20,
        verbose_name='DB 상태',
        default='unknown'
    )
    api_url = models.CharField(
        max_length=200,
        verbose_name='API URL'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='오류 메시지'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='레코드 생성일시')

    class Meta:
        db_table = 'erp_snapshots'
        managed = True
        verbose_name = 'ERP 스냅샷'
        verbose_name_plural = 'Z. 🗄️ 미사용 | ERP 스냅샷 (개발용)'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['status', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} | {self.status} | {self.erp_goods_count:,}개"

    @classmethod
    def get_count_at_time(cls, target_datetime):
        """
        특정 시점의 상품 수 조회

        Args:
            target_datetime: 조회할 시간 (datetime)

        Returns:
            int: 상품 수 (없으면 None)
        """
        snapshot = cls.objects.filter(
            timestamp__lte=target_datetime,
            status='connected'
        ).order_by('-timestamp').first()

        if snapshot:
            return snapshot.erp_goods_count
        return None

    @classmethod
    def get_today_9am_count(cls):
        """오늘 09시 상품 수 조회"""
        from django.utils import timezone
        today = timezone.now().date()
        target_time = timezone.datetime.combine(
            today,
            timezone.datetime.min.time().replace(hour=9)
        )
        target_time = timezone.make_aware(target_time)
        return cls.get_count_at_time(target_time)

    @classmethod
    def get_hourly_stats(cls, hours=24):
        """최근 N시간 통계"""
        from django.utils import timezone
        from django.db.models import Avg, Max, Min, Count

        start_time = timezone.now() - timezone.timedelta(hours=hours)

        return cls.objects.filter(
            timestamp__gte=start_time
        ).aggregate(
            avg_response_time=Avg('response_time_ms'),
            max_response_time=Max('response_time_ms'),
            min_response_time=Min('response_time_ms'),
            total_checks=Count('id'),
            connected_count=Count('id', filter=models.Q(status='connected'))
        )


# ============================================
# 실시간 재고 변화 추적 모델
# ============================================

class GoodsRealtimeSnapshot(models.Model):
    """
    실시간 재고 변화 추적 (매시간 스냅샷)

    용도:
    - 시간별 재고 변화 추적
    - 실시간성 증명 (관리자 위젯용)
    - 인기 상품 분석
    """
    code = models.CharField(max_length=50, verbose_name='상품코드', db_index=True)
    name = models.CharField(max_length=200, verbose_name='상품명')
    bun1 = models.CharField(max_length=100, null=True, blank=True, verbose_name='브랜드')
    jaego = models.IntegerField(verbose_name='재고수량')
    snapshot_time = models.DateTimeField(verbose_name='스냅샷 시간', db_index=True)
    change_from_prev = models.IntegerField(default=0, verbose_name='이전 대비 변화량')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'goods_realtime_snapshots'
        managed = True
        verbose_name = '실시간 재고 스냅샷'
        verbose_name_plural = 'Z. 🗄️ 미사용 | 실시간 재고 추적 (개발용)'
        ordering = ['-snapshot_time', 'code']
        indexes = [
            models.Index(fields=['code', '-snapshot_time']),
            models.Index(fields=['-snapshot_time']),
        ]

    def __str__(self):
        change_indicator = '🔴' if self.change_from_prev < 0 else ('🟢' if self.change_from_prev > 0 else '⚪')
        return f"{self.code} | {self.snapshot_time.strftime('%m-%d %H:%M')} | {self.jaego}개 ({self.change_from_prev:+d}) {change_indicator}"

    @classmethod
    def get_recent_changes(cls, hours=24, limit=5):
        """
        최근 N시간 동안 변화가 많은 상품 조회

        Args:
            hours: 조회 기간 (시간)
            limit: 반환할 상품 수

        Returns:
            QuerySet: 변화량 기준 상위 상품
        """
        from django.utils import timezone
        from django.db.models import Sum, Max

        start_time = timezone.now() - timezone.timedelta(hours=hours)

        # 상품별 총 변화량 계산
        changes = cls.objects.filter(
            snapshot_time__gte=start_time
        ).values('code', 'name', 'bun1').annotate(
            total_change=Sum('change_from_prev'),
            last_snapshot=Max('snapshot_time')
        ).order_by('-total_change')[:limit]

        return changes

    @classmethod
    def get_hourly_data(cls, code, hours=24):
        """
        특정 상품의 시간별 재고 데이터

        Args:
            code: 상품 코드
            hours: 조회 기간

        Returns:
            QuerySet: 시간별 재고 데이터
        """
        from django.utils import timezone

        start_time = timezone.now() - timezone.timedelta(hours=hours)

        return cls.objects.filter(
            code=code,
            snapshot_time__gte=start_time
        ).order_by('snapshot_time')


# ============================================
# 새로운 브랜드/패턴 기반 할인 모델
# ============================================

class Brand(models.Model):
    """브랜드 마스터"""
    name = models.CharField(max_length=50, unique=True, verbose_name='브랜드명')
    name_en = models.CharField(max_length=50, null=True, blank=True, verbose_name='영문명')
    logo_image = models.ImageField(
        upload_to='brands/logos/',
        null=True,
        blank=True,
        verbose_name='브랜드 로고 이미지',
        help_text='브랜드 로고 이미지를 업로드하세요 (PNG, JPG 권장)'
    )
    display_order = models.IntegerField(default=0, verbose_name='표시 순서')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'brands'
        managed = True
        verbose_name = '브랜드'
        verbose_name_plural = 'B. 💰 할인 | 01. 브랜드'
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    @property
    def logo_url(self):
        """로고 이미지 URL 반환 (API용)"""
        if self.logo_image:
            return self.logo_image.url
        return None


class BrandPattern(models.Model):
    """브랜드별 패턴"""

    # 성능표시 선택 옵션
    CLASSIFICATION_CHOICES = [
        ('', '--------'),
        ('전체', '전체'),
        ('승용세단', '승용세단'),
        ('승용SUV/RV', '승용SUV/RV'),
        ('트럭/밴', '트럭/밴'),
        ('스포츠카', '스포츠카'),
    ]

    GRADE_CHOICES = [
        ('', '--------'),
        ('전체', '전체'),
        ('가성비', '가성비'),
        ('고급형', '고급형'),
        ('최고급형', '최고급형'),
        ('OE용타이어', 'OE용타이어'),
        ('전기차', '전기차'),
    ]

    PERFORMANCE_CHOICES = [
        ('', '--------'),
        ('전체', '전체'),
        ('스탠다드', '스탠다드'),
        ('컴포트', '컴포트'),
        ('스포츠', '스포츠'),
        ('프리미엄스포츠', '프리미엄스포츠'),
    ]

    SEASON_CHOICES = [
        ('', '--------'),
        ('사계절용', '사계절용'),
        ('올웨더', '올웨더'),
        ('겨울용', '겨울용'),
        ('여름용', '여름용'),
    ]

    ROAD_TYPE_CHOICES = [
        ('', '--------'),
        ('오프로드(MT)', '오프로드(MT)'),
        ('온오프로드(AT)', '온오프로드(AT)'),
        ('온로드(HT)', '온로드(HT)'),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,
                             related_name='patterns', verbose_name='브랜드')
    pattern_name = models.CharField(max_length=100, verbose_name='패턴명')
    pattern_code = models.CharField(max_length=50, null=True, blank=True,
                                   verbose_name='패턴 코드')
    display_order = models.IntegerField(default=0, verbose_name='표시 순서')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    # 성능 표시 (5개 박스) - 모바일 상품카드용
    # 박스1: 브랜드명 (한글) - 자동으로 brand.name 사용
    # 박스2: 분류1
    classification = models.CharField(
        max_length=50,
        choices=CLASSIFICATION_CHOICES,
        null=True,
        blank=True,
        verbose_name='분류1'
    )

    # 박스3: 상품등급
    grade = models.CharField(
        max_length=50,
        choices=GRADE_CHOICES,
        null=True,
        blank=True,
        verbose_name='상품등급'
    )

    # 박스4: 상품성능
    performance = models.CharField(
        max_length=50,
        choices=PERFORMANCE_CHOICES,
        null=True,
        blank=True,
        verbose_name='상품성능'
    )

    # 박스5: 계절 + ON/OFF로드
    season = models.CharField(
        max_length=20,
        choices=SEASON_CHOICES,
        null=True,
        blank=True,
        verbose_name='계절'
    )
    road_type = models.CharField(
        max_length=20,
        choices=ROAD_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='ON/OFF로드'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'brand_patterns'
        managed = True
        verbose_name = '브랜드 패턴'
        verbose_name_plural = 'B. 💰 할인 | 02. 브랜드 패턴'
        ordering = ['brand', 'display_order', 'pattern_name']
        unique_together = ['brand', 'pattern_name']

    def __str__(self):
        return f"{self.brand.name} - {self.pattern_name}"

    def get_performance_boxes(self):
        """5개 성능 박스 반환 (모바일 상품카드용)"""
        boxes = []

        # 박스1: 브랜드명 (한글)
        boxes.append(self.brand.name)

        # 박스2: 분류1
        if self.classification:
            boxes.append(self.classification)

        # 박스3: 상품등급
        if self.grade:
            boxes.append(self.grade)

        # 박스4: 상품성능
        if self.performance:
            boxes.append(self.performance)

        # 박스5: 계절 + ON/OFF로드
        season_road = []
        if self.season:
            season_road.append(self.season)
        if self.road_type:
            season_road.append(self.road_type)
        if season_road:
            boxes.append(' / '.join(season_road))

        return boxes


class CustomerBrandDiscount(models.Model):
    """고객별 브랜드/패턴 할인율"""
    customer = models.ForeignKey(
        Customers,
        on_delete=models.CASCADE,
        to_field='code',
        db_column='customer_code',
        related_name='brand_discounts',
        verbose_name='고객'
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,
                             related_name='customer_discounts',
                             verbose_name='브랜드')
    pattern = models.ForeignKey(BrandPattern, on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name='customer_discounts',
                               verbose_name='패턴')
    discount_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        verbose_name='할인율(%)',
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    start_date = models.DateField(null=True, blank=True, verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')
    memo = models.TextField(null=True, blank=True, verbose_name='메모')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    priority = models.IntegerField(default=0, verbose_name='우선순위')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    created_by = models.CharField(max_length=50, null=True, blank=True,
                                 verbose_name='생성자')
    updated_by = models.CharField(max_length=50, null=True, blank=True,
                                 verbose_name='수정자')

    class Meta:
        db_table = 'customer_brand_discounts'
        managed = True
        verbose_name = '고객별 브랜드 할인'
        verbose_name_plural = 'B. 💰 할인 | 03. 고객별 할인'
        ordering = ['customer', 'brand', 'pattern', '-priority']
        unique_together = ['customer', 'brand', 'pattern']

    def __str__(self):
        pattern_name = self.pattern.pattern_name if self.pattern else '전체'
        return f"{self.customer.code} - {self.brand.name}/{pattern_name} - {self.discount_rate}%"

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


# ============================================
# 쇼핑/주문 관련 모델
# ============================================
from .models_shopping import ShoppingCart, Order, OrderItem, Payment, ShippingAddress
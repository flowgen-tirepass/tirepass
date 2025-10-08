"""
쇼핑/주문 관련 모델
"""
from django.db import models
from decimal import Decimal


class ShoppingCart(models.Model):
    """장바구니 모델"""
    customer_code = models.CharField(max_length=10, verbose_name='고객 코드')
    product_code = models.CharField(max_length=20, verbose_name='상품 코드')
    quantity = models.IntegerField(default=1, verbose_name='수량')
    selected_year = models.IntegerField(null=True, blank=True, verbose_name='선택 제조년도(DOT)')
    unit_price = models.BigIntegerField(verbose_name='단가')
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='적용 할인율(%)')
    final_price = models.BigIntegerField(verbose_name='최종가격')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'shopping_cart'
        managed = True
        verbose_name = '장바구니'
        verbose_name_plural = '장바구니 목록'
        ordering = ['-created_at']
        unique_together = ['customer_code', 'product_code', 'selected_year']

    def __str__(self):
        return f"{self.customer_code} - {self.product_code} ({self.quantity}개)"

    @property
    def product_name(self):
        """상품명 조회"""
        from .models import Goods
        try:
            goods = Goods.objects.get(code=self.product_code)
            return goods.name
        except Goods.DoesNotExist:
            return '-'

    @property
    def customer_name(self):
        """고객명 조회"""
        from .models import Customers
        try:
            customer = Customers.objects.get(code=self.customer_code)
            return customer.name
        except Customers.DoesNotExist:
            return '-'


class Order(models.Model):
    """주문 모델"""
    ORDER_STATUS_CHOICES = [
        ('pending', '주문대기'),
        ('confirmed', '주문확인'),
        ('preparing', '출고준비'),
        ('shipped', '배송중'),
        ('delivered', '배송완료'),
        ('cancelled', '주문취소'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', '미결제'),
        ('paid', '결제완료'),
        ('refunded', '환불완료'),
    ]

    order_number = models.CharField(max_length=50, unique=True, verbose_name='주문번호')
    customer_code = models.CharField(max_length=10, verbose_name='고객 코드')
    customer_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='고객명')
    total_amount = models.BigIntegerField(default=0, verbose_name='총 주문금액')
    total_discount = models.BigIntegerField(default=0, verbose_name='총 할인금액')
    final_amount = models.BigIntegerField(default=0, verbose_name='최종 결제금액')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name='주문상태')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid', verbose_name='결제상태')
    payment_method = models.CharField(max_length=20, null=True, blank=True, verbose_name='결제방법')
    shipping_address = models.TextField(null=True, blank=True, verbose_name='배송지 주소')
    shipping_memo = models.TextField(null=True, blank=True, verbose_name='배송 메모')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='주문일시')
    confirmed_date = models.DateTimeField(null=True, blank=True, verbose_name='주문확인일시')
    shipped_date = models.DateTimeField(null=True, blank=True, verbose_name='출고일시')
    delivered_date = models.DateTimeField(null=True, blank=True, verbose_name='배송완료일시')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'orders'
        managed = True
        verbose_name = '주문'
        verbose_name_plural = '주문 목록'
        ordering = ['-order_date']

    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"

    def get_order_status_display_korean(self):
        """주문상태 한글 표시"""
        status_dict = dict(self.ORDER_STATUS_CHOICES)
        return status_dict.get(self.order_status, self.order_status)

    def get_payment_status_display_korean(self):
        """결제상태 한글 표시"""
        status_dict = dict(self.PAYMENT_STATUS_CHOICES)
        return status_dict.get(self.payment_status, self.payment_status)


class OrderItem(models.Model):
    """주문 상세 모델"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='주문')
    product_code = models.CharField(max_length=20, verbose_name='상품 코드')
    product_name = models.CharField(max_length=100, verbose_name='상품명')
    brand = models.CharField(max_length=50, null=True, blank=True, verbose_name='브랜드')
    quantity = models.IntegerField(default=1, verbose_name='수량')
    selected_year = models.IntegerField(null=True, blank=True, verbose_name='선택 제조년도(DOT)')
    unit_price = models.BigIntegerField(verbose_name='단가')
    basic_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='기본 할인율(%)')
    customer_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='고객 할인율(%)')
    additional_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='추가 할인율(%)')
    dot_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='DOT 할인율(%)')
    total_discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='총 할인율(%)')
    discounted_price = models.BigIntegerField(verbose_name='할인가격')
    final_price = models.BigIntegerField(verbose_name='최종가격(수량포함)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        db_table = 'order_items'
        managed = True
        verbose_name = '주문 상세'
        verbose_name_plural = '주문 상세 목록'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.order.order_number} - {self.product_name} ({self.quantity}개)"


class Payment(models.Model):
    """결제 모델"""
    PAYMENT_METHOD_CHOICES = [
        ('card', '카드결제'),
        ('transfer', '계좌이체'),
        ('cash', '현금결제'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', '결제대기'),
        ('completed', '결제완료'),
        ('failed', '결제실패'),
        ('cancelled', '결제취소'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name='주문')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='결제방법')
    payment_amount = models.BigIntegerField(verbose_name='결제금액')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', verbose_name='결제상태')
    transaction_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='거래번호(PG사)', db_column='transaction_id')
    payment_key = models.CharField(max_length=200, null=True, blank=True, verbose_name='토스 결제 키', db_column='payment_key')
    order_id_toss = models.CharField(max_length=100, null=True, blank=True, verbose_name='토스 주문 ID', db_column='order_id_toss')
    pg_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='PG사명')
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='결제일시')
    cancelled_date = models.DateTimeField(null=True, blank=True, verbose_name='취소일시')
    memo = models.TextField(null=True, blank=True, verbose_name='메모')
    raw_response = models.TextField(null=True, blank=True, verbose_name='결제 원본 응답', db_column='raw_response')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        db_table = 'payments'
        managed = True
        verbose_name = '결제'
        verbose_name_plural = '결제 목록'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_payment_method_display()} ({self.payment_amount:,}원)"

    def get_payment_status_display_korean(self):
        """결제상태 한글 표시"""
        status_dict = dict(self.PAYMENT_STATUS_CHOICES)
        return status_dict.get(self.payment_status, self.payment_status)

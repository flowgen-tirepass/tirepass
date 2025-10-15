# 재고 및 주문 이원화 관리 시스템

## 📋 개요

**목적**: ERP 데이터와 모바일 데이터를 분리하여 독립적으로 관리하면서도 통합 조회 가능

### 현재 상황
- ✅ ERP 재고: ERP에서 동기화 (읽기 전용)
- ✅ 모바일 고객: `customers_simple` 테이블로 별도 관리 중
- ❌ 모바일 재고: 아직 별도 관리 없음 (ERP 재고를 그대로 사용)
- ❌ ERP 전화주문: 별도 기록 없음
- ❌ 주문 통합 대시보드: 없음

---

## 🎯 구현 목표

### 1. 모바일 전용 재고 관리
- 모바일에서 판매 가능한 재고 별도 추적
- 주문 시 자동 차감, 취소/반품 시 자동 복구
- ERP 재고와 독립적 관리

### 2. 주문 데이터 이원화
- **ERP 전화주문**: ERP에서 발생한 주문 기록
- **모바일 주문**: 앱/웹에서 발생한 주문 (현재 Order 모델)
- 두 데이터를 구분하여 저장하되 통합 조회 가능

### 3. 통합 대시보드
- 전화주문 vs 모바일주문 비교
- 일별/월별 매출 통합 집계
- 재고 현황: ERP 재고 vs 모바일 가용 재고

---

## 🗂️ 데이터베이스 설계

### 1. MobileInventory 모델 (신규)

```python
class MobileInventory(models.Model):
    """모바일 전용 재고 관리"""
    goods_code = models.CharField(max_length=20, unique=True, verbose_name='상품코드')
    available_quantity = models.IntegerField(default=0, verbose_name='모바일 가용 재고')
    reserved_quantity = models.IntegerField(default=0, verbose_name='예약 수량')
    sold_quantity = models.IntegerField(default=0, verbose_name='판매 수량')
    last_synced_from_erp = models.DateTimeField(null=True, blank=True, verbose_name='ERP 마지막 동기화')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='최종 수정')
    memo = models.TextField(null=True, blank=True, verbose_name='메모')

    class Meta:
        db_table = 'mobile_inventory'
        verbose_name = '모바일 재고'
        verbose_name_plural = '📊 판매 | 07. 모바일 재고'

    @property
    def erp_quantity(self):
        """ERP 재고 수량 조회"""
        try:
            goods = Goods.objects.get(code=self.goods_code)
            return goods.jaego
        except Goods.DoesNotExist:
            return 0

    @property
    def total_quantity(self):
        """총 재고 = 가용 + 예약"""
        return self.available_quantity + self.reserved_quantity
```

### 2. Order 모델 확장

```python
class Order(models.Model):
    # 기존 필드 유지

    # 주문 소스 추가
    ORDER_SOURCE_CHOICES = [
        ('mobile', '모바일 주문'),
        ('erp_phone', 'ERP 전화주문'),
        ('erp_import', 'ERP 수동입력'),
    ]
    order_source = models.CharField(
        max_length=20,
        choices=ORDER_SOURCE_CHOICES,
        default='mobile',
        verbose_name='주문 출처'
    )
    erp_order_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='ERP 주문번호'
    )
```

### 3. InventoryTransaction 모델 (신규)

```python
class InventoryTransaction(models.Model):
    """재고 변동 이력"""
    TRANSACTION_TYPE_CHOICES = [
        ('order', '주문'),
        ('cancel', '취소'),
        ('return', '반품'),
        ('manual_add', '수동 증가'),
        ('manual_subtract', '수동 감소'),
        ('sync_from_erp', 'ERP 동기화'),
    ]

    goods_code = models.CharField(max_length=20, verbose_name='상품코드')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    quantity_change = models.IntegerField(verbose_name='변동 수량')  # + or -
    before_quantity = models.IntegerField(verbose_name='변경 전 재고')
    after_quantity = models.IntegerField(verbose_name='변경 후 재고')
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.CharField(max_length=50, verbose_name='처리자')
    created_at = models.DateTimeField(auto_now_add=True)
    memo = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'inventory_transactions'
        verbose_name = '재고 변동 이력'
        verbose_name_plural = '📊 판매 | 08. 재고 변동 이력'
        ordering = ['-created_at']
```

---

## 🔄 비즈니스 로직

### 1. 주문 생성 시

```python
def create_order(customer_code, items):
    """주문 생성 및 재고 차감"""

    # 1. 재고 확인
    for item in items:
        mobile_inv = MobileInventory.objects.get(goods_code=item['code'])
        if mobile_inv.available_quantity < item['quantity']:
            raise ValueError(f'{item["name"]} 재고 부족')

    # 2. 주문 생성
    order = Order.objects.create(
        customer_code=customer_code,
        order_source='mobile',
        # ... other fields
    )

    # 3. 재고 차감 및 이력 기록
    for item in items:
        mobile_inv = MobileInventory.objects.get(goods_code=item['code'])
        before_qty = mobile_inv.available_quantity

        mobile_inv.available_quantity -= item['quantity']
        mobile_inv.sold_quantity += item['quantity']
        mobile_inv.save()

        # 이력 기록
        InventoryTransaction.objects.create(
            goods_code=item['code'],
            transaction_type='order',
            quantity_change=-item['quantity'],
            before_quantity=before_qty,
            after_quantity=mobile_inv.available_quantity,
            order=order,
            created_by='system'
        )

    return order
```

### 2. 주문 취소 시

```python
def cancel_order(order_id):
    """주문 취소 및 재고 복구"""
    order = Order.objects.get(id=order_id)

    if order.order_status not in ['pending', 'confirmed']:
        raise ValueError('취소 불가능한 상태')

    # 재고 복구
    for item in order.items.all():
        mobile_inv = MobileInventory.objects.get(goods_code=item.product_code)
        before_qty = mobile_inv.available_quantity

        mobile_inv.available_quantity += item.quantity
        mobile_inv.sold_quantity -= item.quantity
        mobile_inv.save()

        # 이력 기록
        InventoryTransaction.objects.create(
            goods_code=item.product_code,
            transaction_type='cancel',
            quantity_change=+item.quantity,
            before_quantity=before_qty,
            after_quantity=mobile_inv.available_quantity,
            order=order,
            created_by='admin'
        )

    order.order_status = 'cancelled'
    order.cancelled_date = timezone.now()
    order.save()
```

### 3. ERP 재고 동기화

```python
def sync_inventory_from_erp():
    """ERP 재고를 모바일 재고에 반영"""

    goods_list = Goods.objects.all()

    for goods in goods_list:
        mobile_inv, created = MobileInventory.objects.get_or_create(
            goods_code=goods.code
        )

        # ERP 재고가 증가한 경우만 모바일 재고 증가
        erp_qty = goods.jaego
        current_total = mobile_inv.total_quantity

        if erp_qty > current_total:
            increase = erp_qty - current_total
            mobile_inv.available_quantity += increase
            mobile_inv.last_synced_from_erp = timezone.now()
            mobile_inv.save()

            # 이력 기록
            InventoryTransaction.objects.create(
                goods_code=goods.code,
                transaction_type='sync_from_erp',
                quantity_change=increase,
                before_quantity=current_total,
                after_quantity=erp_qty,
                created_by='system',
                memo=f'ERP 재고 동기화: {erp_qty}개'
            )
```

---

## 🎨 Admin 페이지 설계

### 1. MobileInventory Admin

```python
@admin.register(MobileInventory)
class MobileInventoryAdmin(admin.ModelAdmin):
    list_display = [
        'goods_code', 'goods_name_display',
        'erp_quantity_display', 'available_quantity',
        'reserved_quantity', 'sold_quantity',
        'last_synced_from_erp'
    ]
    list_filter = ['last_synced_from_erp']
    search_fields = ['goods_code']
    actions = ['sync_from_erp', 'manual_adjust']

    def goods_name_display(self, obj):
        try:
            goods = Goods.objects.get(code=obj.goods_code)
            return goods.name
        except:
            return '-'

    def erp_quantity_display(self, obj):
        """ERP 재고와 비교"""
        erp_qty = obj.erp_quantity
        mobile_qty = obj.total_quantity

        if erp_qty > mobile_qty:
            color = 'green'
            icon = '⬆️'
        elif erp_qty < mobile_qty:
            color = 'red'
            icon = '⬇️'
        else:
            color = 'gray'
            icon = '='

        return format_html(
            '<span style="color: {};">{} ERP: {}개</span>',
            color, icon, erp_qty
        )
```

### 2. Order Admin 확장 (분할 뷰)

```python
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'order_source_display', 'customer_name',
        'total_amount', 'order_status', 'order_date'
    ]
    list_filter = ['order_source', 'order_status', 'order_date']

    def order_source_display(self, obj):
        """주문 출처 표시"""
        if obj.order_source == 'mobile':
            return format_html('<span style="color: blue;">📱 모바일</span>')
        else:
            return format_html('<span style="color: green;">☎️ 전화</span>')

    def changelist_view(self, request, extra_context=None):
        """주문 목록을 분할하여 표시"""
        extra_context = extra_context or {}

        # 모바일 주문 통계
        mobile_orders = Order.objects.filter(order_source='mobile')
        extra_context['mobile_count'] = mobile_orders.count()
        extra_context['mobile_total'] = mobile_orders.aggregate(
            total=Sum('final_amount')
        )['total'] or 0

        # ERP 주문 통계
        erp_orders = Order.objects.filter(order_source__startswith='erp')
        extra_context['erp_count'] = erp_orders.count()
        extra_context['erp_total'] = erp_orders.aggregate(
            total=Sum('final_amount')
        )['total'] or 0

        return super().changelist_view(request, extra_context=extra_context)
```

---

## 📊 통합 대시보드

### tire_data/templates/admin/order_dashboard.html

```html
<div class="dashboard-container">
    <div class="split-view">
        <!-- 모바일 주문 -->
        <div class="mobile-orders">
            <h2>📱 모바일 주문 ({{ mobile_count }}건)</h2>
            <p>총 매출: {{ mobile_total|floatformat:0|intcomma }}원</p>
            <table>
                <!-- 모바일 주문 목록 -->
            </table>
        </div>

        <!-- ERP 전화주문 -->
        <div class="erp-orders">
            <h2>☎️ ERP 전화주문 ({{ erp_count }}건)</h2>
            <p>총 매출: {{ erp_total|floatformat:0|intcomma }}원</p>
            <table>
                <!-- ERP 주문 목록 -->
            </table>
        </div>
    </div>

    <!-- 통합 통계 -->
    <div class="total-stats">
        <h2>📊 전체 통계</h2>
        <p>총 주문: {{ mobile_count|add:erp_count }}건</p>
        <p>총 매출: {{ mobile_total|add:erp_total|floatformat:0|intcomma }}원</p>
    </div>
</div>
```

---

## 🚀 구현 단계

### Phase 1: 기본 구조 (1-2일)
- [ ] MobileInventory 모델 생성
- [ ] InventoryTransaction 모델 생성
- [ ] Order 모델에 order_source 필드 추가
- [ ] 마이그레이션 생성 및 적용

### Phase 2: 재고 관리 로직 (2-3일)
- [ ] 주문 시 재고 차감 로직
- [ ] 취소/반품 시 재고 복구 로직
- [ ] ERP 재고 동기화 로직
- [ ] 재고 이력 자동 기록

### Phase 3: Admin 인터페이스 (1-2일)
- [ ] MobileInventoryAdmin 구현
- [ ] OrderAdmin 확장 (출처 구분)
- [ ] 재고 수동 조정 액션
- [ ] ERP 동기화 액션

### Phase 4: ERP 주문 Import (2-3일)
- [ ] ERP 전화주문 데이터 구조 파악
- [ ] Import API 또는 파일 업로드 기능
- [ ] 중복 방지 로직
- [ ] 자동 매핑 (고객코드, 상품코드)

### Phase 5: 통합 대시보드 (3-4일)
- [ ] 분할 뷰 템플릿 작성
- [ ] 실시간 통계 API
- [ ] 차트 및 그래프 (Chart.js)
- [ ] 필터링 및 검색

### Phase 6: 테스트 및 최적화 (2-3일)
- [ ] 단위 테스트 작성
- [ ] 통합 테스트
- [ ] 성능 최적화
- [ ] 문서화

**총 예상 시간: 2-3주**

---

## ⚠️ 주의사항

### 1. 재고 동기화 정책
- **ERP → 모바일**: 증가 시에만 반영 (입고)
- **모바일 → ERP**: 직접 반영 안 함 (ERP는 별도 관리)
- **주의**: 모바일에서 판매한 재고는 ERP에서 수동으로 처리 필요

### 2. 데이터 무결성
- 재고가 음수가 되지 않도록 검증
- 트랜잭션 처리로 동시성 문제 방지
- 이력 기록 누락 방지

### 3. 성능 고려
- 재고 조회 시 캐싱
- 대량 주문 시 bulk operation
- 인덱스 최적화

---

## 📝 API 설계

### 재고 조회
```
GET /api/inventory/{goods_code}/
Response:
{
    "goods_code": "M-CC2SUV-07",
    "goods_name": "미쉐린 크로스클라이메이트2 SUV",
    "erp_quantity": 100,
    "mobile_available": 80,
    "mobile_reserved": 10,
    "mobile_sold": 10
}
```

### 주문 생성
```
POST /api/orders/
Body:
{
    "customer_code": "C001",
    "items": [
        {"goods_code": "M-CC2SUV-07", "quantity": 4}
    ]
}
Response:
{
    "order_number": "MO-20251014-0001",
    "status": "success"
}
```

---

**작성일**: 2025-10-14
**작성자**: Claude Code
**문서 버전**: 1.0

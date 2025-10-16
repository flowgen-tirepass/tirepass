"""
주문 관리 Admin - 모바일 / ERP 주문 분리
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models_shopping import Order, OrderItem, Payment


# Proxy 모델 정의 (같은 Order 모델을 여러 Admin에서 사용하기 위함)
class MobileOrder(Order):
    """모바일 주문 Proxy 모델"""
    class Meta:
        proxy = True
        verbose_name = '모바일 주문'
        verbose_name_plural = 'A. 📊 판매 | 01. 모바일 주문'


class ERPPhoneOrder(Order):
    """ERP 전화주문 Proxy 모델"""
    class Meta:
        proxy = True
        verbose_name = 'ERP 전화주문'
        verbose_name_plural = 'A. 📊 판매 | 02. ERP 전화주문'


# Inline 클래스들 (BaseOrderAdmin에서 사용)
class OrderItemInline(admin.TabularInline):
    """주문 상세 인라인"""
    model = OrderItem
    extra = 0
    fields = ['product_code', 'product_name', 'brand', 'quantity', 'selected_year',
             'unit_price', 'total_discount_rate', 'discounted_price', 'final_price']
    readonly_fields = ['product_name', 'brand', 'unit_price', 'total_discount_rate',
                      'discounted_price', 'final_price']


class PaymentInline(admin.TabularInline):
    """결제 정보 인라인"""
    model = Payment
    extra = 0
    fields = ['payment_method', 'payment_amount', 'payment_status', 'payment_date',
             'transaction_id', 'pg_name']
    readonly_fields = ['payment_date']


class BaseOrderAdmin(admin.ModelAdmin):
    """주문 Admin 기본 클래스"""

    list_display = ['order_number', 'order_source_display', 'customer_code', 'customer_name',
                   'total_amount_display', 'final_amount_display', 'order_status_display',
                   'payment_status_display', 'order_date']
    list_filter = ['order_status', 'payment_status', 'order_date']
    search_fields = ['order_number', 'customer_code', 'customer_name', 'erp_order_number']
    ordering = ['-order_date']
    list_per_page = 50
    inlines = [OrderItemInline, PaymentInline]
    change_list_template = 'admin/order_changelist.html'

    fieldsets = (
        ('주문 정보', {
            'fields': ('order_number', 'customer_code', 'customer_name', 'order_date', 'order_source', 'erp_order_number')
        }),
        ('금액 정보', {
            'fields': ('total_amount', 'total_discount', 'final_amount')
        }),
        ('상태 정보', {
            'fields': ('order_status', 'payment_status', 'payment_method')
        }),
        ('배송 정보', {
            'fields': ('shipping_address', 'shipping_memo')
        }),
        ('처리 일시', {
            'fields': ('confirmed_date', 'shipped_date', 'delivered_date'),
            'classes': ('collapse',)
        }),
        ('취소/반품 정보', {
            'fields': ('cancelled_date', 'cancelled_reason', 'returned_date', 'returned_reason'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['order_date']
    actions = ['cancel_order', 'process_return']

    def save_model(self, request, obj, form, change):
        """주문 상태 변경 시 일시 자동 기록"""
        from django.utils import timezone

        if 'order_status' in form.changed_data:
            if obj.order_status == 'confirmed' and not obj.confirmed_date:
                obj.confirmed_date = timezone.now()
            elif obj.order_status == 'shipped' and not obj.shipped_date:
                obj.shipped_date = timezone.now()
            elif obj.order_status == 'delivered' and not obj.delivered_date:
                obj.delivered_date = timezone.now()
            elif obj.order_status == 'cancelled' and not obj.cancelled_date:
                obj.cancelled_date = timezone.now()
            elif obj.order_status == 'returned' and not obj.returned_date:
                obj.returned_date = timezone.now()

        super().save_model(request, obj, form, change)

    def cancel_order(self, request, queryset):
        """주문 취소 처리"""
        from django.utils import timezone
        from django.contrib import messages

        updated_count = 0
        for order in queryset:
            if order.order_status in ['pending', 'confirmed']:
                order.order_status = 'cancelled'
                order.cancelled_date = timezone.now()
                if not order.cancelled_reason:
                    order.cancelled_reason = '관리자에 의한 주문 취소'
                order.save()
                updated_count += 1

        if updated_count > 0:
            self.message_user(request, f'{updated_count}개 주문이 취소되었습니다.', messages.SUCCESS)
        else:
            self.message_user(request, '취소 가능한 주문이 없습니다. (주문대기 또는 주문확인 상태만 취소 가능)', messages.WARNING)

    cancel_order.short_description = '선택된 주문 취소'

    def process_return(self, request, queryset):
        """반품 처리"""
        from django.utils import timezone
        from django.contrib import messages

        updated_count = 0
        for order in queryset:
            if order.order_status == 'delivered':
                order.order_status = 'returned'
                order.returned_date = timezone.now()
                order.payment_status = 'refunded'
                if not order.returned_reason:
                    order.returned_reason = '관리자에 의한 반품 처리'
                order.save()
                updated_count += 1

        if updated_count > 0:
            self.message_user(request, f'{updated_count}개 주문이 반품 처리되었습니다.', messages.SUCCESS)
        else:
            self.message_user(request, '반품 가능한 주문이 없습니다. (배송완료 상태만 반품 가능)', messages.WARNING)

    process_return.short_description = '선택된 주문 반품 처리'

    def order_source_display(self, obj):
        """주문 출처 표시"""
        if obj.order_source == 'mobile':
            return format_html('<span style="color: blue; font-weight: bold;">📱 모바일</span>')
        elif obj.order_source == 'erp_phone':
            return format_html('<span style="color: green; font-weight: bold;">☎️ 전화주문</span>')
        elif obj.order_source == 'erp_import':
            return format_html('<span style="color: gray;">✏️ 수동입력</span>')
        return obj.get_order_source_display()
    order_source_display.short_description = '주문출처'
    order_source_display.admin_order_field = 'order_source'

    def total_amount_display(self, obj):
        """총 주문금액 표시 (천단위 구분)"""
        from django.contrib.humanize.templatetags.humanize import intcomma
        return format_html(
            '<strong>{}원</strong>',
            intcomma(int(obj.total_amount))
        )
    total_amount_display.short_description = '총 주문금액'
    total_amount_display.admin_order_field = 'total_amount'

    def final_amount_display(self, obj):
        """최종 결제금액 표시 (천단위 구분)"""
        from django.contrib.humanize.templatetags.humanize import intcomma
        return format_html(
            '<strong style="color: #2563eb;">{}원</strong>',
            intcomma(int(obj.final_amount))
        )
    final_amount_display.short_description = '최종 결제금액'
    final_amount_display.admin_order_field = 'final_amount'

    def order_status_display(self, obj):
        """주문 상태 표시 (색상)"""
        colors = {
            'pending': '#f59e0b',      # 주문대기 (주황)
            'confirmed': '#10b981',    # 주문확인 (녹색)
            'preparing': '#3b82f6',    # 출고준비 (파랑)
            'shipped': '#8b5cf6',      # 배송중 (보라)
            'delivered': '#059669',    # 배송완료 (진한 녹색)
            'cancelled': '#ef4444',    # 주문취소 (빨강)
            'returned': '#dc2626',     # 반품완료 (진한 빨강)
        }
        color = colors.get(obj.order_status, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_order_status_display()
        )
    order_status_display.short_description = '주문상태'
    order_status_display.admin_order_field = 'order_status'

    def payment_status_display(self, obj):
        """결제 상태 표시 (색상)"""
        colors = {
            'unpaid': '#f59e0b',       # 미결제 (주황)
            'paid': '#10b981',         # 결제완료 (녹색)
            'refunded': '#ef4444',     # 환불완료 (빨강)
        }
        color = colors.get(obj.payment_status, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_display.short_description = '결제상태'
    payment_status_display.admin_order_field = 'payment_status'

    def changelist_view(self, request, extra_context=None):
        """합계 정보 추가"""
        extra_context = extra_context or {}

        # 현재 필터링된 queryset
        queryset = self.get_queryset(request)

        # 합계 계산
        aggregates = queryset.aggregate(
            total_count=Count('id'),
            total_amount_sum=Sum('total_amount'),
            final_amount_sum=Sum('final_amount'),
        )

        # int()로 변환 (Decimal → int, intcomma 필터 호환)
        extra_context['total_count'] = aggregates['total_count'] or 0
        extra_context['total_amount_sum'] = int(aggregates['total_amount_sum'] or 0)
        extra_context['final_amount_sum'] = int(aggregates['final_amount_sum'] or 0)

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(MobileOrder)
class MobileOrderAdmin(BaseOrderAdmin):
    """모바일 주문 관리 (order_source='mobile')"""

    def get_queryset(self, request):
        """모바일 주문만 표시"""
        qs = super().get_queryset(request)
        return qs.filter(order_source='mobile')


@admin.register(ERPPhoneOrder)
class ERPPhoneOrderAdmin(BaseOrderAdmin):
    """ERP 전화주문 관리 (order_source='erp_phone')"""

    def get_queryset(self, request):
        """ERP 전화주문만 표시"""
        qs = super().get_queryset(request)
        return qs.filter(order_source='erp_phone')

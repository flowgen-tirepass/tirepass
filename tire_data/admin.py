from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
import re
from .models import (
    Goods, CustomersFull, Customers, YearAllocation, BrandGroup,
    BrandGroupPattern, CustomerDiscount, DiscountHistory,
    CustomerProductDiscount, ShoppingCart, Order, OrderItem, Payment
)

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'bun1', 'display_jaego', 'display_fixp']
    list_filter = ['bun1']
    search_fields = ['code', 'name', 'bun1']
    readonly_fields = ['code']  # 상품코드는 읽기 전용
    list_per_page = 50

    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'bun1')
        }),
        ('재고 및 가격', {
            'fields': ('jaego', 'fixp')
        }),
        ('시스템 정보', {
            'fields': (),
            'classes': ('collapse',)
        }),
    )

    def display_jaego(self, obj):
        """재고수량을 정수로 표시 (천단위 콤마 포함)"""
        if obj.jaego is not None:
            return "{:,.0f}".format(float(obj.jaego))
        return "0"
    display_jaego.short_description = '재고수량'
    display_jaego.admin_order_field = 'jaego'

    def display_fixp(self, obj):
        """고정가격을 정수로 표시 (천단위 콤마 포함)"""
        if obj.fixp is not None:
            return "{:,.0f}".format(float(obj.fixp))
        return "0"
    display_fixp.short_description = '고정가격'
    display_fixp.admin_order_field = 'fixp'

    def get_search_results(self, request, queryset, search_term):
        """
        커스텀 검색: 숫자만 입력하면 타이어 사이즈 패턴으로 검색
        예: 2055516 -> 205/55R16, 205/55/16, 205-55-16 등
        """
        use_distinct = False

        if search_term:
            # 숫자만 추출
            numeric_only = re.sub(r'[^0-9]', '', search_term)

            # 숫자가 6자리 이상이면 타이어 사이즈 패턴으로 검색
            if len(numeric_only) >= 6:
                # 타이어 사이즈 패턴 생성
                width = numeric_only[:3]
                aspect = numeric_only[3:5]

                # 나머지 숫자를 인치로 사용
                if len(numeric_only) >= 7:
                    rim = numeric_only[5:7]
                else:
                    rim = numeric_only[5:]

                # 다양한 패턴으로 검색
                patterns = [
                    f"{width}/{aspect}R{rim}",
                    f"{width}/{aspect}/{rim}",
                    f"{width}-{aspect}-{rim}",
                    f"{width} {aspect} {rim}",
                    f"{width}/{aspect}r{rim}",  # 소문자 r
                ]

                # Q 객체로 OR 검색 (패턴 검색 + 기본 필드 검색)
                q_objects = Q()
                for pattern in patterns:
                    q_objects |= Q(name__icontains=pattern)

                # 기본 검색 필드도 추가 (code, name, bun1)
                q_objects |= Q(code__icontains=search_term)
                q_objects |= Q(name__icontains=search_term)
                q_objects |= Q(bun1__icontains=search_term)

                queryset = queryset.filter(q_objects)
                use_distinct = True
            else:
                # 일반 검색 (6자리 미만)
                queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        return queryset, use_distinct

@admin.register(CustomersFull)
class CustomersFullAdmin(admin.ModelAdmin):
    """ERP 전체 고객 목록 (읽기 전용)"""
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'enno', 'last_sync']
    search_fields = ['code', 'name', 'rep', 'enno']
    ordering = ['code']
    list_per_page = 50

    def has_add_permission(self, request):
        """추가 불가 (ERP에서만)"""
        return False

    def has_delete_permission(self, request, obj=None):
        """삭제 불가 (ERP에서만)"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 불가 (ERP에서만)"""
        return False

@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    """모바일 회원가입 고객"""
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'enno', 'is_registered', 'product_discount_count']
    list_filter = ['is_registered', 'must_change_password']
    search_fields = ['code', 'name', 'rep', 'enno']
    ordering = ['code']
    list_per_page = 50
    readonly_fields = ['code']
    fields = ['code', 'name', 'rep', 'tel1', 'tel3', 'enno', 'is_registered', 'must_change_password']

    def product_discount_count(self, obj):
        """개별 상품 할인 개수"""
        count = CustomerProductDiscount.objects.filter(
            customer_code=obj.code, is_active=True
        ).count()
        if count > 0:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:tire_data_customerproductdiscount_changelist') + f'?customer_code={obj.code}'
            return format_html('<a href="{}">{} 개</a>', url, count)
        return '0 개'
    product_discount_count.short_description = '개별 할인 상품'

class BrandGroupPatternInline(admin.TabularInline):
    """브랜드 그룹에 패턴을 인라인으로 추가/편집"""
    model = BrandGroupPattern
    extra = 1
    fields = ['pattern']
    verbose_name = '패턴'
    verbose_name_plural = '패턴 목록'

@admin.register(BrandGroup)
class BrandGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'group_name', 'group_order', 'pattern_count', 'is_active', 'created_at']
    list_filter = ['brand', 'is_active']
    list_editable = ['group_order', 'is_active']
    search_fields = ['brand', 'group_name', 'description']
    ordering = ['brand', 'group_order', 'group_name']
    list_per_page = 50
    inlines = [BrandGroupPatternInline]

    # autocomplete 지원
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    fieldsets = (
        ('기본 정보', {
            'fields': ('brand', 'group_name', 'group_order', 'description')
        }),
        ('상태', {
            'fields': ('is_active',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def pattern_count(self, obj):
        return obj.patterns.count()
    pattern_count.short_description = '패턴 수'

@admin.register(BrandGroupPattern)
class BrandGroupPatternAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_brand', 'get_group_name', 'pattern', 'created_at']
    list_filter = ['group__brand', 'group__group_name']
    search_fields = ['pattern', 'group__brand', 'group__group_name']
    ordering = ['group__brand', 'group__group_name', 'pattern']
    list_per_page = 50

    def get_brand(self, obj):
        return obj.group.brand
    get_brand.short_description = '브랜드'

    def get_group_name(self, obj):
        return obj.group.group_name
    get_group_name.short_description = '그룹명'

@admin.register(CustomerDiscount)
class CustomerDiscountAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'get_customer_name', 'brand', 'get_group_name', 'discount_rate', 'priority', 'date_range', 'is_active', 'is_valid_status']
    list_filter = ['is_active', 'brand', 'group__brand', 'group__group_name']
    list_editable = ['discount_rate', 'priority', 'is_active']
    search_fields = ['customer_code', 'brand', 'group__group_name', 'memo']
    ordering = ['customer_code', 'brand', '-priority']
    list_per_page = 50
    autocomplete_fields = ['group']

    fieldsets = (
        ('고객 및 브랜드', {
            'fields': ('customer_code', 'brand', 'group')
        }),
        ('할인 설정', {
            'fields': ('discount_rate', 'priority', 'start_date', 'end_date')
        }),
        ('메모 및 상태', {
            'fields': ('memo', 'is_active')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def get_customer_name(self, obj):
        try:
            customer = Customers.objects.get(code=obj.customer_code)
            return customer.name
        except Customers.DoesNotExist:
            return '-'
    get_customer_name.short_description = '고객명'

    def get_group_name(self, obj):
        return obj.group.group_name if obj.group else '전체'
    get_group_name.short_description = '그룹명'

    def date_range(self, obj):
        if obj.start_date and obj.end_date:
            return f"{obj.start_date} ~ {obj.end_date}"
        elif obj.start_date:
            return f"{obj.start_date} ~"
        elif obj.end_date:
            return f"~ {obj.end_date}"
        return "제한없음"
    date_range.short_description = '적용기간'

    def is_valid_status(self, obj):
        return obj.is_valid
    is_valid_status.short_description = '유효여부'
    is_valid_status.boolean = True

    def save_model(self, request, obj, form, change):
        """저장 시 생성자/수정자 자동 기록"""
        if not change:
            obj.created_by = request.user.username
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)

@admin.register(YearAllocation)
class YearAllocationAdmin(admin.ModelAdmin):
    list_display = ['goods_code', 'year_2025', 'year_2024', 'year_2023', 'year_2022', 'year_2021_before',
                   'year_2024_discount', 'year_2023_discount', 'year_2022_discount', 'year_2021_before_discount',
                   'total_allocated', 'last_updated']
    list_editable = ['year_2025', 'year_2024', 'year_2023', 'year_2022', 'year_2021_before',
                    'year_2024_discount', 'year_2023_discount', 'year_2022_discount', 'year_2021_before_discount']
    search_fields = ['goods_code']
    ordering = ['goods_code']
    readonly_fields = ['last_updated', 'total_allocated']
    list_per_page = 50

    fieldsets = (
        ('상품 정보', {
            'fields': ('goods_code',)
        }),
        ('연도별 재고 수량', {
            'fields': ('year_2025', 'year_2024', 'year_2023', 'year_2022', 'year_2021_before')
        }),
        ('DOT 할인율 (연도별)', {
            'fields': ('year_2024_discount', 'year_2023_discount', 'year_2022_discount', 'year_2021_before_discount'),
            'description': '과거 제조년도 상품에 대한 추가 할인율을 설정합니다.'
        }),
        ('시스템 정보', {
            'fields': ('total_allocated', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DiscountHistory)
class DiscountHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'product_code', 'brand', 'applied_discount', 'original_price', 'final_price', 'transaction_date']
    list_filter = ['brand', 'transaction_date']
    search_fields = ['customer_code', 'product_code', 'brand']
    ordering = ['-transaction_date']
    readonly_fields = ['transaction_date']
    list_per_page = 50
    date_hierarchy = 'transaction_date'


@admin.register(CustomerProductDiscount)
class CustomerProductDiscountAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'get_customer_name', 'product_code', 'get_product_name', 'brand',
                   'additional_discount_rate', 'priority', 'date_range', 'is_active', 'is_valid_status']
    list_filter = ['is_active', 'brand', 'customer_code']
    list_editable = ['additional_discount_rate', 'priority', 'is_active']
    search_fields = ['customer_code', 'product_code', 'brand', 'memo']
    ordering = ['customer_code', 'brand', 'product_code', '-priority']
    list_per_page = 50

    fieldsets = (
        ('고객 및 상품', {
            'fields': ('customer_code', 'product_code', 'brand')
        }),
        ('할인 설정', {
            'fields': ('additional_discount_rate', 'priority', 'start_date', 'end_date')
        }),
        ('메모 및 상태', {
            'fields': ('memo', 'is_active')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'brand']

    def get_customer_name(self, obj):
        return obj.customer_name if obj.customer_name else '-'
    get_customer_name.short_description = '고객명'

    def get_product_name(self, obj):
        return obj.product_name if obj.product_name else '-'
    get_product_name.short_description = '상품명'

    def date_range(self, obj):
        if obj.start_date and obj.end_date:
            return f"{obj.start_date} ~ {obj.end_date}"
        elif obj.start_date:
            return f"{obj.start_date} ~"
        elif obj.end_date:
            return f"~ {obj.end_date}"
        return "제한없음"
    date_range.short_description = '적용기간'

    def is_valid_status(self, obj):
        return obj.is_valid
    is_valid_status.short_description = '유효여부'
    is_valid_status.boolean = True

    def save_model(self, request, obj, form, change):
        """저장 시 생성자/수정자 자동 기록"""
        if not change:
            obj.created_by = request.user.username
        obj.updated_by = request.user.username
        super().save_model(request, obj, form, change)

# User 모델 커스터마이징
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['get_username', 'get_email', 'get_first_name', 'get_last_name', 'get_is_staff']

    # 필드셋 재정의 (상세 페이지 레이블 변경)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인정보', {'fields': ('first_name', 'last_name', 'email')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요한 일정', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    # 리스트 페이지 컬럼명 변경
    def get_username(self, obj):
        return obj.username
    get_username.short_description = '사업자등록번호'
    get_username.admin_order_field = 'username'

    def get_email(self, obj):
        return obj.email
    get_email.short_description = '이메일 주소'
    get_email.admin_order_field = 'email'

    def get_first_name(self, obj):
        return obj.first_name
    get_first_name.short_description = '대표자'
    get_first_name.admin_order_field = 'first_name'

    def get_last_name(self, obj):
        return obj.last_name
    get_last_name.short_description = '상호'
    get_last_name.admin_order_field = 'last_name'

    def get_is_staff(self, obj):
        return obj.is_staff
    get_is_staff.short_description = '스태프 권한'
    get_is_staff.boolean = True
    get_is_staff.admin_order_field = 'is_staff'

    # 폼 필드 레이블 재정의
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields['username'].label = '사업자등록번호'
        if 'first_name' in form.base_fields:
            form.base_fields['first_name'].label = '대표자'
        if 'last_name' in form.base_fields:
            form.base_fields['last_name'].label = '상호'
        if 'email' in form.base_fields:
            form.base_fields['email'].label = '이메일 주소'
        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].label = '스태프 권한'
        return form

# 기존 UserAdmin 등록 해제 후 커스텀 UserAdmin 등록
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# ============================================
# 쇼핑/주문 관련 Admin
# ============================================

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_code', 'get_customer_name', 'product_code', 'get_product_name',
                   'quantity', 'selected_year', 'final_price', 'created_at']
    list_filter = ['customer_code', 'selected_year', 'created_at']
    search_fields = ['customer_code', 'product_code']
    ordering = ['-created_at']
    list_per_page = 50

    def get_customer_name(self, obj):
        return obj.customer_name
    get_customer_name.short_description = '고객명'

    def get_product_name(self, obj):
        return obj.product_name
    get_product_name.short_description = '상품명'


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer_code', 'customer_name', 'total_amount',
                   'final_amount', 'order_status', 'payment_status', 'order_date']
    list_filter = ['order_status', 'payment_status', 'order_date']
    search_fields = ['order_number', 'customer_code', 'customer_name']
    ordering = ['-order_date']
    list_per_page = 50
    inlines = [OrderItemInline, PaymentInline]

    fieldsets = (
        ('주문 정보', {
            'fields': ('order_number', 'customer_code', 'customer_name', 'order_date')
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
    )
    readonly_fields = ['order_date']

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

        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_order_number', 'product_code', 'product_name', 'brand',
                   'quantity', 'selected_year', 'discounted_price', 'final_price']
    list_filter = ['brand', 'selected_year']
    search_fields = ['order__order_number', 'product_code', 'product_name']
    ordering = ['-created_at']
    list_per_page = 50

    def get_order_number(self, obj):
        return obj.order.order_number
    get_order_number.short_description = '주문번호'
    get_order_number.admin_order_field = 'order__order_number'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_order_number', 'payment_method', 'payment_amount',
                   'payment_status', 'payment_date', 'transaction_id']
    list_filter = ['payment_method', 'payment_status', 'payment_date']
    search_fields = ['order__order_number', 'transaction_id', 'pg_name']
    ordering = ['-created_at']
    list_per_page = 50

    fieldsets = (
        ('주문 정보', {
            'fields': ('order',)
        }),
        ('결제 정보', {
            'fields': ('payment_method', 'payment_amount', 'payment_status', 'payment_date')
        }),
        ('PG 정보', {
            'fields': ('transaction_id', 'pg_name')
        }),
        ('기타', {
            'fields': ('memo', 'cancelled_date'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['payment_date', 'cancelled_date']

    def get_order_number(self, obj):
        return obj.order.order_number
    get_order_number.short_description = '주문번호'
    get_order_number.admin_order_field = 'order__order_number'
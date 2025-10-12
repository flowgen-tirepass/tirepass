from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.html import format_html
import re
from .models import (
    Goods, CustomersFull, Customers, YearAllocation, BrandGroup,
    BrandGroupPattern, CustomerDiscount, DiscountHistory,
    CustomerProductDiscount, ShoppingCart, Order, OrderItem, Payment
)
from .erp_api_client import ERPAPIClient


class TireOnlyFilter(SimpleListFilter):
    """타이어만 필터"""
    title = '타이어 필터'
    parameter_name = 'tire_only'

    def lookups(self, request, model_admin):
        return [('on', '타이어만')]

    def queryset(self, request, queryset):
        return queryset


class StockOnlyFilter(SimpleListFilter):
    """재고있는 상품만 필터"""
    title = '재고 필터'
    parameter_name = 'stock_only'

    def lookups(self, request, model_admin):
        return [('on', '재고있음')]

    def queryset(self, request, queryset):
        return queryset


class TireBrandFilter(SimpleListFilter):
    """ERP 타이어 브랜드 필터 (우측 사이드바)"""
    title = '브랜드'
    parameter_name = 'brand'

    def lookups(self, request, model_admin):
        """브랜드 목록"""
        return [
            ('annaite', '안나이트'),
            ('bfg', 'BFG'),
            ('bridgestone', '브리지스톤'),
            ('continental', '콘티넨탈'),
            ('dunlop', '던롭'),
            ('goodyear', '굳이어'),
            ('hankook', '한국'),
            ('hilo', '하이로'),
            ('kumho', '금호'),
            ('michelin', '미쉐린'),
            ('nexen', '넥센'),
            ('pirelli', '피렐리'),
            ('yokohama', '요코하마'),
            ('maxxis', 'MAXXIS'),
            ('hifly', 'HIFLY'),
        ]

    def queryset(self, request, queryset):
        """
        이 메서드는 호출되지 않음 (changelist_view에서 직접 처리)
        하지만 필수 메서드이므로 구현
        """
        return queryset

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'bun1', 'display_jaego', 'display_fixp']
    list_filter = [TireOnlyFilter, StockOnlyFilter, TireBrandFilter]  # 커스텀 필터들
    search_fields = ['code', 'name', 'bun1']
    readonly_fields = ['code']  # 상품코드는 읽기 전용
    list_per_page = 50
    change_list_template = 'admin/goods_changelist.html'

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

    def get_queryset(self, request):
        """빈 queryset 반환 (ERP 데이터 사용)"""
        # Django admin의 기본 queryset을 사용하지 않음
        return Goods.objects.none()

    def is_tire_product(self, goods):
        """
        타이어 상품 판별 (BUN1 브랜드명 + CODE 접두사 기반)

        조건:
        1. BUN1에 타이어 브랜드명이 있어야 함
        2. CODE에 타이어 브랜드 접두사가 있어야 함
        → 두 조건 모두 만족해야 타이어로 판단
        """
        bun1 = (goods.get('bun1', '') or '').strip()
        code = (goods.get('code', '') or '').strip()

        # BUN1, CODE를 대문자로 변환 (영문 비교용)
        bun1_upper = bun1.upper()
        code_upper = code.upper()

        # 1. BUN1 브랜드명 체크 (한글 + 영문)
        tire_brands_bun1 = [
            '안나이트', 'ANNAITE',
            'BFG',
            '브리지스톤', 'BRIDGESTONE',
            '콘티넨탈', 'CONTINENTAL',
            '던롭', 'DUNLOP',
            '굳이어', 'GOODYEAR',
            '한국', 'HANKOOK',
            '하이로', 'HILO',
            '금호', 'KUMHO',
            '미쉐린', 'MICHELIN',
            '넥센', 'NEXEN',
            '피렐리', 'PIRELLI',
            '요코하마', 'YOKOHAMA',
            'MAXXIS', '맥시스',
            'HIFLY', '하이플라이'
        ]

        # BUN1에 브랜드명이 있는지 확인 (한글은 원본, 영문은 대문자 비교)
        has_tire_brand = False
        for brand in tire_brands_bun1:
            if brand.isupper():  # 영문은 대문자 비교
                if brand in bun1_upper:
                    has_tire_brand = True
                    break
            else:  # 한글은 원본 비교
                if brand in bun1:
                    has_tire_brand = True
                    break

        # 2. CODE 접두사 체크
        tire_code_prefixes = [
            'BFG-', 'BS-', 'C-', 'CT-', 'D-', 'G-', 'H-',
            'HIFLY-', 'HILO-', 'K-', 'M-', 'MAXXIS-', 'N-', 'P-'
        ]

        has_tire_code = any(code_upper.startswith(prefix) for prefix in tire_code_prefixes)

        # 3. 두 조건 모두 만족해야 타이어
        return has_tire_brand and has_tire_code

    def get_queryset(self, request):
        """
        Django admin이 데이터베이스 쿼리를 하지 않도록 빈 queryset 반환
        실제 데이터는 changelist_view에서 ERP API로 가져옴
        """
        return Goods.objects.none()

    def changelist_view(self, request, extra_context=None):
        """ERP 실시간 데이터로 완전 교체"""
        import logging
        logger = logging.getLogger(__name__)

        extra_context = extra_context or {}

        # 페이지네이션 파라미터
        page = int(request.GET.get('p', 1))
        per_page = 50
        offset = (page - 1) * per_page

        # 검색어 및 필터
        search_term = request.GET.get('q', '')
        filter_tire_only = request.GET.get('tire_only', '')
        filter_stock_only = request.GET.get('stock_only', '')
        filter_brand = request.GET.get('brand', '')  # 우측 사이드바 브랜드 필터

        logger.info(f"=== GoodsAdmin changelist_view ===")
        logger.info(f"검색어: '{search_term}'")
        logger.info(f"타이어 필터: '{filter_tire_only}' (타입: {type(filter_tire_only).__name__})")
        logger.info(f"재고 필터: '{filter_stock_only}' (타입: {type(filter_stock_only).__name__})")
        logger.info(f"브랜드 필터: '{filter_brand}'")

        # 필터 적용 여부 확인
        has_filter = (filter_tire_only == 'on' or filter_stock_only == 'on' or filter_brand)
        logger.info(f"필터 적용 여부: {has_filter}")

        # ERP API에서 실시간 데이터 조회
        if has_filter:
            # 필터 사용 시: 데이터를 가져와서 필터링 (타임아웃 방지)
            fetch_limit = 100  # 500→100으로 축소 (타임아웃 방지)
            logger.info(f"필터 모드: {fetch_limit}개 로드")
            erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=fetch_limit, search=search_term)
            erp_goods_count = ERPAPIClient.get_goods_count()
            logger.info(f"ERP 응답: {len(erp_goods_list)}개 상품, 전체: {erp_goods_count}")
        elif search_term:
            # 검색만 사용 시: 검색 결과를 페이지네이션
            logger.info(f"검색 모드: '{search_term}' (offset={offset}, limit={per_page})")
            erp_goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=per_page, search=search_term)
            # 검색 결과가 limit만큼 반환되면 더 많은 결과가 있을 수 있음
            if len(erp_goods_list) == per_page:
                erp_goods_count = 9999  # 충분히 큰 숫자 (페이지네이션 가능하게)
            else:
                erp_goods_count = offset + len(erp_goods_list)
            logger.info(f"검색 결과: {len(erp_goods_list)}개 상품 (현재 페이지)")
        else:
            # 일반 조회: 기본 페이지네이션
            logger.info(f"일반 조회 모드 (offset={offset}, limit={per_page})")
            erp_goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=per_page)
            erp_goods_count = ERPAPIClient.get_goods_count()
            logger.info(f"ERP 응답: {len(erp_goods_list)}개 상품, 전체: {erp_goods_count}")

        # 필터 적용 전 원본 개수
        original_count = len(erp_goods_list)

        # 클라이언트 사이드 필터 적용
        filtered_goods = erp_goods_list

        if filter_tire_only == 'on':
            # 타이어 상품만 필터링
            before_filter = len(filtered_goods)

            # 디버깅: 첫 3개 상품의 BUN1, CODE 값 확인
            if len(filtered_goods) > 0:
                logger.info(f"필터 전 샘플 (처음 3개):")
                for i, g in enumerate(filtered_goods[:3]):
                    logger.info(f"  [{i+1}] CODE: {g.get('code', 'N/A')}, BUN1: {g.get('bun1', 'N/A')}, NAME: {g.get('name', 'N/A')[:30]}")

            filtered_goods = [g for g in filtered_goods if self.is_tire_product(g)]
            logger.info(f"✓ 타이어 필터 적용: {before_filter} → {len(filtered_goods)}")

            if len(filtered_goods) > 0:
                sample = filtered_goods[0]
                logger.info(f"  타이어 샘플: CODE={sample.get('code', 'N/A')}, BUN1={sample.get('bun1', 'N/A')}, NAME={sample.get('name', 'N/A')[:30]}")

        if filter_stock_only == 'on':
            # 재고가 있는 상품만 필터링
            before_filter = len(filtered_goods)

            # 첫 3개 상품의 재고 값 확인 (디버깅)
            if len(filtered_goods) > 0:
                for i, g in enumerate(filtered_goods[:3]):
                    jaego_value = g.get('jaego', 0)
                    logger.info(f"  상품{i+1} 재고값: '{jaego_value}' (타입: {type(jaego_value).__name__})")

            # 재고 필터링 (문자열도 고려)
            def has_stock(goods):
                jaego = goods.get('jaego', 0)
                try:
                    return float(jaego) > 0
                except (ValueError, TypeError):
                    return False

            filtered_goods = [g for g in filtered_goods if has_stock(g)]
            logger.info(f"✓ 재고 필터 적용: {before_filter} → {len(filtered_goods)}")

            if len(filtered_goods) > 0:
                logger.info(f"  재고 샘플: {filtered_goods[0].get('name', 'N/A')} (재고: {filtered_goods[0].get('jaego', 0)})")

        if filter_brand:
            # 브랜드 필터링 (우측 사이드바 필터)
            before_filter = len(filtered_goods)

            # 브랜드 매핑 (파라미터 → 검색 키워드)
            brand_mapping = {
                'annaite': ['안나이트', 'ANNAITE'],
                'bfg': ['BFG'],
                'bridgestone': ['브리지스톤', 'BRIDGESTONE'],
                'continental': ['콘티넨탈', 'CONTINENTAL'],
                'dunlop': ['던롭', 'DUNLOP'],
                'goodyear': ['굳이어', 'GOODYEAR'],
                'hankook': ['한국', 'HANKOOK'],
                'hilo': ['하이로', 'HILO'],
                'kumho': ['금호', 'KUMHO'],
                'michelin': ['미쉐린', 'MICHELIN'],
                'nexen': ['넥센', 'NEXEN'],
                'pirelli': ['피렐리', 'PIRELLI'],
                'yokohama': ['요코하마', 'YOKOHAMA'],
                'maxxis': ['맥시스', 'MAXXIS'],
                'hifly': ['하이플라이', 'HIFLY'],
            }

            brand_keywords = brand_mapping.get(filter_brand.lower(), [])
            if brand_keywords:
                def matches_brand(goods):
                    bun1 = (goods.get('bun1', '') or '').strip()
                    bun1_upper = bun1.upper()
                    for keyword in brand_keywords:
                        if keyword.isupper():  # 영문은 대문자 비교
                            if keyword in bun1_upper:
                                return True
                        else:  # 한글은 원본 비교
                            if keyword in bun1:
                                return True
                    return False

                filtered_goods = [g for g in filtered_goods if matches_brand(g)]
                logger.info(f"✓ 브랜드 필터 적용 ({filter_brand}): {before_filter} → {len(filtered_goods)}")

                if len(filtered_goods) > 0:
                    logger.info(f"  브랜드 샘플: BUN1={filtered_goods[0].get('bun1', 'N/A')}, NAME={filtered_goods[0].get('name', 'N/A')[:30]}")

        # 필터 적용 후 최종 결과
        erp_goods_list = filtered_goods
        filtered_count = len(erp_goods_list)

        # 페이지네이션 정보
        if has_filter:
            # 필터 사용 시: 전체 결과 표시
            total_pages = 1
            has_previous = False
            has_next = False
            display_count = filtered_count
        else:
            # 일반 조회: 기본 페이지네이션
            total_pages = (erp_goods_count + per_page - 1) // per_page
            has_previous = page > 1
            has_next = page < total_pages
            display_count = erp_goods_count

        # 컨텍스트에 ERP 데이터 추가
        extra_context['erp_goods_count'] = display_count
        extra_context['erp_goods_list'] = erp_goods_list
        extra_context['page_num'] = page
        extra_context['total_pages'] = total_pages
        extra_context['has_previous'] = has_previous
        extra_context['has_next'] = has_next
        extra_context['search_term'] = search_term
        extra_context['filter_tire_only'] = filter_tire_only
        extra_context['filter_stock_only'] = filter_stock_only
        extra_context['filter_brand'] = filter_brand

        # 필터 정보 추가
        extra_context['original_count'] = original_count if has_filter else erp_goods_count
        extra_context['filtered_count'] = filtered_count if has_filter else None
        extra_context['has_filter'] = has_filter

        # tire_only, stock_only, brand를 SimpleListFilter로 등록했으므로
        # Django admin이 이제 이 파라미터들을 인식하고 리다이렉트하지 않음
        return super().changelist_view(request, extra_context=extra_context)

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
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'tel4', 'enno', 'last_sync']
    search_fields = ['code', 'name', 'rep', 'enno', 'address1']
    ordering = ['code']
    list_per_page = 50

    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'rep')
        }),
        ('연락처', {
            'fields': ('tel1', 'tel3', 'tel4')
        }),
        ('사업자 정보', {
            'fields': ('enno', 'address1')
        }),
        ('시스템 정보', {
            'fields': ('last_sync',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['code', 'name', 'rep', 'tel1', 'tel3', 'tel4', 'enno', 'address1', 'last_sync']

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
from django.contrib import admin
from django.contrib.admin import SimpleListFilter, helpers
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.html import format_html
from django.shortcuts import render, redirect
import re
from .models import (
    Goods, GoodsDisplayName, ExcludedGoods, CustomersFull, Customers, PaymentMethod, YearAllocation, BrandGroup,
    BrandGroupPattern, CustomerDiscount, DiscountHistory,
    CustomerProductDiscount, ShoppingCart, Order, OrderItem, Payment,
    ShippingAddress, PerformanceCategory, PerformanceTag, GoodsPerformanceTag,
    ERPSnapshot, GoodsRealtimeSnapshot
)
from .erp_api_client import ERPAPIClient
from .forms import BulkDiscountForm


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
    search_fields = ['=code', 'code', 'name', 'bun1']  # =code: 정확히 일치, code: 포함
    readonly_fields = ['code']  # 상품코드는 읽기 전용
    list_per_page = 50
    change_list_template = 'admin/goods_changelist.html'
    actions = ['set_custom_discount']  # 할인율 일괄 적용 액션

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
        """MySQL 데이터베이스에서 상품 조회"""
        qs = super().get_queryset(request)
        return qs

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
            'ANNAITE-',  # 안나이트 추가!
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

        중요: none()을 사용하되 model 정보는 유지
        """
        qs = Goods.objects.none()
        # model 정보가 확실히 설정되도록 보장
        qs.model = Goods
        return qs

    def changelist_view(self, request, extra_context=None):
        """ERP 실시간 데이터로 완전 교체"""
        import logging
        logger = logging.getLogger(__name__)

        # 디버깅: 요청 메서드 로그
        logger.info(f"🔍 changelist_view - Method: {request.method}, POST data: {dict(request.POST)}")

        # POST 요청이고 action이 있으면 먼저 처리
        if request.method == 'POST' and 'action' in request.POST:
            action = request.POST.get('action')
            logger.info(f"✅ Action detected: {action}")
            if action:  # action이 빈 문자열이 아닌 경우
                # action 메서드 찾기
                func = getattr(self, action, None)
                logger.info(f"🔧 Action function: {func}")
                if func:
                    # queryset은 사용하지 않으므로 None 전달
                    logger.info(f"▶️ Executing action: {action}")
                    response = func(request, None)
                    logger.info(f"📤 Action response: {response}")
                    if response:
                        return response
                else:
                    logger.warning(f"⚠️ Action function not found: {action}")
            else:
                logger.warning("⚠️ Action is empty string")
        else:
            if request.method == 'POST':
                logger.warning("⚠️ POST request but no action in POST data")
            else:
                logger.info("ℹ️ GET request (normal page view)")

        extra_context = extra_context or {}

        # 페이지네이션 파라미터
        page = int(request.GET.get('p', 1))
        per_page = 50
        offset = (page - 1) * per_page

        # 제외 목록 조회 (ERP 동기화 제외 상품)
        excluded_codes = set(ExcludedGoods.objects.values_list('code', flat=True))
        if excluded_codes:
            logger.info(f"⚠️  제외 목록: {len(excluded_codes)}개 상품 ({', '.join(list(excluded_codes)[:5])}{'...' if len(excluded_codes) > 5 else ''})")

        # 검색어 및 필터
        search_term = request.GET.get('q', '')
        filter_tire_only = request.GET.get('tire_only', '')
        filter_stock_only = request.GET.get('stock_only', '')
        filter_brand = request.GET.get('brand', '')  # 우측 사이드바 브랜드 필터

        # 검색어 변환: 숫자만 입력 시 타이어 사이즈로 변환
        enhanced_search_term = search_term
        search_patterns = []  # 복수 검색 패턴

        if search_term:
            numeric_only = re.sub(r'[^0-9]', '', search_term)

            # 순수 숫자 3자리 이상: 타이어 사이즈 패턴 생성
            if len(numeric_only) >= 3 and numeric_only == search_term:
                if len(numeric_only) == 3:
                    enhanced_search_term = f"{numeric_only}/"
                    search_patterns = [search_term, enhanced_search_term]
                elif len(numeric_only) == 4:
                    width = numeric_only[:3]
                    aspect_partial = numeric_only[3]
                    enhanced_search_term = f"{width}/{aspect_partial}"
                    search_patterns = [search_term, enhanced_search_term]
                elif len(numeric_only) == 5:
                    width = numeric_only[:3]
                    aspect_or_rim = numeric_only[3:5]
                    enhanced_search_term = f"{width}/{aspect_or_rim}"
                    search_patterns = [search_term, enhanced_search_term, f"{width}R{aspect_or_rim}"]
                elif len(numeric_only) >= 6:
                    width = numeric_only[:3]
                    aspect = numeric_only[3:5]
                    rim = numeric_only[5:7] if len(numeric_only) >= 7 else numeric_only[5:]
                    enhanced_search_term = f"{width}/{aspect}R{rim}"
                    search_patterns = [search_term, enhanced_search_term]

                logger.info(f"검색어 변환: '{search_term}' → '{enhanced_search_term}' (패턴: {search_patterns})")
            else:
                search_patterns = [search_term]
                logger.info(f"검색어 유지: '{search_term}'")

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
            # 필터 사용 시: 전체 상품 로드 후 필터링
            erp_goods_count = ERPAPIClient.get_goods_count()

            # 필터 사용 시: 전체 상품 로드 후 필터링 (ERP 검색 API 사용 안 함)
            fetch_limit = erp_goods_count
            if search_term:
                logger.info(f"검색 + 필터 모드: 전체 {fetch_limit}개 로드, 검색어: '{enhanced_search_term}'")
            else:
                logger.info(f"필터 모드: 전체 {fetch_limit}개 로드")

            erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=fetch_limit)
            logger.info(f"ERP 응답: {len(erp_goods_list)}개 상품")

            # 제외 목록 필터링
            if excluded_codes:
                before_count = len(erp_goods_list)
                erp_goods_list = [g for g in erp_goods_list if g.get('code') not in excluded_codes]
                if before_count != len(erp_goods_list):
                    logger.info(f"제외 목록 필터링: {before_count}개 → {len(erp_goods_list)}개 ({before_count - len(erp_goods_list)}개 제외)")

            # ERP 응답 샘플 로그 (처음 3개)
            if len(erp_goods_list) > 0:
                logger.info(f"ERP 응답 샘플 (처음 3개):")
                for i, g in enumerate(erp_goods_list[:3]):
                    logger.info(f"  [{i+1}] CODE: {g.get('code', 'N/A')}, BUN1: {g.get('bun1', 'N/A')}, NAME: {g.get('name', 'N/A')[:50]}")

                # 브랜드 필터 사용 시: 해당 브랜드 상품이 몇 개나 있는지 확인
                if filter_brand:
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
                        'michelin': ['미쉐린', '미슐랭', 'MICHELIN'],
                        'nexen': ['넥센', 'NEXEN'],
                        'pirelli': ['피렐리', 'PIRELLI', 'P ZERO'],
                        'yokohama': ['요코하마', 'YOKOHAMA'],
                        'maxxis': ['맥시스', 'MAXXIS'],
                        'hifly': ['하이플라이', 'HIFLY'],
                    }
                    brand_keywords = brand_mapping.get(filter_brand.lower(), [])
                    brand_count = sum(1 for g in erp_goods_list if any(
                        (kw in (g.get('bun1', '') or '').upper() if kw.isupper() else kw in (g.get('bun1', '') or ''))
                        for kw in brand_keywords
                    ))
                    logger.info(f"🔍 {fetch_limit}개 중 BUN1에 {brand_keywords} 포함된 상품: {brand_count}개")

                    if brand_count > 0:
                        # 해당 브랜드 상품 샘플 보기
                        brand_samples = [g for g in erp_goods_list if any(
                            (kw in (g.get('bun1', '') or '').upper() if kw.isupper() else kw in (g.get('bun1', '') or ''))
                            for kw in brand_keywords
                        )][:5]
                        logger.info(f"  {filter_brand} 브랜드 샘플 (처음 5개):")
                        for i, g in enumerate(brand_samples):
                            logger.info(f"    [{i+1}] CODE: {g.get('code', 'N/A')}, BUN1: {g.get('bun1', 'N/A')}, NAME: {g.get('name', 'N/A')[:50]}")
            else:
                logger.warning(f"⚠️ ERP 응답 0개! 검색어: '{enhanced_search_term}', 브랜드 필터: {filter_brand}")
        elif search_term:
            # 검색만 사용 시: DB + ERP API 결합 검색
            logger.info(f"검색 모드: '{search_term}' (offset={offset}, limit={per_page})")

            # 1. 먼저 데이터베이스에서 검색 (정확한 코드 매칭 우선)
            db_goods_list = []
            from django.db.models import Q
            db_queryset = Goods.objects.filter(
                Q(code__iexact=search_term) |  # 정확한 코드 매칭
                Q(code__icontains=search_term) |  # 코드 포함
                Q(name__icontains=search_term) |  # 상품명 포함
                Q(bun1__icontains=search_term)  # 브랜드 포함
            )
            # 제외 목록 필터링
            if excluded_codes:
                db_queryset = db_queryset.exclude(code__in=excluded_codes)

            db_queryset = db_queryset[:per_page]

            for goods in db_queryset:
                db_goods_list.append({
                    'code': goods.code,
                    'name': goods.name,
                    'bun1': goods.bun1,
                    'jaego': float(goods.jaego) if goods.jaego else 0,
                    'fixp': int(goods.fixp) if goods.fixp else 0,
                })

            logger.info(f"DB 검색 결과: {len(db_goods_list)}개 상품")

            # 2. ERP API에서도 검색
            erp_goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=per_page, search=enhanced_search_term)
            logger.info(f"ERP 검색 결과: {len(erp_goods_list)}개 상품")

            # 제외 목록 필터링
            if excluded_codes:
                before_count = len(erp_goods_list)
                erp_goods_list = [g for g in erp_goods_list if g.get('code') not in excluded_codes]
                if before_count != len(erp_goods_list):
                    logger.info(f"제외 목록 필터링: {before_count}개 → {len(erp_goods_list)}개 ({before_count - len(erp_goods_list)}개 제외)")

            # 3. 두 결과 합치기 (DB 우선, 중복 제거)
            seen_codes = set()
            combined_list = []

            # DB 결과 먼저 추가
            for goods in db_goods_list:
                code = goods.get('code')
                if code and code not in seen_codes:
                    combined_list.append(goods)
                    seen_codes.add(code)

            # ERP 결과 추가 (중복 제외)
            for goods in erp_goods_list:
                code = goods.get('code')
                if code and code not in seen_codes:
                    combined_list.append(goods)
                    seen_codes.add(code)

            erp_goods_list = combined_list
            logger.info(f"통합 검색 결과: {len(erp_goods_list)}개 상품 (DB: {len(db_goods_list)}, ERP: {len(erp_goods_list) - len(db_goods_list)})")

            # 검색 결과가 limit만큼 반환되면 더 많은 결과가 있을 수 있음
            if len(erp_goods_list) >= per_page:
                erp_goods_count = 9999  # 충분히 큰 숫자 (페이지네이션 가능하게)
            else:
                erp_goods_count = offset + len(erp_goods_list)
        else:
            # 일반 조회: 기본 페이지네이션
            logger.info(f"일반 조회 모드 (offset={offset}, limit={per_page})")
            erp_goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=per_page)
            erp_goods_count = ERPAPIClient.get_goods_count()
            logger.info(f"ERP 응답: {len(erp_goods_list)}개 상품, 전체: {erp_goods_count}")

            # 제외 목록 필터링
            if excluded_codes:
                before_count = len(erp_goods_list)
                erp_goods_list = [g for g in erp_goods_list if g.get('code') not in excluded_codes]
                if before_count != len(erp_goods_list):
                    logger.info(f"제외 목록 필터링: {before_count}개 → {len(erp_goods_list)}개 ({before_count - len(erp_goods_list)}개 제외)")

        # 필터 적용 전 원본 개수
        original_count = len(erp_goods_list)

        # 클라이언트 사이드 필터 적용 (순서: 브랜드 → 타이어 → 재고)
        filtered_goods = erp_goods_list
        brand_filtered = False  # 브랜드 필터 적용 여부

        # 1. 브랜드 필터: BUN1 필드로 필터링 (타이어만)
        if filter_brand:
            before_filter = len(filtered_goods)

            # 브랜드 매핑 (파라미터 → BUN1/NAME 검색 키워드)
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
                'michelin': ['미쉐린', '미슐랭', 'MICHELIN'],
                'nexen': ['넥센', 'NEXEN'],
                'pirelli': ['피렐리', 'PIRELLI', 'P ZERO'],
                'yokohama': ['요코하마', 'YOKOHAMA'],
                'maxxis': ['맥시스', 'MAXXIS'],
                'hifly': ['하이플라이', 'HIFLY'],
            }

            brand_keywords = brand_mapping.get(filter_brand.lower(), [])
            logger.info(f"브랜드 필터 키워드: {brand_keywords}")

            # 브랜드별 코드 접두사 매핑 (인코딩 문제 대비)
            brand_code_prefixes = {
                'annaite': ['ANNAITE-'],
                'bfg': ['BFG-'],
                'bridgestone': ['BS-'],
                'continental': ['C-', 'CT-'],
                'dunlop': ['D-'],
                'goodyear': ['G-'],
                'hankook': ['H-'],
                'hilo': ['HILO-'],
                'kumho': ['K-'],
                'michelin': ['M-'],
                'nexen': ['N-'],
                'pirelli': ['P-'],
                'yokohama': ['Y-'],
                'maxxis': ['MAXXIS-'],
                'hifly': ['HIFLY-'],
            }

            brand_prefixes = brand_code_prefixes.get(filter_brand.lower(), [])

            if brand_keywords:
                def matches_brand_and_tire(goods):
                    # BUN1 + NAME 필드에서 브랜드 체크 (인코딩 문제 대비)
                    bun1 = (goods.get('bun1', '') or '').strip()
                    name = (goods.get('name', '') or '').strip()
                    bun1_upper = bun1.upper()
                    name_upper = name.upper()
                    code = (goods.get('code', '') or '').strip().upper()

                    # 키워드 매칭 (bun1, name에서 검색)
                    keyword_match = False
                    for keyword in brand_keywords:
                        if keyword.isupper():  # 영문은 대문자 비교
                            if keyword in bun1_upper or keyword in name_upper:
                                keyword_match = True
                                break
                        else:  # 한글은 원본 비교
                            if keyword in bun1 or keyword in name:
                                keyword_match = True
                                break

                    # 코드 접두사 매칭 (인코딩 문제 대비)
                    code_match = any(code.startswith(prefix) for prefix in brand_prefixes)

                    # 키워드 OR 코드 매칭 (mobile API와 동일한 로직)
                    brand_match = keyword_match or code_match

                    # 브랜드 매칭 안되면 False
                    if not brand_match:
                        return False

                    # 브랜드 매칭되면 타이어 상품인지 확인 (CODE 접두사)
                    tire_code_prefixes = [
                        'ANNAITE-', 'BFG-', 'BS-', 'C-', 'CT-', 'D-', 'G-', 'H-',
                        'HIFLY-', 'HILO-', 'K-', 'M-', 'MAXXIS-', 'N-', 'P-'
                    ]
                    return any(code.startswith(prefix) for prefix in tire_code_prefixes)

                filtered_goods = [g for g in filtered_goods if matches_brand_and_tire(g)]
                brand_filtered = True
                logger.info(f"✓ 브랜드 필터 (타이어만) 적용 ({filter_brand}): {before_filter} → {len(filtered_goods)}")

                if len(filtered_goods) > 0:
                    logger.info(f"  브랜드 샘플 (처음 3개):")
                    for i, g in enumerate(filtered_goods[:3]):
                        logger.info(f"    [{i+1}] CODE: {g.get('code', 'N/A')}, BUN1: {g.get('bun1', 'N/A')}, NAME: {g.get('name', 'N/A')[:50]}")
                else:
                    logger.warning(f"  ⚠️ 브랜드 필터 후 0개! 브랜드: {filter_brand}, 키워드: {brand_keywords}")

        # 2. 타이어 필터
        if filter_tire_only == 'on':
            before_filter = len(filtered_goods)

            # 브랜드 필터 적용 후: CODE만 확인 (BUN1은 이미 검증됨)
            # 브랜드 필터 없음: BUN1 + CODE 모두 확인
            if brand_filtered:
                # CODE 접두사만 확인
                tire_code_prefixes = [
                    'ANNAITE-', 'BFG-', 'BS-', 'C-', 'CT-', 'D-', 'G-', 'H-',
                    'HIFLY-', 'HILO-', 'K-', 'M-', 'MAXXIS-', 'N-', 'P-'
                ]
                def is_tire_by_code(goods):
                    code = (goods.get('code', '') or '').strip().upper()
                    return any(code.startswith(prefix) for prefix in tire_code_prefixes)

                filtered_goods = [g for g in filtered_goods if is_tire_by_code(g)]
                logger.info(f"✓ 타이어 필터 (브랜드 후, CODE만 검증): {before_filter} → {len(filtered_goods)}")
            else:
                # BUN1 + CODE 모두 확인
                filtered_goods = [g for g in filtered_goods if self.is_tire_product(g)]
                logger.info(f"✓ 타이어 필터 (BUN1+CODE 검증): {before_filter} → {len(filtered_goods)}")

            if len(filtered_goods) > 0:
                sample = filtered_goods[0]
                logger.info(f"  타이어 샘플: CODE={sample.get('code', 'N/A')}, BUN1={sample.get('bun1', 'N/A')}, NAME={sample.get('name', 'N/A')[:50]}")
            else:
                logger.warning(f"  ⚠️ 타이어 필터 후 0개!")

        # 3. 재고 필터
        if filter_stock_only == 'on':
            before_filter = len(filtered_goods)

            # 재고 필터링 (문자열도 고려)
            def has_stock(goods):
                jaego = goods.get('jaego', 0)
                try:
                    return float(jaego) > 0
                except (ValueError, TypeError):
                    return False

            filtered_goods = [g for g in filtered_goods if has_stock(g)]
            logger.info(f"✓ 재고 필터: {before_filter} → {len(filtered_goods)}")

        # 4. 검색어 필터 (필터 모드에서만)
        if search_term and has_filter:
            before_filter = len(filtered_goods)

            # 검색어로 필터링 (코드, 상품명) - 복수 패턴 지원
            patterns_to_use = search_patterns if search_patterns else [search_term]
            search_filtered = []

            # 디버깅: 검색 전 샘플 확인
            if before_filter > 0:
                logger.info(f"🔍 검색 전 샘플 (처음 5개):")
                for i, g in enumerate(filtered_goods[:5]):
                    logger.info(f"    [{i+1}] {g.get('code', 'N/A')} - {g.get('name', 'N/A')[:60]}")

            for goods in filtered_goods:
                code = (goods.get('code', '') or '').strip()
                name = (goods.get('name', '') or '').strip()

                # 모든 패턴 중 하나라도 매칭되면 포함
                matched = False
                for pattern in patterns_to_use:
                    if (pattern in code or
                        pattern in name or
                        pattern.upper() in name.upper()):
                        matched = True
                        break

                if matched:
                    search_filtered.append(goods)

            filtered_goods = search_filtered
            logger.info(f"✓ 검색어 필터 (패턴: {patterns_to_use}): {before_filter} → {len(filtered_goods)}")

            if len(filtered_goods) > 0:
                logger.info(f"  재고 샘플: {filtered_goods[0].get('name', 'N/A')} (재고: {filtered_goods[0].get('jaego', 0)})")

        # 필터 적용 후 최종 결과
        filtered_count = len(filtered_goods)

        # 페이지네이션 정보
        if has_filter:
            # 필터 사용 시: 페이지네이션 적용
            total_pages = (filtered_count + per_page - 1) // per_page
            has_previous = page > 1
            has_next = page < total_pages

            # 현재 페이지 결과만 추출
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            erp_goods_list = filtered_goods[start_index:end_index]

            display_count = filtered_count
            logger.info(f"📄 페이지네이션: {filtered_count}개 중 {start_index+1}~{min(end_index, filtered_count)}번째 표시 (페이지 {page}/{total_pages})")
        else:
            # 일반 조회: 기본 페이지네이션
            erp_goods_list = filtered_goods
            total_pages = (erp_goods_count + per_page - 1) // per_page
            has_previous = page > 1
            has_next = page < total_pages
            display_count = erp_goods_count

        # YearAllocation 데이터를 각 상품에 추가 (base_discount)
        goods_codes = [g.get('code') for g in erp_goods_list if g.get('code')]
        year_allocations_list = YearAllocation.objects.filter(goods_code__in=goods_codes)
        year_allocations = {ya.goods_code: ya for ya in year_allocations_list}

        # 각 상품에 base_discount 추가
        for goods in erp_goods_list:
            goods_code = goods.get('code')
            if goods_code and goods_code in year_allocations:
                goods['base_discount'] = float(year_allocations[goods_code].base_discount)
            else:
                goods['base_discount'] = 0.00

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

        # Django admin 템플릿이 필요로 하는 컨텍스트 명시적으로 추가
        extra_context.update({
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request),
            'has_delete_permission': self.has_delete_permission(request),
        })

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

    # ===== 할인율 일괄 적용 Admin Actions =====

    def set_custom_discount(self, request, queryset):
        """선택한 상품의 기본 할인율을 사용자 지정 값으로 설정"""
        from django.contrib import messages
        from decimal import Decimal

        # POST 데이터에서 선택된 상품 코드 추출
        selected_codes = request.POST.getlist('_selected_action')

        if not selected_codes:
            self.message_user(request, "선택된 상품이 없습니다.", messages.WARNING)
            return

        # GET 요청: 할인율 입력 폼 표시
        if 'apply' not in request.POST:
            # 선택된 상품 정보 가져오기
            products = []
            for code in selected_codes:
                try:
                    goods = Goods.objects.get(code=code)
                    products.append(goods)
                except Goods.DoesNotExist:
                    pass

            form = BulkDiscountForm()
            context = {
                'products': products,
                'form': form,
                'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
                'opts': self.model._meta,
                'site_title': admin.site.site_title,
                'site_header': admin.site.site_header,
            }
            return render(request, 'admin/bulk_discount.html', context)

        # POST 요청: 할인율 적용
        form = BulkDiscountForm(request.POST)
        if not form.is_valid():
            self.message_user(request, "입력한 할인율이 유효하지 않습니다.", messages.ERROR)
            return

        discount_rate = form.cleaned_data['discount_rate']
        updated_count = 0
        created_count = 0

        for goods_code in selected_codes:
            # YearAllocation 레코드 가져오기 또는 생성
            year_allocation, created = YearAllocation.objects.get_or_create(
                goods_code=goods_code,
                defaults={'base_discount': Decimal(str(discount_rate))}
            )

            if created:
                created_count += 1
            else:
                # 기존 레코드 업데이트
                year_allocation.base_discount = Decimal(str(discount_rate))
                year_allocation.save()
                updated_count += 1

        # 결과 메시지
        total = created_count + updated_count
        message_parts = []
        if created_count > 0:
            message_parts.append(f"{created_count}개 상품 할인율 신규 설정")
        if updated_count > 0:
            message_parts.append(f"{updated_count}개 상품 할인율 업데이트")

        message = f"{discount_rate}% 적용 완료: " + ", ".join(message_parts) + f" (총 {total}개)"
        self.message_user(request, message, messages.SUCCESS)

        # 상품 목록 페이지로 리다이렉트
        return redirect('admin:tire_data_goods_changelist')

    set_custom_discount.short_description = "할인율 일괄 적용"

# CustomersFull은 ERP의 customers 테이블을 참조하는데,
# 현재 데이터베이스에 해당 테이블이 없어서 임시로 비활성화
# ERP 동기화가 완료되면 다시 활성화할 수 있습니다.
# @admin.register(CustomersFull)
# class CustomersFullAdmin(admin.ModelAdmin):
#     """ERP 전체 고객 목록 (읽기 전용)"""
#     list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'tel4', 'enno', 'last_sync']
#     search_fields = ['code', 'name', 'rep', 'enno', 'address1']
#     ordering = ['code']
#     list_per_page = 50
#
#     fieldsets = (
#         ('기본 정보', {
#             'fields': ('code', 'name', 'rep')
#         }),
#         ('연락처', {
#             'fields': ('tel1', 'tel3', 'tel4')
#         }),
#         ('사업자 정보', {
#             'fields': ('enno', 'address1')
#         }),
#         ('시스템 정보', {
#             'fields': ('last_sync',),
#             'classes': ('collapse',)
#         }),
#     )
#     readonly_fields = ['code', 'name', 'rep', 'tel1', 'tel3', 'tel4', 'enno', 'address1', 'last_sync']
#
#     def has_add_permission(self, request):
#         """추가 불가 (ERP에서만)"""
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         """삭제 불가 (ERP에서만)"""
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         """수정 불가 (ERP에서만)"""
#         return False


@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    """모바일 회원가입 고객"""
    list_display = ['code', 'name', 'rep', 'tel1', 'tel3', 'enno', 'is_registered', 'shipping_count', 'product_discount_count']
    list_filter = ['is_registered', 'must_change_password']
    search_fields = ['=code', 'code', 'name', 'rep', '=enno', 'enno']  # =code: 정확히 일치, code: 포함
    ordering = ['code']
    list_per_page = 50
    readonly_fields = ['code', 'shipping_addresses_display']
    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'rep', 'tel1', 'tel3', 'enno')
        }),
        ('계정 상태', {
            'fields': ('is_registered', 'must_change_password')
        }),
        ('등록된 배송지', {
            'fields': ('shipping_addresses_display',),
            'classes': ('collapse',)
        }),
    )
    actions = ['sync_from_erp']

    def shipping_count(self, obj):
        """등록된 배송지 개수"""
        try:
            # ShippingAddress는 customer_code에 사업자번호(enno)를 사용
            if not obj.enno:
                return '❌ 0'

            count = ShippingAddress.objects.filter(customer_code=obj.enno).count()
            if count > 0:
                from django.urls import reverse
                from django.utils.html import format_html
                url = reverse('admin:tire_data_shippingaddress_changelist') + f'?customer_code={obj.enno}'
                return format_html('<a href="{}">✅ {} 개</a>', url, count)
            return '❌ 0'
        except Exception:
            return '-'
    shipping_count.short_description = '배송지'

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

    def shipping_addresses_display(self, obj):
        """등록된 배송지 목록 표시"""
        try:
            # ShippingAddress는 customer_code에 사업자번호(enno)를 사용
            if not obj.enno:
                return '사업자번호가 없어 배송지를 조회할 수 없습니다.'

            addresses = ShippingAddress.objects.filter(customer_code=obj.enno).order_by('-is_default', '-created_at')

            if not addresses.exists():
                return '등록된 배송지가 없습니다.'

            from django.urls import reverse
            from django.utils.html import format_html

            html = '<table style="width: 100%; border-collapse: collapse;">'
            html += '<thead><tr style="background: #f3f4f6;">'
            html += '<th style="padding: 8px; text-align: center; border: 1px solid #e5e7eb;">기본</th>'
            html += '<th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">수령인</th>'
            html += '<th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">주소</th>'
            html += '<th style="padding: 8px; text-align: left; border: 1px solid #e5e7eb;">전화번호</th>'
            html += '<th style="padding: 8px; text-align: center; border: 1px solid #e5e7eb;">관리</th>'
            html += '</tr></thead><tbody>'

            for address in addresses:
                url = reverse('admin:tire_data_shippingaddress_change', args=[address.id])
                html += '<tr>'
                html += f'<td style="padding: 8px; text-align: center; border: 1px solid #e5e7eb;">{"✅" if address.is_default else ""}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #e5e7eb;">{address.recipient_name}</td>'

                # 주소 (우편번호 포함)
                full_address = address.full_address
                if address.postal_code:
                    full_address = f'({address.postal_code}) {full_address}'
                html += f'<td style="padding: 8px; border: 1px solid #e5e7eb;">{full_address}</td>'

                html += f'<td style="padding: 8px; border: 1px solid #e5e7eb;">{address.phone_number}</td>'
                html += f'<td style="padding: 8px; text-align: center; border: 1px solid #e5e7eb;"><a href="{url}">수정</a></td>'
                html += '</tr>'

            html += '</tbody></table>'

            # 전체 배송지 목록 링크
            list_url = reverse('admin:tire_data_shippingaddress_changelist') + f'?customer_code={obj.enno}'
            html += f'<p style="margin-top: 10px;"><a href="{list_url}">전체 배송지 목록 보기 →</a></p>'

            return format_html(html)
        except Exception as e:
            return f'배송지 정보를 불러올 수 없습니다: {str(e)}'
    shipping_addresses_display.short_description = '등록된 배송지'

    @admin.action(description='ERP에서 고객 정보 동기화')
    def sync_from_erp(self, request, queryset):
        """선택한 고객들의 정보를 ERP에서 가져와서 업데이트"""
        from .erp_api_client import ERPAPIClient
        from django.contrib import messages

        success_count = 0
        error_count = 0

        for customer in queryset:
            try:
                # ERP API에서 고객 정보 조회
                erp_data = ERPAPIClient.get_customer_detail(customer.code)

                if not erp_data:
                    error_count += 1
                    messages.warning(request, f'고객 {customer.code}: ERP에서 데이터를 가져올 수 없습니다.')
                    continue

                # 고객 정보 업데이트
                customer.name = erp_data.get('NAME', customer.name)
                customer.rep = erp_data.get('REP', customer.rep)
                customer.tel1 = erp_data.get('TEL1', customer.tel1)
                customer.tel3 = erp_data.get('TEL3', customer.tel3)
                customer.enno = erp_data.get('ENNO', customer.enno)
                customer.save()

                success_count += 1

            except Exception as e:
                error_count += 1
                messages.error(request, f'고객 {customer.code}: 오류 - {str(e)}')

        # 결과 메시지
        if success_count > 0:
            messages.success(request, f'{success_count}개 고객 정보를 ERP에서 동기화했습니다.')
        if error_count > 0:
            messages.error(request, f'{error_count}개 고객 동기화 실패')

        # 주문의 customer_name도 업데이트
        if success_count > 0:
            try:
                updated_orders = 0
                for customer in queryset:
                    updated = Order.objects.filter(customer_code=customer.code).update(customer_name=customer.name)
                    updated_orders += updated

                if updated_orders > 0:
                    messages.info(request, f'관련 주문 {updated_orders}개의 고객명도 업데이트했습니다.')
            except Exception as e:
                messages.warning(request, f'주문 업데이트 중 오류: {str(e)}')


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """결제 수단 관리"""
    list_display = ['customer_code', 'customer_name', 'payment_type', 'masked_info', 'nickname', 'is_default', 'is_active', 'created_at']
    list_filter = ['payment_type', 'is_default', 'is_active', 'card_company', 'account_bank', 'created_at']
    search_fields = ['customer_code', 'card_company', 'account_bank', 'nickname']
    ordering = ['-created_at']
    list_per_page = 50
    readonly_fields = ['billing_key', 'card_last4', 'account_last4', 'created_at', 'updated_at']
    actions = ['make_active', 'make_inactive', 'set_as_default']

    fieldsets = (
        ('기본 정보', {
            'fields': ('customer_code', 'payment_type', 'nickname', 'is_default', 'is_active')
        }),
        ('카드 정보', {
            'fields': ('billing_key', 'card_company', 'card_last4', 'card_type'),
            'classes': ('collapse',)
        }),
        ('계좌 정보', {
            'fields': ('account_bank', 'account_number_encrypted', 'account_last4', 'account_holder'),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def customer_name(self, obj):
        """고객명 표시"""
        return obj.customer_name or '-'
    customer_name.short_description = '고객명'

    def has_add_permission(self, request):
        """Admin에서 직접 추가 불가 (모바일에서만)"""
        return False

    @admin.action(description='선택된 결제 수단 활성화')
    def make_active(self, request, queryset):
        """선택된 결제 수단을 활성화"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated}개 결제 수단이 활성화되었습니다.')

    @admin.action(description='선택된 결제 수단 비활성화')
    def make_inactive(self, request, queryset):
        """선택된 결제 수단을 비활성화"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated}개 결제 수단이 비활성화되었습니다.')

    @admin.action(description='기본 결제 수단으로 설정')
    def set_as_default(self, request, queryset):
        """선택된 결제 수단을 기본으로 설정 (1개만 선택 가능)"""
        if queryset.count() > 1:
            self.message_user(request, '기본 결제 수단은 1개만 선택해주세요.', level='error')
            return

        method = queryset.first()
        # 같은 고객의 다른 결제 수단을 기본에서 해제
        PaymentMethod.objects.filter(customer_code=method.customer_code, is_default=True).update(is_default=False)
        # 선택한 결제 수단을 기본으로 설정
        method.is_default = True
        method.save()
        self.message_user(request, f'{method.masked_info}를 기본 결제 수단으로 설정했습니다.')


class BrandGroupPatternInline(admin.TabularInline):
    """브랜드 그룹에 패턴을 인라인으로 추가/편집"""
    model = BrandGroupPattern
    extra = 1
    fields = ['pattern']
    verbose_name = '패턴'
    verbose_name_plural = '패턴 목록'

@admin.register(BrandGroup)
class BrandGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'group_name', 'group_order', 'pattern_count', 'pattern_preview', 'is_active', 'created_at']
    list_filter = ['brand', 'is_active']
    list_editable = ['group_order', 'is_active']
    search_fields = ['brand', 'group_name', 'description']  # 브랜드/그룹명은 정확한 일치보다 포함 검색이 유용
    ordering = ['brand', 'group_order', 'group_name']
    list_per_page = 50
    inlines = [BrandGroupPatternInline]
    actions = ['activate_groups', 'deactivate_groups', 'duplicate_group', 'apply_discount_to_all_customers']

    # autocomplete 지원
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    fieldsets = (
        ('기본 정보', {
            'fields': ('brand', 'group_name', 'group_order', 'description'),
            'description': '브랜드별로 타이어 시리즈를 그룹화합니다. 예: 피렐리 → P ZERO 시리즈'
        }),
        ('상태', {
            'fields': ('is_active',),
            'description': '비활성화하면 고객 할인 적용 시 이 그룹이 제외됩니다.'
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at', 'updated_at']

    def pattern_count(self, obj):
        """패턴 개수 표시"""
        count = obj.patterns.count()
        if count > 0:
            return format_html('<strong style="color: #2563eb;">{} 개</strong>', count)
        return format_html('<span style="color: #9ca3af;">0 개</span>')
    pattern_count.short_description = '패턴 수'

    def pattern_preview(self, obj):
        """패턴 미리보기 (처음 3개)"""
        patterns = obj.patterns.all()[:3]
        if patterns:
            pattern_names = [p.pattern for p in patterns]
            preview = ', '.join(pattern_names)
            total = obj.patterns.count()
            if total > 3:
                preview += f' 외 {total - 3}개'
            return format_html('<span style="color: #666; font-size: 12px;">{}</span>', preview)
        return format_html('<span style="color: #9ca3af;">-</span>')
    pattern_preview.short_description = '패턴 미리보기'

    def activate_groups(self, request, queryset):
        """선택한 그룹 활성화"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated}개 그룹을 활성화했습니다.', 'success')
    activate_groups.short_description = '선택한 그룹 활성화'

    def deactivate_groups(self, request, queryset):
        """선택한 그룹 비활성화"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated}개 그룹을 비활성화했습니다.', 'warning')
    deactivate_groups.short_description = '선택한 그룹 비활성화'

    def duplicate_group(self, request, queryset):
        """선택한 그룹 복제 (패턴 포함)"""
        if queryset.count() != 1:
            self.message_user(request, '하나의 그룹만 선택해주세요.', 'error')
            return

        original = queryset.first()
        # 새 그룹 생성
        new_group = BrandGroup.objects.create(
            brand=original.brand,
            group_name=f'{original.group_name} (복사본)',
            group_order=original.group_order + 1,
            description=original.description,
            is_active=False  # 복사본은 기본적으로 비활성
        )

        # 패턴 복사
        for pattern in original.patterns.all():
            BrandGroupPattern.objects.create(
                group=new_group,
                pattern=pattern.pattern
            )

        self.message_user(request, f'"{original.group_name}"을 복제했습니다. (패턴 {original.patterns.count()}개 포함)', 'success')
    duplicate_group.short_description = '선택한 그룹 복제 (패턴 포함)'

    def apply_discount_to_all_customers(self, request, queryset):
        """선택한 브랜드/그룹에 대해 전체 고객에게 할인율 일괄 적용"""
        from django.shortcuts import render, redirect
        from django.contrib import messages, admin as admin_module
        from django.urls import reverse
        from django.http import HttpResponseRedirect
        from decimal import Decimal

        # POST 요청인 경우: 폼 제출 처리
        if 'apply' in request.POST:
            # POST에서 선택된 그룹 ID 가져오기
            selected_ids = request.POST.getlist(admin_module.helpers.ACTION_CHECKBOX_NAME)
            if not selected_ids:
                self.message_user(request, '그룹을 먼저 선택해주세요.', messages.ERROR)
                return redirect(reverse('admin:tire_data_brandgroup_changelist'))

            # queryset 재구성
            queryset = BrandGroup.objects.filter(pk__in=selected_ids)

            discount_rate = request.POST.get('discount_rate')

            # 유효성 검증
            if not discount_rate:
                self.message_user(request, '할인율을 입력해주세요.', messages.ERROR)
                return redirect(reverse('admin:tire_data_brandgroup_changelist'))

            try:
                discount_rate = Decimal(discount_rate)
                if discount_rate < 0 or discount_rate > 100:
                    self.message_user(request, '할인율은 0~100 사이의 값이어야 합니다.', messages.ERROR)
                    return redirect(reverse('admin:tire_data_brandgroup_changelist'))
            except:
                self.message_user(request, '올바른 숫자를 입력해주세요.', messages.ERROR)
                return redirect(reverse('admin:tire_data_brandgroup_changelist'))

            # 활성 고객 목록 조회
            active_customers = Customers.objects.filter(is_registered=True)

            if active_customers.count() == 0:
                self.message_user(request, '활성 고객이 없습니다. 먼저 고객을 등록해주세요.', messages.WARNING)
                return redirect(reverse('admin:tire_data_brandgroup_changelist'))

            created_count = 0
            updated_count = 0
            skipped_count = 0

            # 각 선택된 그룹에 대해
            for group in queryset:
                # 각 활성 고객에 대해
                for customer in active_customers:
                    # customer.enno가 None이거나 빈 문자열인 경우 건너뜀
                    if not customer.enno:
                        continue

                    # 이미 존재하는지 확인
                    existing = CustomerDiscount.objects.filter(
                        customer_code=customer.enno,  # customer_code는 사업자번호(enno) 저장
                        brand=group.brand,
                        group=group
                    ).first()

                    if existing:
                        # 기존 할인율과 다르면 업데이트
                        if existing.discount_rate != discount_rate or not existing.is_active:
                            existing.discount_rate = discount_rate
                            existing.is_active = True
                            existing.updated_by = request.user.username
                            existing.save()
                            updated_count += 1
                        else:
                            skipped_count += 1
                    else:
                        # 신규 생성
                        CustomerDiscount.objects.create(
                            customer_code=customer.enno,
                            brand=group.brand,
                            group=group,
                            discount_rate=discount_rate,
                            priority=1,
                            is_active=True,
                            created_by=request.user.username,
                            updated_by=request.user.username
                        )
                        created_count += 1

            # 결과 메시지
            total = created_count + updated_count
            msg_parts = []
            if created_count > 0:
                msg_parts.append(f'신규 {created_count}건')
            if updated_count > 0:
                msg_parts.append(f'수정 {updated_count}건')
            if skipped_count > 0:
                msg_parts.append(f'건너뜀 {skipped_count}건')

            if total > 0:
                result_msg = f'{discount_rate}% 할인율 적용 완료: ' + ', '.join(msg_parts)
                self.message_user(request, result_msg, messages.SUCCESS)
            else:
                self.message_user(request, '적용된 할인율이 없습니다.', messages.WARNING)

            # changelist로 리다이렉트
            return redirect(reverse('admin:tire_data_brandgroup_changelist'))

        # 첫 번째 POST 요청: 중간 페이지 표시
        active_customers = Customers.objects.filter(is_registered=True)
        customer_count = active_customers.count()

        # 선택된 그룹 정보 (queryset을 list로 변환)
        selected_groups = list(queryset.values('id', 'brand', 'group_name'))

        # selected_action IDs 추출
        selected_ids = [str(group['id']) for group in selected_groups]

        context = {
            'title': '전체 고객에게 할인율 일괄 적용',
            'selected_groups': selected_groups,
            'selected_ids': selected_ids,  # ID 목록 추가
            'customer_count': customer_count,
            'opts': self.model._meta,
            'action_checkbox_name': admin_module.helpers.ACTION_CHECKBOX_NAME,
        }

        return render(request, 'admin/apply_discount_to_all.html', context)

    apply_discount_to_all_customers.short_description = '선택한 그룹의 할인율을 전체 고객에게 적용'

@admin.register(BrandGroupPattern)
class BrandGroupPatternAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_brand', 'get_group_name', 'pattern_badge', 'get_group_status', 'created_at']
    list_filter = ['group__brand', 'group__group_name', 'group__is_active']
    search_fields = ['pattern', 'group__brand', 'group__group_name']  # 패턴은 부분 검색이 유용
    ordering = ['group__brand', 'group__group_name', 'pattern']
    list_per_page = 100
    autocomplete_fields = ['group']
    actions = ['copy_patterns_to_group', 'delete_patterns']

    fieldsets = (
        ('그룹 선택', {
            'fields': ('group',),
            'description': '이 패턴이 속할 브랜드 그룹을 선택합니다.'
        }),
        ('패턴 정보', {
            'fields': ('pattern',),
            'description': '타이어 모델명의 일부분을 입력합니다. 예: "P ZERO", "PILOT SPORT"'
        }),
        ('시스템 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']

    def get_brand(self, obj):
        """브랜드 표시"""
        return format_html(
            '<strong style="color: #0ea5e9;">{}</strong>',
            obj.group.brand
        )
    get_brand.short_description = '브랜드'
    get_brand.admin_order_field = 'group__brand'

    def get_group_name(self, obj):
        """그룹명 표시"""
        return format_html(
            '<span style="color: #666;">{}</span>',
            obj.group.group_name
        )
    get_group_name.short_description = '그룹명'
    get_group_name.admin_order_field = 'group__group_name'

    def pattern_badge(self, obj):
        """패턴 뱃지 스타일 표시"""
        return format_html(
            '<span style="background: #f0f9ff; color: #0369a1; padding: 4px 8px; '
            'border-radius: 4px; font-weight: 600; font-size: 12px;">{}</span>',
            obj.pattern
        )
    pattern_badge.short_description = '패턴'

    def get_group_status(self, obj):
        """그룹 활성화 상태"""
        if obj.group.is_active:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">✓ 활성</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: bold;">✗ 비활성</span>'
        )
    get_group_status.short_description = '그룹 상태'
    get_group_status.admin_order_field = 'group__is_active'

    def copy_patterns_to_group(self, request, queryset):
        """선택한 패턴을 다른 그룹으로 복사"""
        # 이 기능은 추후 구현 (현재는 메시지만)
        self.message_user(
            request,
            '패턴 복사 기능은 추후 구현 예정입니다. 현재는 직접 추가해주세요.',
            'info'
        )
    copy_patterns_to_group.short_description = '선택한 패턴을 다른 그룹으로 복사'

    def delete_patterns(self, request, queryset):
        """선택한 패턴 삭제"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count}개 패턴을 삭제했습니다.', 'success')
    delete_patterns.short_description = '선택한 패턴 삭제'

@admin.register(CustomerDiscount)
class CustomerDiscountAdmin(admin.ModelAdmin):
    list_display = ['get_customer_name', 'customer_code', 'brand', 'get_group_name', 'discount_rate', 'priority', 'date_range', 'is_active', 'is_valid_status']
    list_filter = ['is_active', 'brand', 'group__brand', 'group__group_name']
    list_editable = ['discount_rate', 'priority', 'is_active']
    search_fields = ['customer__name', 'customer__code', '=customer_code', 'customer_code', 'brand', 'group__group_name', 'memo']
    ordering = ['customer__name', 'brand', '-priority']
    list_per_page = 50
    autocomplete_fields = ['group', 'customer']

    fieldsets = (
        ('고객 및 브랜드', {
            'fields': ('customer', 'customer_code', 'brand', 'group')
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
        # customer ForeignKey 사용, 없으면 customer_code로 조회 (하위 호환성)
        if obj.customer:
            return obj.customer.name
        # 기존 customer_code는 사업자번호(enno)를 저장
        customer = Customers.objects.filter(enno=obj.customer_code).first()
        return customer.name if customer else f'⚠️ {obj.customer_code}'
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
    list_display = ['goods_code', 'stock_quantity', 'year_2025', 'year_2024', 'year_2023', 'year_2022', 'year_2021_before',
                   'year_2024_discount', 'year_2023_discount', 'year_2022_discount', 'year_2021_before_discount',
                   'mobile_stock_display', 'last_updated']
    list_editable = ['year_2025', 'year_2024', 'year_2023', 'year_2022', 'year_2021_before',
                    'year_2024_discount', 'year_2023_discount', 'year_2022_discount', 'year_2021_before_discount']
    search_fields = ['=goods_code', 'goods_code']  # =goods_code: 정확히 일치, goods_code: 포함
    ordering = ['goods_code']
    readonly_fields = ['last_updated', 'total_allocated_display', 'stock_quantity', 'mobile_stock_display']
    list_per_page = 50

    def stock_quantity(self, obj):
        """Goods 테이블의 재고수량 표시 (ERP 참고용)"""
        try:
            from .models import Goods
            from django.utils.html import format_html
            # filter().first()로 변경하여 중복 레코드 문제 방지
            goods = Goods.objects.filter(code=obj.goods_code).first()
            if goods:
                erp_stock = int(goods.jaego)
                mobile_stock = obj.total_allocated

                # ERP 재고와 모바일 재고 차이 표시
                if erp_stock > mobile_stock:
                    # ERP 재고가 더 많음 (정상)
                    return format_html(
                        '<span style="color: #666;" title="ERP 참고용 재고">{}</span>',
                        erp_stock
                    )
                elif erp_stock == mobile_stock:
                    # 동일함
                    return format_html(
                        '<span style="color: #666;" title="ERP 참고용 재고">{}</span>',
                        erp_stock
                    )
                else:
                    # 모바일 재고가 더 많음 (경고)
                    return format_html(
                        '<span style="color: #d63031; font-weight: bold;" title="⚠️ 모바일 재고({})가 ERP 재고보다 많습니다!">{}</span>',
                        mobile_stock, erp_stock
                    )
            else:
                return format_html('<span style="color: #999;">-</span>')
        except (ValueError, TypeError):
            return format_html('<span style="color: #999;">-</span>')
    stock_quantity.short_description = '재고수량 (ERP 참고)'

    def mobile_stock_display(self, obj):
        """모바일 판매 가능 재고 표시"""
        from django.utils.html import format_html
        mobile_stock = obj.total_allocated

        # 재고 부족 여부에 따라 색상 변경
        if mobile_stock == 0:
            # 재고 없음 (빨강)
            return format_html(
                '<span style="color: #d63031; font-weight: bold;" title="재고 없음 - 주문 불가">품절 (0)</span>'
            )
        elif mobile_stock <= 5:
            # 재고 부족 (주황)
            return format_html(
                '<span style="color: #e17055; font-weight: bold;" title="재고 부족 - 모바일 주문 가능">⚠️ {}</span>',
                mobile_stock
            )
        else:
            # 재고 충분 (초록)
            return format_html(
                '<span style="color: #00b894; font-weight: bold;" title="모바일 판매 가능 재고">{}</span>',
                mobile_stock
            )
    mobile_stock_display.short_description = '모바일 판매 가능'

    def total_allocated_display(self, obj):
        """total_allocated를 읽기 전용 필드로 표시"""
        from django.utils.html import format_html
        return format_html('<span>{}</span>', obj.total_allocated)
    total_allocated_display.short_description = 'DOT 합계'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """수량 및 할인율 필드에서 음수 입력 방지"""
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        # 수량 필드: 음수 입력 금지 (min=0)
        if db_field.name in ['year_2025', 'year_2024', 'year_2023', 'year_2022', 'year_2021_before']:
            formfield.widget.attrs.update({
                'min': '0',
                'style': 'width: 80px;'
            })

        # 할인율 필드: 음수 입력 금지 (min=0, max=100)
        if db_field.name in ['year_2024_discount', 'year_2023_discount', 'year_2022_discount', 'year_2021_before_discount', 'base_discount']:
            formfield.widget.attrs.update({
                'min': '0',
                'max': '100',
                'step': '0.01',
                'style': 'width: 80px;'
            })

        return formfield

    fieldsets = (
        ('상품 정보', {
            'fields': ('goods_code', 'stock_quantity', 'mobile_stock_display')
        }),
        ('📦 모바일 판매 재고 (DOT별 수량)', {
            'fields': ('year_2025', 'year_2024', 'year_2023', 'year_2022', 'year_2021_before'),
            'description': '⚠️ 모바일 주문 시 이 수량에서 차감됩니다. ERP 재고와는 별도로 관리됩니다.'
        }),
        ('💰 DOT 할인율 (연도별)', {
            'fields': ('year_2024_discount', 'year_2023_discount', 'year_2022_discount', 'year_2021_before_discount'),
            'description': '과거 제조년도 상품에 대한 추가 할인율을 설정합니다.'
        }),
        ('📊 시스템 정보', {
            'fields': ('total_allocated_display', 'last_updated'),
            'classes': ('collapse',)
        }),
    )

    def _validate_negative_values(self, obj):
        """음수 방지 검증"""
        errors = []
        if obj.year_2025 < 0:
            errors.append(f'{obj.goods_code}: 2025년 수량은 음수일 수 없습니다.')
        if obj.year_2024 < 0:
            errors.append(f'{obj.goods_code}: 2024년 수량은 음수일 수 없습니다.')
        if obj.year_2023 < 0:
            errors.append(f'{obj.goods_code}: 2023년 수량은 음수일 수 없습니다.')
        if obj.year_2022 < 0:
            errors.append(f'{obj.goods_code}: 2022년 수량은 음수일 수 없습니다.')
        if obj.year_2021_before < 0:
            errors.append(f'{obj.goods_code}: 2021년 이전 수량은 음수일 수 없습니다.')
        if obj.year_2024_discount < 0:
            errors.append(f'{obj.goods_code}: 2024년 할인율은 음수일 수 없습니다.')
        if obj.year_2023_discount < 0:
            errors.append(f'{obj.goods_code}: 2023년 할인율은 음수일 수 없습니다.')
        if obj.year_2022_discount < 0:
            errors.append(f'{obj.goods_code}: 2022년 할인율은 음수일 수 없습니다.')
        if obj.year_2021_before_discount < 0:
            errors.append(f'{obj.goods_code}: 2021년 이전 할인율은 음수일 수 없습니다.')
        if obj.base_discount < 0:
            errors.append(f'{obj.goods_code}: 기본 할인율은 음수일 수 없습니다.')
        return errors

    def save_model(self, request, obj, form, change):
        """저장 전 유효성 검증"""
        from django.contrib import messages
        from django.core.exceptions import ValidationError

        # 음수 방지 검증
        errors = self._validate_negative_values(obj)
        if errors:
            for error in errors:
                messages.error(request, error)
            raise ValidationError(errors)

        try:
            obj.clean()  # clean() 메서드 호출하여 검증
            super().save_model(request, obj, form, change)
        except Exception as e:
            messages.error(request, str(e))
            raise

    def save_formset(self, request, form, formset, change):
        """일괄 저장 시 각 인스턴스의 save() 메서드가 호출되도록 보장"""
        from django.contrib import messages
        from django.core.exceptions import ValidationError

        instances = formset.save(commit=False)

        # 각 인스턴스를 개별적으로 저장하면서 음수 검증
        for instance in instances:
            # 음수 검증
            errors = self._validate_negative_values(instance)
            if errors:
                for error in errors:
                    messages.error(request, error)
                raise ValidationError(errors)

            # 모델의 save() 메서드 호출 (Goods.jaego 자동 동기화)
            instance.save()

        # 삭제된 인스턴스 처리
        for obj in formset.deleted_objects:
            obj.delete()

        # formset 자체도 저장
        formset.save_m2m()

@admin.register(DiscountHistory)
class DiscountHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer_code', 'product_code', 'brand', 'applied_discount', 'original_price', 'final_price', 'transaction_date']
    list_filter = ['brand', 'transaction_date']
    search_fields = ['=customer_code', 'customer_code', '=product_code', 'product_code', 'brand']
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
    search_fields = ['=customer_code', 'customer_code', '=product_code', 'product_code', 'brand', 'memo']
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
    search_fields = ['=customer_code', 'customer_code', '=product_code', 'product_code']
    ordering = ['-created_at']
    list_per_page = 50

    def get_customer_name(self, obj):
        return obj.customer_name
    get_customer_name.short_description = '고객명'

    def get_product_name(self, obj):
        return obj.product_name
    get_product_name.short_description = '상품명'


# ============================================
# 주문 관리 Admin (분리됨 - admin_orders.py 참조)
# ============================================
#
# NOTE: OrderItemInline과 PaymentInline은 admin_orders.py에 정의되어 있습니다.
# MobileOrderAdmin과 ERPPhoneOrderAdmin에서 사용하는 인라인 클래스는
# admin_orders.py의 BaseOrderAdmin에 정의되어 있습니다.
# ============================================

# 기존 Order Admin 대신 모바일/ERP 주문 분리 Admin 사용
# admin_orders.py에서 MobileOrderAdmin, ERPPhoneOrderAdmin 임포트
from .admin_orders import MobileOrderAdmin, ERPPhoneOrderAdmin


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_order_number', 'product_code', 'product_name', 'brand',
                   'quantity', 'selected_year', 'discounted_price', 'final_price']
    list_filter = ['brand', 'selected_year']
    search_fields = ['=order__order_number', 'order__order_number', '=product_code', 'product_code', 'product_name']
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
    search_fields = ['=order__order_number', 'order__order_number', '=transaction_id', 'transaction_id', 'pg_name']
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


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_code', 'get_customer_name', 'recipient_name',
                   'phone_number', 'address', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['=customer_code', 'customer_code', 'recipient_name', 'phone_number', 'address']
    ordering = ['-is_default', '-created_at']
    list_per_page = 50

    fieldsets = (
        ('고객 정보', {
            'fields': ('customer_code', 'recipient_name', 'phone_number')
        }),
        ('주소 정보', {
            'fields': ('postal_code', 'address', 'address_detail')
        }),
        ('설정', {
            'fields': ('is_default',)
        }),
    )
    readonly_fields = []

    def get_customer_name(self, obj):
        return obj.customer_name
    get_customer_name.short_description = '고객명'


# ============================================
# 성능 표기 Admin (별도 파일에서 import)
# ============================================
@admin.register(GoodsDisplayName)
class GoodsDisplayNameAdmin(admin.ModelAdmin):
    """상품 표시명 (한글/영문) 관리"""
    list_display = ['goods_code', 'get_original_name', 'korean_name', 'english_name', 'updated_at']
    search_fields = ['=goods_code', 'goods_code', 'korean_name', 'english_name']
    ordering = ['goods_code']
    list_per_page = 50

    fieldsets = (
        ('상품 정보', {
            'fields': ('goods_code', 'get_original_name')
        }),
        ('표시명 설정', {
            'fields': ('korean_name', 'english_name'),
            'description': '모바일 화면에 표시될 한글명과 영문명을 입력합니다.'
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['get_original_name', 'created_at', 'updated_at']

    def get_original_name(self, obj):
        """Goods 테이블의 원래 상품명 표시"""
        try:
            goods = Goods.objects.get(code=obj.goods_code)
            return format_html('<span style="color: #666;">{}</span>', goods.name)
        except Goods.DoesNotExist:
            return '-'
    get_original_name.short_description = '원래 상품명 (ERP)'


from .admin_performance import (
    PerformanceCategoryAdmin,
    PerformanceTagAdmin,
    GoodsPerformanceTagAdmin
)


# ============================================
# ERP 스냅샷 관리
# ============================================

@admin.register(ERPSnapshot)
class ERPSnapshotAdmin(admin.ModelAdmin):
    """ERP 상태 스냅샷 관리"""

    list_display = [
        'timestamp',
        'status_badge',
        'erp_goods_count_display',
        'response_time_display',
        'database_status',
    ]

    list_filter = [
        'status',
        'database_status',
        ('timestamp', admin.DateFieldListFilter),
    ]

    search_fields = [
        'api_url',
        'error_message',
    ]

    readonly_fields = [
        'timestamp',
        'status',
        'response_time_ms',
        'erp_goods_count',
        'database_status',
        'api_url',
        'error_message',
        'created_at',
    ]

    date_hierarchy = 'timestamp'

    list_per_page = 50

    def has_add_permission(self, request):
        """추가 권한 없음 (명령어로만 생성)"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 권한 없음 (읽기 전용)"""
        return False

    def status_badge(self, obj):
        """상태 배지"""
        colors = {
            'connected': '#10b981',  # 녹색
            'disconnected': '#ef4444',  # 빨강
            'timeout': '#f59e0b',  # 주황
            'connection_error': '#ef4444',  # 빨강
        }
        color = colors.get(obj.status, '#6b7280')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = '상태'

    def erp_goods_count_display(self, obj):
        """상품 수 표시"""
        if obj.erp_goods_count > 0:
            # 숫자를 먼저 포맷팅
            formatted_count = f'{obj.erp_goods_count:,}'
            return format_html(
                '<strong style="color: #2563eb;">{}개</strong>',
                formatted_count
            )
        return '-'
    erp_goods_count_display.short_description = 'ERP 상품 수'

    def response_time_display(self, obj):
        """응답 시간 표시"""
        if obj.response_time_ms:
            # 응답 시간에 따라 색상 변경
            if obj.response_time_ms < 200:
                color = '#10b981'  # 빠름 (녹색)
            elif obj.response_time_ms < 500:
                color = '#f59e0b'  # 보통 (주황)
            else:
                color = '#ef4444'  # 느림 (빨강)

            # 시간을 먼저 포맷팅
            formatted_time = f'{obj.response_time_ms:.2f}'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}ms</span>',
                color,
                formatted_time
            )
        return '-'
    response_time_display.short_description = '응답 시간'

    fieldsets = (
        ('스냅샷 정보', {
            'fields': ('timestamp', 'created_at')
        }),
        ('연결 상태', {
            'fields': ('status', 'response_time_ms', 'database_status')
        }),
        ('데이터', {
            'fields': ('erp_goods_count',)
        }),
        ('API 정보', {
            'fields': ('api_url',)
        }),
        ('오류 정보', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )


# ============================================
# 실시간 재고 변화 추적
# ============================================

@admin.register(GoodsRealtimeSnapshot)
class GoodsRealtimeSnapshotAdmin(admin.ModelAdmin):
    """실시간 재고 변화 추적 (관리자 실시간성 증명용)"""

    list_display = [
        'snapshot_time_display',
        'code',
        'name_short',
        'bun1',
        'jaego_display',
        'change_display',
    ]

    list_filter = [
        ('snapshot_time', admin.DateFieldListFilter),
        'code',
    ]

    search_fields = [
        'code',
        'name',
        'bun1',
    ]

    readonly_fields = [
        'code',
        'name',
        'bun1',
        'jaego',
        'snapshot_time',
        'change_from_prev',
        'created_at',
    ]

    date_hierarchy = 'snapshot_time'

    list_per_page = 50

    ordering = ['-snapshot_time', 'code']

    def has_add_permission(self, request):
        """추가 권한 없음 (명령어로만 생성)"""
        return False

    def has_change_permission(self, request, obj=None):
        """수정 권한 없음 (읽기 전용)"""
        return False

    def snapshot_time_display(self, obj):
        """스냅샷 시간 표시 (한국 시간)"""
        from django.utils import timezone
        local_time = timezone.localtime(obj.snapshot_time)
        return format_html(
            '<span style="font-weight: bold; color: #2563eb;">{}</span>',
            local_time.strftime('%m-%d %H:%M')
        )
    snapshot_time_display.short_description = '스냅샷 시간'
    snapshot_time_display.admin_order_field = 'snapshot_time'

    def name_short(self, obj):
        """상품명 짧게 표시 (40자 제한)"""
        if len(obj.name) > 40:
            return format_html(
                '<span title="{}">{}</span>',
                obj.name,
                obj.name[:40] + '...'
            )
        return obj.name
    name_short.short_description = '상품명'

    def jaego_display(self, obj):
        """재고수량 표시"""
        formatted_jaego = f'{obj.jaego:,}'
        return format_html(
            '<strong style="color: #059669;">{}개</strong>',
            formatted_jaego
        )
    jaego_display.short_description = '재고수량'
    jaego_display.admin_order_field = 'jaego'

    def change_display(self, obj):
        """변화량 표시 (색상 + 아이콘)"""
        if obj.change_from_prev > 0:
            # 증가 (녹색)
            formatted_change = f'+{obj.change_from_prev:,}'
            return format_html(
                '<span style="color: #10b981; font-weight: bold; font-size: 14px;">🟢 {}</span>',
                formatted_change
            )
        elif obj.change_from_prev < 0:
            # 감소 (빨강)
            formatted_change = f'{obj.change_from_prev:,}'
            return format_html(
                '<span style="color: #ef4444; font-weight: bold; font-size: 14px;">🔴 {}</span>',
                formatted_change
            )
        else:
            # 변화 없음 (회색)
            return format_html(
                '<span style="color: #9ca3af; font-size: 14px;">⚪ 0</span>'
            )
    change_display.short_description = '변화량'
    change_display.admin_order_field = 'change_from_prev'

    fieldsets = (
        ('스냅샷 정보', {
            'fields': ('snapshot_time', 'created_at')
        }),
        ('상품 정보', {
            'fields': ('code', 'name', 'bun1')
        }),
        ('재고 정보', {
            'fields': ('jaego', 'change_from_prev')
        }),
    )


# ============================================
# Admin 활동 내역 관리
# ============================================

from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Admin 활동 내역 관리 (읽기 전용)"""

    list_display = [
        'action_time_display',
        'user_display',
        'action_type_display',
        'object_repr_short',
        'change_message_short',
    ]

    list_filter = [
        'action_flag',
        'user',
        ('action_time', admin.DateFieldListFilter),
    ]

    search_fields = [
        'user__username',
        'object_repr',
        'change_message',
    ]

    ordering = ['-action_time']

    list_per_page = 100

    date_hierarchy = 'action_time'

    # 읽기 전용
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # 슈퍼유저만 삭제 가능

    def action_time_display(self, obj):
        """활동 시간 표시"""
        from django.utils import timezone
        local_time = timezone.localtime(obj.action_time)
        return format_html(
            '<span style="color: #2563eb;">{}</span>',
            local_time.strftime('%Y-%m-%d %H:%M:%S')
        )
    action_time_display.short_description = '활동 시간'
    action_time_display.admin_order_field = 'action_time'

    def user_display(self, obj):
        """사용자 표시"""
        return format_html(
            '<strong>{}</strong>',
            obj.user.username if obj.user else '-'
        )
    user_display.short_description = '사용자'
    user_display.admin_order_field = 'user'

    def action_type_display(self, obj):
        """활동 유형 표시"""
        colors = {
            1: '#10b981',  # 추가 (녹색)
            2: '#3b82f6',  # 수정 (파랑)
            3: '#ef4444',  # 삭제 (빨강)
        }
        labels = {
            1: '추가',
            2: '수정',
            3: '삭제',
        }
        color = colors.get(obj.action_flag, '#6b7280')
        label = labels.get(obj.action_flag, '알 수 없음')

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            label
        )
    action_type_display.short_description = '활동 유형'
    action_type_display.admin_order_field = 'action_flag'

    def object_repr_short(self, obj):
        """대상 객체 표시 (짧게)"""
        if len(obj.object_repr) > 50:
            return format_html(
                '<span title="{}">{}</span>',
                obj.object_repr,
                obj.object_repr[:50] + '...'
            )
        return obj.object_repr
    object_repr_short.short_description = '대상 객체'

    def change_message_short(self, obj):
        """변경 메시지 표시 (짧게)"""
        if len(obj.change_message) > 80:
            return format_html(
                '<span title="{}">{}</span>',
                obj.change_message,
                obj.change_message[:80] + '...'
            )
        return obj.change_message or '-'
    change_message_short.short_description = '변경 내용'


# ============================================
# Custom Admin Site - 사이드바 메뉴 재구성
# ============================================

class TirePassAdminSite(admin.AdminSite):
    """
    TirePASS 전용 Admin Site
    사이드바를 3개 카테고리로 재구성: 판매, 할인, 설정
    """
    site_header = 'TirePASS 관리'
    site_title = 'TirePASS 관리자'
    index_title = 'TirePASS 관리 시스템'

    def get_app_list(self, request, app_label=None):
        """
        사이드바 메뉴를 3개 카테고리로 재구성

        A. 판매 (8개): Goods, MobileOrder, ERPPhoneOrder, OrderItem, Payment, ShoppingCart, ShippingAddress, Customers
        B. 할인 (6개): BrandGroup, BrandGroupPattern, CustomerDiscount, CustomerProductDiscount, YearAllocation, DiscountHistory
        C. 설정 (8개): GoodsDisplayName, PerformanceCategory, PerformanceTag, GoodsPerformanceTag, ERPSnapshot, GoodsRealtimeSnapshot, User, LogEntry
        """
        # 기본 앱 목록 가져오기
        app_dict = self._build_app_dict(request, app_label)

        # 모델별 카테고리 매핑
        category_mapping = {
            # A. 판매 (8개)
            'goods': 'A. 판매',
            'mobileorder': 'A. 판매',
            'erpphoneorder': 'A. 판매',
            'orderitem': 'A. 판매',
            'payment': 'A. 판매',
            'shoppingcart': 'A. 판매',
            'shippingaddress': 'A. 판매',
            'customers': 'A. 판매',

            # B. 할인 (6개)
            'brandgroup': 'B. 할인',
            'brandgrouppattern': 'B. 할인',
            'customerdiscount': 'B. 할인',
            'customerproductdiscount': 'B. 할인',
            'yearallocation': 'B. 할인',
            'discounthistory': 'B. 할인',

            # C. 설정 (8개)
            'goodsdisplayname': 'C. 설정',
            'performancecategory': 'C. 설정',
            'performancetag': 'C. 설정',
            'goodsperformancetag': 'C. 설정',
            'erpsnapshot': 'C. 설정',
            'goodsrealtimesnapshot': 'C. 설정',
            'user': 'C. 설정',
            'logentry': 'C. 설정',
        }

        # 카테고리별로 모델 그룹화
        categorized = {
            'A. 판매': {'name': 'A. 판매', 'app_label': 'sales', 'app_url': '', 'models': []},
            'B. 할인': {'name': 'B. 할인', 'app_label': 'discounts', 'app_url': '', 'models': []},
            'C. 설정': {'name': 'C. 설정', 'app_label': 'settings', 'app_url': '', 'models': []},
        }

        # 각 앱의 모델들을 카테고리별로 분류
        for app in app_dict.values():
            for model in app['models']:
                model_name = model['object_name'].lower()
                category = category_mapping.get(model_name)

                if category:
                    categorized[category]['models'].append(model)

        # 각 카테고리의 모델을 이름순으로 정렬
        for category in categorized.values():
            category['models'].sort(key=lambda x: x['name'])

        # 결과 리스트 생성 (A → B → C 순서)
        app_list = [
            categorized['A. 판매'],
            categorized['B. 할인'],
            categorized['C. 설정'],
        ]

        # 빈 카테고리 제거
        app_list = [cat for cat in app_list if cat['models']]

        return app_list


@admin.register(ExcludedGoods)
class ExcludedGoodsAdmin(admin.ModelAdmin):
    """ERP 동기화 제외 상품 관리"""
    list_display = ['code', 'reason', 'excluded_at', 'excluded_by']
    search_fields = ['code', 'reason']
    readonly_fields = ['excluded_at']
    fields = ['code', 'reason', 'excluded_by', 'excluded_at']

    def has_add_permission(self, request):
        """추가 권한"""
        return True

    def has_change_permission(self, request, obj=None):
        """변경 권한"""
        return True

    def has_delete_permission(self, request, obj=None):
        """삭제 권한 (제외 목록에서 제거 = 다시 동기화 허용)"""
        return True


# 커스텀 Admin Site 인스턴스 생성
custom_admin_site = TirePassAdminSite(name='custom_admin')

# 기본 admin.site에 등록된 모든 모델을 custom_admin_site로 복사
def register_all_to_custom_site():
    """기본 admin.site의 모든 모델 등록을 custom_admin_site로 복사"""
    for model, model_admin in admin.site._registry.items():
        # 이미 등록되지 않은 경우에만 등록
        if model not in custom_admin_site._registry:
            # 같은 AdminClass 인스턴스를 재사용
            admin_class = model_admin.__class__
            custom_admin_site.register(model, admin_class)

# 등록 실행
register_all_to_custom_site()
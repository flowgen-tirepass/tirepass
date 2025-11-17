"""
모바일 API 뷰
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.utils import timezone
from functools import wraps
import json
import secrets
import re
import time

from .models import Goods, GoodsDisplayName, Customers, ShoppingCart, Order, OrderItem, Payment, ShippingAddress, Brand, BrandPattern
from .utils import calculate_discount_price, generate_order_number, update_stock


# ============================================
# 세션 인증 데코레이터
# ============================================

def require_session_auth(view_func):
    """
    세션 인증이 필요한 API에 사용하는 데코레이터

    - 세션에 customer_code가 있는지 확인
    - 요청의 customer_code와 세션의 customer_code가 일치하는지 확인
    - 인증 실패 시 401 Unauthorized 응답
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # 세션에서 customer_code 가져오기
        session_customer_code = request.session.get('customer_code')

        if not session_customer_code:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.',
                'error_code': 'AUTH_REQUIRED'
            }, status=401)

        # 요청에서 customer_code 가져오기 (GET 또는 POST)
        if request.method == 'GET':
            request_customer_code = request.GET.get('customer_code')
        else:
            try:
                data = json.loads(request.body)
                request_customer_code = data.get('customer_code')
            except (json.JSONDecodeError, AttributeError):
                request_customer_code = None

        # customer_code가 요청에 있고, 세션과 일치하는지 확인
        if request_customer_code and request_customer_code != session_customer_code:
            return JsonResponse({
                'success': False,
                'message': '인증 오류: 권한이 없습니다.',
                'error_code': 'AUTH_MISMATCH'
            }, status=403)

        # 인증 통과 - 원래 뷰 함수 실행
        return view_func(request, *args, **kwargs)

    return wrapper


# 브랜드명 영문-한글 매핑
BRAND_NAME_MAP = {
    'GOODYEAR': '굿이어',
    'KUMHO': '금호',
    'NEXEN': '넥센',
    'DUNLOP': '던롭',
    'MICHELIN': '미쉐린',
    'BRIDGESTONE': '브리지스톤',
    'YOKOHAMA': '요코하마',
    'CONTINENTAL': '콘티넨탈',
    'PIRELLI': '피렐리',
    'HANKOOK': '한국',
    'HANKOOKTIRE': '한국',
    'TOYO': '토요',
    'FIRESTONE': '파이어스톤',
    'BFG': 'BFG',
    'BFGOODRICH': 'BFG',
}


# ============================================
# API 인덱스
# ============================================

@require_http_methods(["GET"])
def api_index(request):
    """모바일 API 인덱스 - 사용 가능한 엔드포인트 목록"""
    return JsonResponse({
        'success': True,
        'message': 'TirePASS Mobile API',
        'version': '1.0',
        'endpoints': {
            '상품 API': {
                'GET /api/mobile/products/': '상품 목록 조회',
                'GET /api/mobile/products/<code>/': '상품 상세 조회',
            },
            '장바구니 API': {
                'GET /api/mobile/cart/': '장바구니 조회',
                'POST /api/mobile/cart/add/': '장바구니 담기',
                'POST /api/mobile/cart/<id>/update/': '장바구니 수량 수정',
                'DELETE /api/mobile/cart/<id>/remove/': '장바구니 삭제',
            },
            '주문 API': {
                'GET /api/mobile/orders/': '주문 목록 조회',
                'POST /api/mobile/orders/create/': '주문 생성',
                'GET /api/mobile/orders/<id>/': '주문 상세 조회',
            },
            '가격 계산 API': {
                'GET /api/mobile/calculate-price/': '가격 계산',
            },
            '인증 API': {
                'POST /api/mobile/auth/register/': '회원가입',
                'POST /api/mobile/auth/login/': '로그인',
                'POST /api/mobile/auth/logout/': '로그아웃',
                'GET /api/mobile/auth/profile/': '프로필 조회',
            },
            '결제 API (토스페이먼츠)': {
                'POST /api/mobile/payment/prepare/': '결제 준비 (주문 생성)',
                'POST /api/mobile/payment/confirm/': '결제 승인',
                'POST /api/mobile/payment/cancel/': '결제 취소',
                'GET /api/mobile/payment/status/<payment_key>/': '결제 상태 조회',
            },
            '배송지 주소 API': {
                'GET /api/mobile/shipping-addresses/': '배송지 목록 조회',
                'POST /api/mobile/shipping-addresses/add/': '배송지 추가',
                'POST /api/mobile/shipping-addresses/<id>/update/': '배송지 수정',
                'DELETE /api/mobile/shipping-addresses/<id>/delete/': '배송지 삭제',
                'POST /api/mobile/shipping-addresses/<id>/set-default/': '기본 배송지 설정',
            }
        },
        'documentation': 'http://localhost:8080/api/mobile/docs/'
    })


# ============================================
# 상품 API
# ============================================

@require_http_methods(["GET"])
def api_products_list(request):
    """
    상품 목록 조회 API

    Query Parameters:
        - search: 검색어 (상품명, 코드)
        - brand: 단일 브랜드 필터
        - brands: 다중 브랜드 필터 (쉼표로 구분, 예: KUMHO,NEXEN,MICHELIN)
        - tire_only: 타이어만 보기 (1/0)
        - in_stock: 재고 있는 상품만 (1/0)
        - page: 페이지 번호 (기본값: 1)
        - page_size: 페이지 크기 (기본값: 20)
    """
    # 파라미터 추출
    search = request.GET.get('search', '')
    brand = request.GET.get('brand', '')
    brands = request.GET.get('brands', '')  # 다중 브랜드 (쉼표로 구분)
    tire_only = request.GET.get('tire_only', '0') == '1'
    in_stock = request.GET.get('in_stock', '1') == '1'  # 기본값: 재고 있는 것만
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))

    # 기본 쿼리셋
    products = Goods.objects.all()

    # 타이어만 필터 (코드 패턴으로 필터링)
    if tire_only:
        tire_patterns = ['K-', 'H-', 'M-', 'N-', 'P-', 'BS-', 'CT-', 'D-', 'Y-', 'F-', 'T-', 'G-', 'BFG']
        tire_filter = Q()
        for pattern in tire_patterns:
            tire_filter |= Q(code__startswith=pattern)
        products = products.filter(tire_filter)

    # 재고 필터
    if in_stock:
        products = products.filter(jaego__gt=0)

    # 검색
    if search:
        # 기본 검색 (코드, 상품명, 브랜드)
        q_filter = Q(code__icontains=search) | Q(name__icontains=search) | Q(bun1__icontains=search)

        # 영문 브랜드명을 한글로 변환하여 검색 (예: "pirelli" -> "피렐리")
        search_upper = search.strip().upper()
        if search_upper in BRAND_NAME_MAP:
            brand_korean = BRAND_NAME_MAP[search_upper]
            q_filter |= Q(bun1__icontains=brand_korean)

        # 숫자만 추출하여 타이어 사이즈 패턴 검색
        numeric_only = re.sub(r'[^0-9]', '', search)
        if len(numeric_only) >= 5:
            patterns = []

            if len(numeric_only) == 5:
                # 5자리: 145R13 형식 (width 3자리 + rim 2자리, aspect ratio 없음)
                width = numeric_only[:3]
                rim = numeric_only[3:5]
                patterns = [
                    f"{width}R{rim}",
                    f"{width}r{rim}",
                    f"{width}/{rim}",
                    f"{width}-{rim}",
                    f"{width} {rim}",
                ]
            else:
                # 6자리 이상: 205/55R16 형식 (width 3자리 + aspect 2자리 + rim)
                width = numeric_only[:3]
                aspect = numeric_only[3:5]

                # 나머지 숫자를 인치로 사용
                if len(numeric_only) >= 7:
                    rim = numeric_only[5:7]
                else:
                    rim = numeric_only[5:]

                patterns = [
                    f"{width}/{aspect}R{rim}",
                    f"{width}/{aspect}/{rim}",
                    f"{width}-{aspect}-{rim}",
                    f"{width} {aspect} {rim}",
                    f"{width}/{aspect}r{rim}",  # 소문자 r
                ]

            # 패턴 추가
            for pattern in patterns:
                q_filter |= Q(name__icontains=pattern)

        products = products.filter(q_filter)

    # 브랜드 필터
    if brands:
        # 다중 브랜드 검색 (교차 정렬)
        brand_list_eng = [b.strip().upper() for b in brands.split(',') if b.strip()]

        # 영문 브랜드명을 한글로 변환
        brand_list = []
        for brand_eng in brand_list_eng:
            brand_kor = BRAND_NAME_MAP.get(brand_eng, brand_eng)
            brand_list.append(brand_kor)

        if len(brand_list) > 0:
            # 각 브랜드별로 상품 조회 (재고 많은 순 + 가격 높은 순)
            brand_products = []

            for brand_name in brand_list:
                brand_items = products.filter(bun1=brand_name).order_by('-jaego', '-fixp')
                brand_products.append(list(brand_items))

            # 브랜드별로 1개씩 교차 출력
            interleaved_products = []
            max_len = max([len(bp) for bp in brand_products]) if brand_products else 0

            for i in range(max_len):
                for brand_items in brand_products:
                    if i < len(brand_items):
                        if brand_items[i] not in interleaved_products:
                            interleaved_products.append(brand_items[i])

            # 페이지네이션
            total_count = len(interleaved_products)
            start = (page - 1) * page_size
            end = start + page_size
            products_page = interleaved_products[start:end]
        else:
            # 일반 정렬
            products = products.order_by('-jaego', '-fixp')
            total_count = products.count()
            start = (page - 1) * page_size
            end = start + page_size
            products_page = products[start:end]

    elif brand:
        # 단일 브랜드 필터
        products = products.filter(bun1=brand).order_by('-jaego', '-fixp')
        total_count = products.count()
        start = (page - 1) * page_size
        end = start + page_size
        products_page = products[start:end]

    else:
        # 브랜드 필터 없음 - 일반 정렬
        products = products.order_by('-jaego', 'code')
        total_count = products.count()
        start = (page - 1) * page_size
        end = start + page_size
        products_page = products[start:end]

    # YearAllocation 정보 가져오기
    from .models import YearAllocation, GoodsPerformanceTag
    product_codes = [p.code for p in products_page]
    year_allocations = {ya.goods_code: ya for ya in YearAllocation.objects.filter(goods_code__in=product_codes)}

    # GoodsDisplayName 정보 가져오기 (한글명/영문명)
    display_names = {dn.goods_code: dn for dn in GoodsDisplayName.objects.filter(goods_code__in=product_codes)}

    # 성능 표기 정보 가져오기 (기존 시스템)
    performance_tags_qs = GoodsPerformanceTag.objects.filter(
        goods_code__in=product_codes
    ).select_related('tag', 'tag__category').order_by('tag__category__order', 'tag__order')

    # 상품별로 성능 표기 그룹화
    performance_tags_by_goods = {}
    for pt in performance_tags_qs:
        if pt.goods_code not in performance_tags_by_goods:
            performance_tags_by_goods[pt.goods_code] = []
        performance_tags_by_goods[pt.goods_code].append({
            'category': pt.tag.category.display_name,
            'tag': pt.tag.name
        })

    # 브랜드/패턴별 성능표시 정보 가져오기 (BrandPattern 기반)
    # 1. 활성화된 모든 브랜드 조회 (브랜드명 매칭용)
    all_brands = {brand.name: brand for brand in Brand.objects.filter(is_active=True)}

    # 2. 모든 활성화된 브랜드 패턴 조회 (성능표시 포함)
    brand_patterns = BrandPattern.objects.filter(
        is_active=True
    ).select_related('brand')

    # 3. 브랜드별, 패턴별로 그룹화
    brand_performance_map = {}
    for bp in brand_patterns:
        brand_name = bp.brand.name
        pattern_name = bp.pattern_name

        if brand_name not in brand_performance_map:
            brand_performance_map[brand_name] = {
                'patterns': {}     # 패턴별
            }

        # 패턴별 성능표시 저장
        brand_performance_map[brand_name]['patterns'][pattern_name] = bp

    # 결과 구성
    products_data = []
    for p in products_page:
        ya = year_allocations.get(p.code)

        # 할인율 결정: YearAllocation의 base_discount 우선, 없으면 Goods의 discount_rate 사용
        base_discount = 0.00
        if ya and hasattr(ya, 'base_discount') and ya.base_discount:
            base_discount = float(ya.base_discount)
        elif p.discount_rate:
            base_discount = float(p.discount_rate)

        # DOT 재고 정보 (제조년도별)
        # 중요: 모든 할인은 공장도가 기준으로 단순 합산 (cascading 방식 아님)
        # 공식: 공장도가 × (1 - 총할인율/100), 총할인율 = 기본할인% + DOT할인%
        dot_inventory = []
        if ya:
            base_price = p.fixp

            # 2025년 (DOT 할인 없음, 상품 기본할인만 적용)
            if ya.year_2025 > 0:
                total_discount_2025 = base_discount  # 기본 할인만
                price_2025 = int(base_price * (1 - total_discount_2025 / 100))
                dot_inventory.append({
                    'year': 2025,  # 정수로 변경
                    'stock': ya.year_2025,
                    'discount': total_discount_2025,
                    'price': price_2025
                })

            # 2024년 (상품 기본할인 + DOT 할인)
            if ya.year_2024 > 0:
                dot_discount_2024 = float(ya.year_2024_discount)
                total_discount_2024 = base_discount + dot_discount_2024  # 단순 합산
                price_2024 = int(base_price * (1 - total_discount_2024 / 100))
                dot_inventory.append({
                    'year': 2024,  # 정수로 변경
                    'stock': ya.year_2024,
                    'discount': total_discount_2024,
                    'price': price_2024
                })

            # 2023년 (상품 기본할인 + DOT 할인)
            if ya.year_2023 > 0:
                dot_discount_2023 = float(ya.year_2023_discount)
                total_discount_2023 = base_discount + dot_discount_2023  # 단순 합산
                price_2023 = int(base_price * (1 - total_discount_2023 / 100))
                dot_inventory.append({
                    'year': 2023,  # 정수로 변경
                    'stock': ya.year_2023,
                    'discount': total_discount_2023,
                    'price': price_2023
                })

            # 2022년 (상품 기본할인 + DOT 할인)
            if ya.year_2022 > 0:
                dot_discount_2022 = float(ya.year_2022_discount)
                total_discount_2022 = base_discount + dot_discount_2022  # 단순 합산
                price_2022 = int(base_price * (1 - total_discount_2022 / 100))
                dot_inventory.append({
                    'year': 2022,  # 정수로 변경
                    'stock': ya.year_2022,
                    'discount': total_discount_2022,
                    'price': price_2022
                })

            # 2021년 이전 (상품 기본할인 + DOT 할인)
            if ya.year_2021_before > 0:
                dot_discount_2021 = float(ya.year_2021_before_discount)
                total_discount_2021 = base_discount + dot_discount_2021  # 단순 합산
                price_2021 = int(base_price * (1 - total_discount_2021 / 100))
                dot_inventory.append({
                    'year': 2021,  # 정수로 변경
                    'stock': ya.year_2021_before,
                    'discount': total_discount_2021,
                    'price': price_2021
                })

        # 상품 목록에 표시할 할인율
        discount_rate = base_discount

        # 한글명/영문명 가져오기
        dn = display_names.get(p.code)
        korean_name = dn.korean_name if dn else None
        english_name = dn.english_name if dn else None

        # 브랜드/패턴별 성능표시 찾기
        brand_performance_boxes = []
        brand_logo = None
        product_brand_name = (p.bun1 or '').strip()

        if product_brand_name and product_brand_name in brand_performance_map:
            # 패턴 매칭 시도 (상품명에서 패턴명 찾기)
            matched_performance = None
            brand_patterns = brand_performance_map[product_brand_name]['patterns']

            # 상품명에서 패턴명 검색 (가장 긴 패턴명부터 매칭)
            sorted_patterns = sorted(brand_patterns.keys(), key=len, reverse=True)
            for pattern_name in sorted_patterns:
                if pattern_name in p.name or pattern_name in (korean_name or ''):
                    matched_performance = brand_patterns[pattern_name]
                    break

            # 성능표시 박스 생성
            if matched_performance:
                brand_performance_boxes = matched_performance.get_performance_boxes()
                # 브랜드 로고는 Brand 모델에서 가져옴 (이미지 URL)
                brand_logo = matched_performance.brand.logo_url

        products_data.append({
            'code': p.code,
            'name': p.name,
            'korean_name': korean_name,
            'english_name': english_name,
            'brand': product_brand_name,
            'price': p.fixp,
            'discount_rate': discount_rate,
            'stock': p.jaego,
            'is_tire': p.is_tire,
            'dot_inventory': dot_inventory,
            'performance_tags': performance_tags_by_goods.get(p.code, []),  # 기존 시스템 (호환성 유지)
            'brand_performance_boxes': brand_performance_boxes,  # 신규: 5개 성능 박스
            'brand_logo': brand_logo  # 신규: 브랜드 로고 파일명
        })

    result = {
        'success': True,
        'data': {
            'products': products_data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        }
    }

    return JsonResponse(result)


@require_http_methods(["GET"])
def api_product_detail(request, code):
    """
    상품 상세 조회 API (가격 계산 포함)

    Query Parameters:
        - customer_code: 고객 코드 (할인 계산용, 필수)
        - selected_year: 선택한 제조년도 (옵션)
    """
    customer_code = request.GET.get('customer_code')

    if not customer_code:
        return JsonResponse({
            'success': False,
            'message': '고객 코드가 필요합니다.'
        }, status=400)

    try:
        product = Goods.objects.get(code=code)
    except Goods.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '상품을 찾을 수 없습니다.'
        }, status=404)

    # 가격 계산
    selected_year = request.GET.get('selected_year')
    if selected_year:
        selected_year = int(selected_year)

    price_info = calculate_discount_price(
        product_code=code,
        customer_code=customer_code,
        selected_year=selected_year
    )

    result = {
        'success': True,
        'data': {
            'code': product.code,
            'name': product.name,
            'brand': product.bun1 or '',
            'price': product.fixp,
            'stock': product.jaego,
            'is_tire': product.is_tire,
            'price_info': {
                'unit_price': price_info['unit_price'],
                'basic_discount_rate': float(price_info['basic_discount_rate']),
                'customer_discount_rate': float(price_info['customer_discount_rate']),
                'additional_discount_rate': float(price_info['additional_discount_rate']),
                'dot_discount_rate': float(price_info['dot_discount_rate']),
                'total_discount_rate': float(price_info['total_discount_rate']),
                'discounted_price': price_info['discounted_price'],
                'available_years': price_info['available_years']
            }
        }
    }

    return JsonResponse(result)


# ============================================
# 장바구니 API
# ============================================

@require_session_auth
@require_http_methods(["GET"])
def api_cart_list(request):
    """장바구니 조회 API (상세 할인율 정보 포함)"""
    customer_code = request.GET.get('customer_code')

    if not customer_code:
        return JsonResponse({
            'success': False,
            'message': '고객 코드가 필요합니다.'
        }, status=400)

    carts = ShoppingCart.objects.filter(customer_code=customer_code).order_by('-created_at')

    items = []
    for cart in carts:
        # 실시간 가격 계산 (최신 할인율 반영)
        price_info = calculate_discount_price(
            product_code=cart.product_code,
            customer_code=customer_code,
            selected_year=cart.selected_year,
            quantity=cart.quantity
        )

        # 선택된 제조년도의 재고 수량 조회
        available_stock = 0
        if cart.selected_year and price_info.get('available_years'):
            # selected_year를 정수로 변환하여 비교
            try:
                selected_year_int = int(cart.selected_year)
                for year_info in price_info['available_years']:
                    if year_info['year'] == selected_year_int:
                        available_stock = year_info['quantity']
                        break
            except (ValueError, TypeError):
                # 변환 실패 시 문자열로 비교
                for year_info in price_info['available_years']:
                    if str(year_info['year']) == str(cart.selected_year):
                        available_stock = year_info['quantity']
                        break

        items.append({
            'id': cart.id,
            'product_code': cart.product_code,
            'product_name': cart.product_name,
            'quantity': cart.quantity,
            'selected_year': cart.selected_year,
            'available_stock': available_stock,  # 재고 정보 추가
            'unit_price': price_info['unit_price'],
            'basic_discount_rate': float(price_info['basic_discount_rate']),
            'customer_discount_rate': float(price_info['customer_discount_rate']),
            'additional_discount_rate': float(price_info['additional_discount_rate']),
            'dot_discount_rate': float(price_info['dot_discount_rate']),
            'total_discount_rate': float(price_info['total_discount_rate']),
            'discounted_price': price_info['discounted_price'],
            'final_price': price_info['final_price'],
        })

    result = {
        'success': True,
        'data': {
            'items': items,
            'total_price': sum(item['final_price'] for item in items)
        }
    }

    return JsonResponse(result)


@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_cart_add(request):
    """장바구니 담기 API"""
    import logging
    logger = logging.getLogger(__name__)

    try:
        data = json.loads(request.body)
        logger.info(f"장바구니 추가 요청: {data}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 오류: {e}")
        return JsonResponse({
            'success': False,
            'message': '잘못된 JSON 형식입니다.'
        }, status=400)

    customer_code = data.get('customer_code')
    product_code = data.get('product_code')
    quantity = data.get('quantity', 1)
    selected_year = data.get('selected_year')

    if not customer_code or not product_code:
        logger.warning(f"필수 파라미터 누락 - customer_code: {customer_code}, product_code: {product_code}")
        return JsonResponse({
            'success': False,
            'message': '고객 코드와 상품 코드가 필요합니다.'
        }, status=400)

    try:
        # 가격 계산
        logger.info(f"가격 계산 시작 - product: {product_code}, customer: {customer_code}, year: {selected_year}")
        price_info = calculate_discount_price(
            product_code=product_code,
            customer_code=customer_code,
            selected_year=selected_year,
            quantity=quantity
        )
        logger.info(f"가격 계산 완료: {price_info}")

        # 장바구니에 추가 또는 업데이트
        cart, created = ShoppingCart.objects.update_or_create(
            customer_code=customer_code,
            product_code=product_code,
            selected_year=selected_year,
            defaults={
                'quantity': quantity,
                'unit_price': price_info['unit_price'],
                'discount_rate': price_info['total_discount_rate'],
                'final_price': price_info['final_price']
            }
        )
        logger.info(f"장바구니 {'추가' if created else '업데이트'} 성공 - cart_id: {cart.id}")

        return JsonResponse({
            'success': True,
            'message': '장바구니에 추가되었습니다.' if created else '장바구니가 업데이트되었습니다.',
            'data': {
                'cart_id': cart.id,
                'quantity': cart.quantity
            }
        })

    except Exception as e:
        logger.error(f"장바구니 추가 실패: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'message': f'장바구니 추가 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_cart_update(request, cart_id):
    """장바구니 수량 수정 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 JSON 형식입니다.'
        }, status=400)

    quantity = data.get('quantity', 1)

    try:
        cart = ShoppingCart.objects.get(id=cart_id)
    except ShoppingCart.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '장바구니 항목을 찾을 수 없습니다.'
        }, status=404)

    # 가격 재계산
    price_info = calculate_discount_price(
        product_code=cart.product_code,
        customer_code=cart.customer_code,
        selected_year=cart.selected_year,
        quantity=quantity
    )

    cart.quantity = quantity
    cart.final_price = price_info['final_price']
    cart.save()

    return JsonResponse({
        'success': True,
        'message': '수량이 업데이트되었습니다.',
        'data': {
            'quantity': cart.quantity,
            'final_price': cart.final_price
        }
    })


@require_session_auth
@csrf_exempt
@require_http_methods(["DELETE"])
def api_cart_remove(request, cart_id):
    """장바구니 항목 삭제 API"""
    try:
        cart = ShoppingCart.objects.get(id=cart_id)
        cart.delete()
        return JsonResponse({
            'success': True,
            'message': '장바구니에서 삭제되었습니다.'
        })
    except ShoppingCart.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '장바구니 항목을 찾을 수 없습니다.'
        }, status=404)


# ============================================
# 주문 API
# ============================================

@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_order_create(request):
    """주문 생성 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 JSON 형식입니다.'
        }, status=400)

    customer_code = data.get('customer_code')
    cart_ids = data.get('cart_ids', [])  # 주문할 장바구니 항목 ID 목록
    shipping_address = data.get('shipping_address', '')
    shipping_memo = data.get('shipping_memo', '')
    payment_method = data.get('payment_method', 'transfer')

    if not customer_code or not cart_ids:
        return JsonResponse({
            'success': False,
            'message': '고객 코드와 장바구니 항목이 필요합니다.'
        }, status=400)

    # 고객 정보 조회
    try:
        customer = Customers.objects.get(code=customer_code)
    except Customers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '고객을 찾을 수 없습니다.'
        }, status=404)

    # 장바구니 항목 조회
    carts = ShoppingCart.objects.filter(id__in=cart_ids, customer_code=customer_code)

    if not carts.exists():
        return JsonResponse({
            'success': False,
            'message': '장바구니 항목을 찾을 수 없습니다.'
        }, status=404)

    # 주문 생성
    order_number = generate_order_number()
    total_amount = sum(cart.unit_price * cart.quantity for cart in carts)
    final_amount = sum(cart.final_price for cart in carts)
    total_discount = total_amount - final_amount

    order = Order.objects.create(
        order_number=order_number,
        customer_code=customer_code,
        customer_name=customer.name,
        total_amount=total_amount,
        total_discount=total_discount,
        final_amount=final_amount,
        payment_method=payment_method,
        shipping_address=shipping_address,
        shipping_memo=shipping_memo,
        order_status='pending',
        payment_status='unpaid'
    )

    # 주문 상세 생성 및 재고 차감
    for cart in carts:
        # 가격 정보 재계산
        price_info = calculate_discount_price(
            product_code=cart.product_code,
            customer_code=customer_code,
            selected_year=cart.selected_year,
            quantity=cart.quantity
        )

        OrderItem.objects.create(
            order=order,
            product_code=cart.product_code,
            product_name=price_info['product_name'],
            brand=price_info['brand'],
            quantity=cart.quantity,
            selected_year=cart.selected_year,
            unit_price=price_info['unit_price'],
            basic_discount_rate=price_info['basic_discount_rate'],
            customer_discount_rate=price_info['customer_discount_rate'],
            additional_discount_rate=price_info['additional_discount_rate'],
            dot_discount_rate=price_info['dot_discount_rate'],
            total_discount_rate=price_info['total_discount_rate'],
            discounted_price=price_info['discounted_price'],
            final_price=price_info['final_price']
        )

        # 재고 차감
        if cart.selected_year:
            update_stock(cart.product_code, cart.selected_year, cart.quantity, 'subtract')

        # 장바구니에서 삭제
        cart.delete()

    return JsonResponse({
        'success': True,
        'message': '주문이 완료되었습니다.',
        'data': {
            'order_number': order.order_number,
            'order_id': order.id,
            'final_amount': order.final_amount
        }
    })


@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_payment_billing(request):
    """
    빌링키 자동결제 API
    등록된 결제 수단으로 자동 결제 처리

    Request Body:
        - payment_method_id: 등록된 결제 수단 ID (필수)
        - customer_code: 고객 코드 (필수)
        - cart_ids: 장바구니 ID 목록 (필수)
        - shipping_address_id: 배송지 ID (선택)
        - shipping_memo: 배송 메모 (선택)
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '잘못된 요청입니다.'
        }, status=400)

    payment_method_id = data.get('payment_method_id')
    customer_code = data.get('customer_code')
    cart_ids = data.get('cart_ids', [])
    shipping_address_id = data.get('shipping_address_id')
    shipping_memo = data.get('shipping_memo', '')

    if not all([payment_method_id, customer_code, cart_ids]):
        return JsonResponse({
            'success': False,
            'message': '결제 수단, 고객 코드, 장바구니 항목이 필요합니다.'
        }, status=400)

    try:
        from django.db import transaction
        import requests
        import base64
        from django.conf import settings

        # 트랜잭션 시작 (실패 시 모든 작업 롤백)
        with transaction.atomic():
            # 1. 고객 확인
            customer = Customers.objects.get(code=customer_code)

            # 2. 등록된 결제 수단 확인
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id,
                customer_code=customer_code,
                is_active=True
            )

            # 빌링키 유효성 검증
            if payment_method.billing_key.startswith('TEMP_'):
                return JsonResponse({
                    'success': False,
                    'message': '임시 빌링키는 사용할 수 없습니다. 카드를 다시 등록해주세요.'
                }, status=400)

            # 3. 장바구니 항목 조회
            cart_items = ShoppingCart.objects.filter(
                id__in=cart_ids,
                customer_code=customer_code
            )

            if not cart_items.exists():
                return JsonResponse({
                    'success': False,
                    'message': '장바구니 항목을 찾을 수 없습니다.'
                }, status=404)

            # 4. 총 금액 계산
            total_amount = 0
            total_discount = 0

            for cart_item in cart_items:
                total_amount += cart_item.unit_price * cart_item.quantity
                discount_amount = (cart_item.unit_price * cart_item.quantity) - cart_item.final_price
                total_discount += discount_amount

            final_amount = total_amount - total_discount

            # 5. 배송지 정보 가져오기
            shipping_address = ''
            if shipping_address_id:
                try:
                    address = ShippingAddress.objects.get(
                        id=shipping_address_id,
                        customer_code=customer_code
                    )
                    shipping_address = f"{address.address} {address.detail_address}"
                except ShippingAddress.DoesNotExist:
                    pass

            # 6. 주문 생성
            order_number = generate_order_number()
            order = Order.objects.create(
                order_number=order_number,
                customer_code=customer_code,
                customer_name=customer.name,
                total_amount=total_amount,
                total_discount=total_discount,
                final_amount=final_amount,
                order_status='pending',
                payment_status='unpaid',
                payment_method='card',
                shipping_address=shipping_address,
                shipping_memo=shipping_memo,
                order_source='mobile'
            )

            # 7. 주문 상세 생성
            for cart_item in cart_items:
                product = Goods.objects.get(code=cart_item.product_code)

                price_info = calculate_discount_price(
                    product_code=cart_item.product_code,
                    customer_code=customer_code,
                    selected_year=cart_item.selected_year,
                    quantity=cart_item.quantity
                )

                OrderItem.objects.create(
                    order=order,
                    product_code=cart_item.product_code,
                    product_name=product.name,
                    brand=product.brand,
                    quantity=cart_item.quantity,
                    selected_year=cart_item.selected_year,
                    unit_price=price_info['unit_price'],
                    basic_discount_rate=price_info['basic_discount_rate'],
                    customer_discount_rate=price_info['customer_discount_rate'],
                    additional_discount_rate=price_info['additional_discount_rate'],
                    dot_discount_rate=price_info['dot_discount_rate'],
                    total_discount_rate=price_info['total_discount_rate'],
                    discounted_price=price_info['discounted_price'],
                    final_price=price_info['final_price']
                )

            # 8. 토스페이먼츠 빌링키 자동결제 API 호출
            url = f"https://api.tosspayments.com/v1/billing/{payment_method.billing_key}"

            secret_key = settings.TOSS_PAYMENTS_SECRET_KEY + ':'
            encoded_key = base64.b64encode(secret_key.encode()).decode()

            headers = {
                'Authorization': f'Basic {encoded_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'customerKey': customer_code,
                'amount': int(final_amount),
                'orderId': order_number,
                'orderName': f'{customer.name} 주문',
                'customerEmail': customer.email if hasattr(customer, 'email') and customer.email else None,
                'customerName': customer.name
            }

            logger.info(f"빌링키 자동결제 요청: order={order_number}, amount={final_amount}, billing_key={payment_method.billing_key[:20]}...")

            billing_response = requests.post(url, json=payload, headers=headers)
            billing_data = billing_response.json()

            if billing_response.status_code == 200:
                # 결제 성공
                payment_key = billing_data.get('paymentKey')
                transaction_key = billing_data.get('transactionKey')

                logger.info(f"빌링키 자동결제 성공: order={order_number}, payment_key={payment_key}")

                # 9. Payment 레코드 생성
                payment = Payment.objects.create(
                    order=order,
                    payment_method='card',
                    payment_amount=final_amount,
                    payment_status='completed',
                    payment_date=timezone.now(),
                    pg_name='TossPayments',
                    payment_key=payment_key,
                    transaction_id=transaction_key,
                    order_id_toss=order_number,
                    raw_response=json.dumps(billing_data, ensure_ascii=False)
                )

                # 10. 주문 상태 업데이트
                order.payment_status = 'paid'
                order.order_status = 'confirmed'
                order.confirmed_date = timezone.now()
                order.save()

                # 11. 재고 차감
                for item in order.items.all():
                    update_stock(
                        product_code=item.product_code,
                        year=item.selected_year,
                        quantity=item.quantity,
                        operation='subtract'
                    )

                # 12. 장바구니 삭제
                cart_items.delete()

                return JsonResponse({
                    'success': True,
                    'message': '결제가 완료되었습니다.',
                    'data': {
                        'order_number': order.order_number,
                        'order_id': order.id,
                        'payment_key': payment_key,
                        'amount': final_amount,
                        'payment_date': payment.payment_date.isoformat()
                    }
                })
            else:
                # 결제 실패 - 트랜잭션 롤백됨
                error_code = billing_data.get('code', 'UNKNOWN')
                error_message = billing_data.get('message', '결제에 실패했습니다')

                logger.error(f"빌링키 자동결제 실패: order={order_number}, code={error_code}, message={error_message}")

                # 주문을 취소 상태로 변경 (트랜잭션 내에서)
                order.order_status = 'cancelled'
                order.payment_status = 'failed'
                order.save()

                # 실패 Payment 레코드 생성
                Payment.objects.create(
                    order=order,
                    payment_method='card',
                    payment_amount=final_amount,
                    payment_status='failed',
                    pg_name='TossPayments',
                    order_id_toss=order_number,
                    memo=f'실패: {error_code} - {error_message}',
                    raw_response=json.dumps(billing_data, ensure_ascii=False)
                )

                return JsonResponse({
                    'success': False,
                    'message': f'결제 실패: {error_message}',
                    'error_code': error_code
                }, status=400)

    except Customers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '고객을 찾을 수 없습니다.'
        }, status=404)
    except PaymentMethod.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '등록된 결제 수단을 찾을 수 없습니다.'
        }, status=404)
    except requests.exceptions.RequestException as e:
        logger.error(f"빌링키 결제 API 호출 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '결제 중 네트워크 오류가 발생했습니다.'
        }, status=500)
    except Exception as e:
        logger.error(f"빌링키 자동결제 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'결제 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@require_session_auth
@require_http_methods(["GET"])
def api_order_list(request):
    """주문 목록 조회 API"""
    customer_code = request.GET.get('customer_code')

    if not customer_code:
        return JsonResponse({
            'success': False,
            'message': '고객 코드가 필요합니다.'
        }, status=400)

    # 해당 고객의 모든 주문 조회 (모바일 + ERP 전화주문 모두)
    # 고객이 모바일 로그인하면 자신의 모든 주문 내역을 볼 수 있음
    orders = Order.objects.filter(customer_code=customer_code).order_by('-order_date')

    result = {
        'success': True,
        'data': {
            'orders': [
                {
                    'id': order.id,
                    'order_number': order.order_number,
                    'order_date': timezone.localtime(order.order_date).strftime('%Y-%m-%d %H:%M:%S'),
                    'total_amount': order.total_amount,
                    'final_amount': order.final_amount,
                    'order_status': order.order_status,
                    'payment_status': order.payment_status,
                    'order_source': order.order_source,  # 주문 출처 (mobile/erp_phone/erp_import)
                    'items_count': order.items.count()
                }
                for order in orders
            ]
        }
    }

    return JsonResponse(result)


@require_session_auth
@require_http_methods(["GET"])
def api_order_detail(request, order_id):
    """주문 상세 조회 API"""
    customer_code = request.GET.get('customer_code')

    if not customer_code:
        return JsonResponse({
            'success': False,
            'message': '고객 코드가 필요합니다.'
        }, status=400)

    try:
        order = Order.objects.get(id=order_id, customer_code=customer_code)
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '주문을 찾을 수 없습니다.'
        }, status=404)

    items = order.items.all()

    result = {
        'success': True,
        'data': {
            'order_number': order.order_number,
            'order_date': timezone.localtime(order.order_date).strftime('%Y-%m-%d %H:%M:%S'),
            'customer_name': order.customer_name,
            'total_amount': order.total_amount,
            'total_discount': order.total_discount,
            'final_amount': order.final_amount,
            'order_status': order.order_status,
            'payment_status': order.payment_status,
            'payment_method': order.payment_method,
            'shipping_address': order.shipping_address,
            'shipping_memo': order.shipping_memo,
            'items': [
                {
                    'product_code': item.product_code,
                    'product_name': item.product_name,
                    'brand': item.brand,
                    'quantity': item.quantity,
                    'selected_year': item.selected_year,
                    'unit_price': item.unit_price,
                    'total_discount_rate': float(item.total_discount_rate),
                    'discounted_price': item.discounted_price,
                    'final_price': item.final_price
                }
                for item in items
            ]
        }
    }

    return JsonResponse(result)


@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_order_cancel(request, order_id):
    """주문 취소 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    customer_code = data.get('customer_code')
    cancel_reason = data.get('cancel_reason', '고객 요청')

    if not customer_code:
        return JsonResponse({'success': False, 'message': '고객 코드가 필요합니다.'}, status=400)

    try:
        order = Order.objects.get(id=order_id, customer_code=customer_code)

        # 이미 취소된 주문
        if order.order_status == 'cancelled':
            return JsonResponse({'success': False, 'message': '이미 취소된 주문입니다.'}, status=400)

        # 배송 완료된 주문은 취소 불가
        if order.order_status == 'delivered':
            return JsonResponse({'success': False, 'message': '배송 완료된 주문은 취소할 수 없습니다.'}, status=400)

        # 주문 취소 처리
        order.order_status = 'cancelled'
        order.save()

        # 결제 취소 처리 (카드 결제인 경우)
        if order.payment_method == 'card':
            payments = Payment.objects.filter(order=order, payment_status='completed')
            for payment in payments:
                if payment.payment_key:
                    # 토스페이먼츠 결제 취소 API 호출
                    try:
                        import requests
                        import base64
                        from django.conf import settings

                        url = f"{settings.TOSS_PAYMENTS_API_URL}/payments/{payment.payment_key}/cancel"
                        secret_key = settings.TOSS_PAYMENTS_SECRET_KEY + ':'
                        encoded_key = base64.b64encode(secret_key.encode()).decode()

                        headers = {
                            'Authorization': f'Basic {encoded_key}',
                            'Content-Type': 'application/json'
                        }

                        payload = {'cancelReason': cancel_reason}
                        response = requests.post(url, json=payload, headers=headers)

                        if response.status_code == 200:
                            payment.payment_status = 'cancelled'
                            payment.cancelled_date = timezone.now()
                            payment.memo = f'취소 사유: {cancel_reason}'
                            payment.save()

                            order.payment_status = 'refunded'
                            order.save()
                    except Exception as e:
                        print(f"결제 취소 API 오류: {e}")

        # 재고 복구
        for item in order.items.all():
            if item.selected_year:
                try:
                    selected_year_int = int(item.selected_year.split('/')[0]) if '/' in item.selected_year else int(item.selected_year)
                    update_stock(
                        product_code=item.product_code,
                        selected_year=selected_year_int,
                        quantity=item.quantity,
                        operation='add'
                    )
                except:
                    pass

        return JsonResponse({
            'success': True,
            'message': '주문이 취소되었습니다.',
            'data': {
                'order_number': order.order_number,
                'order_status': order.order_status,
                'payment_status': order.payment_status
            }
        })

    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': '주문을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'주문 취소 중 오류가 발생했습니다: {str(e)}'}, status=500)


@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_order_reorder(request, order_id):
    """재주문 API - 과거 주문의 상품들을 장바구니에 담기"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    customer_code = data.get('customer_code')

    if not customer_code:
        return JsonResponse({'success': False, 'message': '고객 코드가 필요합니다.'}, status=400)

    try:
        # 주문 조회
        order = Order.objects.get(id=order_id, customer_code=customer_code)

        # 주문 아이템 가져오기
        order_items = order.items.all()

        if not order_items:
            return JsonResponse({'success': False, 'message': '주문 상품이 없습니다.'}, status=400)

        # 장바구니에 추가된 상품 수 추적
        added_count = 0
        skipped_items = []

        for item in order_items:
            # 상품 정보 조회
            try:
                product = Goods.objects.get(code=item.product_code)
            except Goods.DoesNotExist:
                skipped_items.append({
                    'product_name': item.product_name,
                    'reason': '상품을 찾을 수 없습니다'
                })
                continue

            # 이미 장바구니에 있는지 확인
            existing_cart = ShoppingCart.objects.filter(
                customer_code=customer_code,
                product_code=item.product_code,
                selected_year=item.selected_year
            ).first()

            if existing_cart:
                # 기존 수량에 추가
                existing_cart.quantity += item.quantity
                existing_cart.save()
                added_count += 1
            else:
                # 새로 장바구니에 추가
                ShoppingCart.objects.create(
                    customer_code=customer_code,
                    product_code=item.product_code,
                    quantity=item.quantity,
                    selected_year=item.selected_year
                )
                added_count += 1

        # 결과 메시지 생성
        if added_count == 0:
            return JsonResponse({
                'success': False,
                'message': '장바구니에 담을 수 있는 상품이 없습니다.',
                'data': {'skipped_items': skipped_items}
            }, status=400)

        message = f'{added_count}개 상품이 장바구니에 담겼습니다.'
        if skipped_items:
            message += f' ({len(skipped_items)}개 상품 제외)'

        return JsonResponse({
            'success': True,
            'message': message,
            'data': {
                'added_count': added_count,
                'skipped_items': skipped_items
            }
        })

    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': '주문을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        import traceback
        print(f"재주문 오류: {e}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'message': f'재주문 중 오류가 발생했습니다: {str(e)}'}, status=500)


# ============================================
# 가격 계산 API
# ============================================

@require_http_methods(["GET"])
def api_calculate_price(request):
    """
    가격 계산 API

    Query Parameters:
        - product_code: 상품 코드 (필수)
        - customer_code: 고객 코드 (필수)
        - selected_year: 선택한 제조년도 (옵션)
        - quantity: 수량 (기본값: 1)
    """
    product_code = request.GET.get('product_code')
    customer_code = request.GET.get('customer_code')
    selected_year = request.GET.get('selected_year')
    quantity = int(request.GET.get('quantity', 1))

    if not product_code or not customer_code:
        return JsonResponse({
            'success': False,
            'message': '상품 코드와 고객 코드가 필요합니다.'
        }, status=400)

    if selected_year:
        selected_year = int(selected_year)

    price_info = calculate_discount_price(
        product_code=product_code,
        customer_code=customer_code,
        selected_year=selected_year,
        quantity=quantity
    )

    return JsonResponse({
        'success': True,
        'data': price_info
    })


@require_http_methods(["GET"])
def api_calculate_quote(request):
    """
    제안가 계산 API (카센터가 최종 고객에게 제시할 가격)

    Query Parameters:
        - product_code: 상품 코드 (필수)
        - customer_code: 고객 코드 (필수)
        - selected_year: 선택한 제조년도 (선택)
        - quantity: 수량 (기본값: 1)
        - margin_rate: 마진율 (선택, 기본값: 고객의 default_margin)
    """
    product_code = request.GET.get('product_code')
    customer_code = request.GET.get('customer_code')
    selected_year = request.GET.get('selected_year')
    quantity = int(request.GET.get('quantity', 1))
    margin_rate = request.GET.get('margin_rate')

    if not product_code or not customer_code:
        return JsonResponse({
            'success': False,
            'message': '상품 코드와 고객 코드가 필요합니다.'
        }, status=400)

    try:
        # 고객 정보 조회 (마진율 가져오기)
        customer = Customers.objects.get(code=customer_code)

        # 마진율 결정
        if margin_rate:
            margin_rate = float(margin_rate)
        else:
            margin_rate = float(customer.default_margin)

        if selected_year:
            selected_year = int(selected_year)

        # 매입 가격 정보 계산 (할인 적용된 가격)
        price_info = calculate_discount_price(
            product_code=product_code,
            customer_code=customer_code,
            selected_year=selected_year,
            quantity=quantity
        )

        # 제안가 계산 (매입가에 마진 추가)
        purchase_price = price_info['discounted_price']  # 단가
        purchase_total = price_info['final_price']  # 총액

        # 제안가 = 매입가 × (1 + 마진율/100)
        quote_price = int(purchase_price * (1 + margin_rate / 100))
        quote_total = int(purchase_total * (1 + margin_rate / 100))

        # 마진 금액
        margin_amount = quote_price - purchase_price
        margin_total = quote_total - purchase_total

        return JsonResponse({
            'success': True,
            'data': {
                # 매입 정보
                'purchase': {
                    'unit_price': price_info['unit_price'],  # 정가
                    'purchase_price': purchase_price,  # 할인된 매입 단가
                    'purchase_total': purchase_total,  # 할인된 매입 총액
                    'discount_rate': float(price_info['total_discount_rate']),  # 총 할인율
                },
                # 제안가 정보
                'quote': {
                    'margin_rate': margin_rate,  # 마진율
                    'margin_amount': margin_amount,  # 단가 마진
                    'margin_total': margin_total,  # 총 마진
                    'quote_price': quote_price,  # 제안 단가
                    'quote_total': quote_total,  # 제안 총액
                },
                # 상품 정보
                'product': {
                    'code': product_code,
                    'name': price_info['product_name'],
                    'brand': price_info['brand'],
                    'quantity': quantity,
                    'selected_year': selected_year,
                },
                # 할인 상세
                'discount_detail': {
                    'basic_discount': price_info['basic_discount_rate'],
                    'customer_discount': price_info['customer_discount_rate'],
                    'additional_discount': price_info['additional_discount_rate'],
                    'dot_discount': price_info['dot_discount_rate'],
                },
                'available_years': price_info.get('available_years', [])
            }
        })

    except Customers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '고객을 찾을 수 없습니다.'
        }, status=404)
    except Goods.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '상품을 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'제안가 계산 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


# ============================================
# 인증 API
# ============================================

def generate_customer_code():
    """새 고객 코드 생성 (C001, C002, ...)"""
    last_customer = Customers.objects.filter(code__startswith='C', code__regex=r'^C\d{3,}$').order_by('-code').first()
    if last_customer:
        try:
            last_number = int(last_customer.code[1:])
            new_number = last_number + 1
        except ValueError:
            new_number = 1
    else:
        new_number = 1

    return f'C{new_number:03d}'


@csrf_exempt
@require_http_methods(["POST"])
def api_auth_register(request):
    """
    모바일 회원가입 API

    Request Body:
        - enno: 사업자등록번호 또는 고객코드 (필수, TEST로 시작하면 테스트 계정)
        - name: 상호 (필수)
        - password: 비밀번호 (필수, 최소 4자)
        - rep: 대표자 (선택)
        - tel1: 전화번호 (선택)
        - tel3: 휴대전화 (선택)
    """
    try:
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({
            'success': False,
            'message': f'잘못된 요청입니다: {str(e)}'
        }, status=400)

    # 필수 필드 검증
    enno = data.get('enno', '').strip().replace('-', '')  # 하이픈 제거
    name = data.get('name', '').strip()
    password = data.get('password', '').strip()

    if not enno or not name or not password:
        return JsonResponse({
            'success': False,
            'message': '사업자등록번호, 상호, 비밀번호는 필수입니다.'
        }, status=400)

    if len(password) < 4:
        return JsonResponse({
            'success': False,
            'message': '비밀번호는 최소 4자 이상이어야 합니다.'
        }, status=400)

    # 고객코드 생성
    # TEST로 시작하면 그대로 사용, 아니면 사업자등록번호를 고객코드로 사용
    if enno.upper().startswith('TEST'):
        customer_code = enno.upper()  # TEST001, TEST002 등
    else:
        # 사업자등록번호 검증 (10자리 숫자)
        if not enno.isdigit() or len(enno) != 10:
            return JsonResponse({
                'success': False,
                'message': '사업자등록번호는 10자리 숫자여야 합니다.'
            }, status=400)
        customer_code = enno  # 사업자등록번호를 고객코드로 사용

    # 이미 등록된 고객코드 확인
    if Customers.objects.filter(code=customer_code).exists():
        return JsonResponse({
            'success': False,
            'message': '이미 등록된 사업자등록번호입니다.'
        }, status=400)

    # 비밀번호 해시화
    hashed_password = make_password(password)

    try:
        # 고객 생성
        customer = Customers.objects.create(
            code=customer_code,
            name=name,
            password=hashed_password,
            rep=data.get('rep', ''),
            tel1=data.get('tel1', ''),
            tel3=data.get('tel3', ''),
            enno=enno,
            is_registered=True,
            must_change_password=False
        )

        return JsonResponse({
            'success': True,
            'message': '회원가입이 완료되었습니다.',
            'data': {
                'customer_code': customer.code,
                'name': customer.name
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'회원가입 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_auth_login(request):
    """
    로그인 API

    Request Body:
        - customer_code: 사업자등록번호 또는 고객코드 (필수)
        - password: 비밀번호 (필수)
    """
    try:
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({
            'success': False,
            'message': f'잘못된 요청입니다: {str(e)}'
        }, status=400)

    customer_code = data.get('customer_code', '').strip().replace('-', '')  # 하이픈 제거
    password = data.get('password', '').strip()

    if not customer_code or not password:
        return JsonResponse({
            'success': False,
            'message': '사업자등록번호와 비밀번호는 필수입니다.'
        }, status=400)

    try:
        # TEST로 시작하는 경우 대문자로 변환
        if customer_code.upper().startswith('TEST'):
            customer_code = customer_code.upper()

        # 고객코드 또는 사업자번호로 검색
        customer = None

        # 1단계: 고객코드로 검색
        try:
            customer = Customers.objects.get(code=customer_code)
        except Customers.DoesNotExist:
            pass

        # 2단계: 사업자번호로 검색 (10자리 숫자면 하이픈 추가해서도 시도)
        if not customer:
            from django.db.models import Q

            # 하이픈 추가 형식 (예: 4101448232 → 410-14-48232)
            if len(customer_code) == 10 and customer_code.isdigit():
                formatted_enno = f"{customer_code[:3]}-{customer_code[3:5]}-{customer_code[5:]}"
                customer = Customers.objects.filter(
                    Q(enno=formatted_enno) | Q(enno=customer_code)
                ).first()
            else:
                customer = Customers.objects.filter(enno=customer_code).first()

        # 3단계: 고객을 찾지 못한 경우
        if not customer:
            return JsonResponse({
                'success': False,
                'message': '사업자등록번호 또는 비밀번호가 올바르지 않습니다.'
            }, status=401)

        # 비밀번호가 없는 경우
        if not customer.password:
            return JsonResponse({
                'success': False,
                'message': '비밀번호가 설정되지 않았습니다. 회원가입을 먼저 진행해주세요.'
            }, status=401)

        # 비밀번호 확인
        if check_password(password, customer.password):
            # 세션에 고객 코드 저장
            request.session['customer_code'] = customer.code

            return JsonResponse({
                'success': True,
                'message': '로그인 성공',
                'data': {
                    'customer_code': customer.code,
                    'name': customer.name,
                    'must_change_password': customer.must_change_password,
                    'login_time': int(time.time() * 1000)
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '사업자등록번호 또는 비밀번호가 올바르지 않습니다.'
            }, status=401)

    except Customers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '사업자등록번호 또는 비밀번호가 올바르지 않습니다.'
        }, status=401)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'로그인 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_auth_logout(request):
    """로그아웃 API"""
    try:
        if 'customer_code' in request.session:
            del request.session['customer_code']

        return JsonResponse({
            'success': True,
            'message': '로그아웃되었습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'로그아웃 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def api_auth_profile(request):
    """프로필 조회 API"""
    customer_code = request.session.get('customer_code') or request.GET.get('customer_code')

    if not customer_code:
        return JsonResponse({
            'success': False,
            'message': '로그인이 필요합니다.'
        }, status=401)

    try:
        customer = Customers.objects.get(code=customer_code)

        return JsonResponse({
            'success': True,
            'data': {
                'customer_code': customer.code,
                'name': customer.name,
                'rep': customer.rep,
                'tel1': customer.tel1,
                'tel3': customer.tel3,
                'enno': customer.enno,
                'is_registered': customer.is_registered,
                'membership_tier': customer.membership_tier,
                'membership_tier_display': customer.get_membership_tier_display(),
                'tier_updated_at': customer.tier_updated_at.strftime('%Y-%m-%d') if customer.tier_updated_at else None
            }
        })
    except Customers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '고객 정보를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'프로필 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_auth_change_password(request):
    """비밀번호 변경 API"""
    try:
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return JsonResponse({
            'success': False,
            'message': f'잘못된 요청입니다: {str(e)}'
        }, status=400)

    customer_code = request.session.get('customer_code') or data.get('customer_code')
    current_password = data.get('current_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    if not customer_code:
        return JsonResponse({
            'success': False,
            'message': '로그인이 필요합니다.'
        }, status=401)

    if not current_password or not new_password or not confirm_password:
        return JsonResponse({
            'success': False,
            'message': '모든 필드를 입력해주세요.'
        }, status=400)

    if new_password != confirm_password:
        return JsonResponse({
            'success': False,
            'message': '새 비밀번호가 일치하지 않습니다.'
        }, status=400)

    if len(new_password) < 4:
        return JsonResponse({
            'success': False,
            'message': '비밀번호는 최소 4자 이상이어야 합니다.'
        }, status=400)

    try:
        customer = Customers.objects.get(code=customer_code)

        # 현재 비밀번호 확인
        if not check_password(current_password, customer.password):
            return JsonResponse({
                'success': False,
                'message': '현재 비밀번호가 일치하지 않습니다.'
            }, status=401)

        # 새 비밀번호로 변경
        customer.password = make_password(new_password)
        customer.must_change_password = False  # 비밀번호 변경 완료
        customer.save()

        return JsonResponse({
            'success': True,
            'message': '비밀번호가 변경되었습니다.'
        })

    except Customers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '고객 정보를 찾을 수 없습니다.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'비밀번호 변경 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


# ============================================
# 토스페이먼츠 결제 API
# ============================================

@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_payment_prepare(request):
    """결제 준비 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    customer_code = data.get('customer_code')
    cart_ids = data.get('cart_ids', [])
    payment_method = data.get('payment_method', 'card')
    shipping_address = data.get('shipping_address', '')
    shipping_memo = data.get('shipping_memo', '')

    if not customer_code or not cart_ids:
        return JsonResponse({'success': False, 'message': '고객 코드와 장바구니 항목이 필요합니다.'}, status=400)

    try:
        customer = Customers.objects.get(code=customer_code)
        cart_items = ShoppingCart.objects.filter(id__in=cart_ids, customer_code=customer_code)

        if not cart_items.exists():
            return JsonResponse({'success': False, 'message': '장바구니 항목을 찾을 수 없습니다.'}, status=404)

        total_amount = 0
        total_discount = 0

        for cart_item in cart_items:
            total_amount += cart_item.unit_price * cart_item.quantity
            discount_amount = (cart_item.unit_price * cart_item.quantity) - cart_item.final_price
            total_discount += discount_amount

        final_amount = total_amount - total_discount
        order_number = generate_order_number()

        order = Order.objects.create(
            order_number=order_number,
            customer_code=customer_code,
            customer_name=customer.name,
            total_amount=total_amount,
            total_discount=total_discount,
            final_amount=final_amount,
            order_status='pending',
            payment_status='unpaid',
            payment_method=payment_method,
            shipping_address=shipping_address,
            shipping_memo=shipping_memo
        )

        for cart_item in cart_items:
            product = Goods.objects.get(code=cart_item.product_code)
            price_info = calculate_discount_price(
                product_code=cart_item.product_code,
                customer_code=customer_code,
                selected_year=cart_item.selected_year,
                quantity=cart_item.quantity
            )

            OrderItem.objects.create(
                order=order,
                product_code=cart_item.product_code,
                product_name=product.name,
                brand=product.brand,
                quantity=cart_item.quantity,
                selected_year=cart_item.selected_year,
                unit_price=price_info['unit_price'],
                basic_discount_rate=price_info['basic_discount_rate'],
                customer_discount_rate=price_info['customer_discount_rate'],
                additional_discount_rate=price_info['additional_discount_rate'],
                dot_discount_rate=price_info['dot_discount_rate'],
                total_discount_rate=price_info['total_discount_rate'],
                discounted_price=price_info['discounted_price'],
                final_price=price_info['final_price']
            )

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            payment_amount=final_amount,
            payment_status='pending',
            pg_name='TossPayments',
            order_id_toss=order_number
        )

        from django.conf import settings

        return JsonResponse({
            'success': True,
            'message': '결제 준비가 완료되었습니다.',
            'data': {
                'order_number': order_number,
                'order_id': order.id,
                'payment_id': payment.id,
                'amount': final_amount,
                'order_name': f'{customer.name} 주문',
                'customer_name': customer.name,
                'customer_code': customer_code,
                'client_key': settings.TOSS_PAYMENTS_CLIENT_KEY,
                'cart_ids': cart_ids
            }
        }, status=201)

    except Customers.DoesNotExist:
        return JsonResponse({'success': False, 'message': '고객을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'결제 준비 중 오류가 발생했습니다: {str(e)}'}, status=500)


@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_payment_confirm(request):
    """토스페이먼츠 결제 승인 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    payment_key = data.get('paymentKey')
    order_id = data.get('orderId')
    amount = data.get('amount')
    cart_ids = data.get('cart_ids', [])

    if not payment_key or not order_id or not amount:
        return JsonResponse({'success': False, 'message': '결제 키, 주문 ID, 금액이 필요합니다.'}, status=400)

    try:
        import requests
        import base64
        from django.conf import settings

        url = f"{settings.TOSS_PAYMENTS_API_URL}/payments/confirm"
        secret_key = settings.TOSS_PAYMENTS_SECRET_KEY + ':'
        encoded_key = base64.b64encode(secret_key.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'paymentKey': payment_key,
            'orderId': order_id,
            'amount': amount
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            order = Order.objects.get(order_number=order_id)
            payment = Payment.objects.get(order=order, payment_status='pending')

            payment.payment_key = payment_key
            payment.transaction_id = response_data.get('transactionKey')
            payment.payment_status = 'completed'
            payment.payment_date = timezone.now()
            payment.raw_response = json.dumps(response_data, ensure_ascii=False)
            payment.save()

            order.payment_status = 'paid'
            order.order_status = 'confirmed'
            order.confirmed_date = timezone.now()
            order.save()

            # 재고 차감
            for item in order.items.all():
                if item.selected_year:
                    update_stock(
                        product_code=item.product_code,
                        selected_year=item.selected_year,
                        quantity=item.quantity,
                        operation='subtract'
                    )

            if cart_ids:
                ShoppingCart.objects.filter(id__in=cart_ids).delete()

            return JsonResponse({
                'success': True,
                'message': '결제가 완료되었습니다.',
                'data': {
                    'order_number': order.order_number,
                    'payment_key': payment_key,
                    'amount': amount,
                    'payment_date': timezone.localtime(payment.payment_date).strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        else:
            error_code = response_data.get('code', 'UNKNOWN')
            error_message = response_data.get('message', '결제 승인에 실패했습니다.')

            try:
                order = Order.objects.get(order_number=order_id)
                payment = Payment.objects.get(order=order, payment_status='pending')
                payment.payment_status = 'failed'
                payment.memo = f'실패 코드: {error_code}, 메시지: {error_message}'
                payment.raw_response = json.dumps(response_data, ensure_ascii=False)
                payment.save()
                order.order_status = 'cancelled'
                order.save()
            except:
                pass

            return JsonResponse({'success': False, 'message': error_message, 'error_code': error_code}, status=400)

    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': '주문을 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'결제 승인 중 오류가 발생했습니다: {str(e)}'}, status=500)


@require_session_auth
@csrf_exempt
@require_http_methods(["POST"])
def api_payment_cancel(request):
    """결제 취소 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    payment_key = data.get('payment_key')
    cancel_reason = data.get('cancel_reason', '고객 요청')
    cancel_amount = data.get('cancel_amount')

    if not payment_key:
        return JsonResponse({'success': False, 'message': '결제 키가 필요합니다.'}, status=400)

    try:
        import requests
        import base64
        from django.conf import settings

        payment = Payment.objects.get(payment_key=payment_key)

        if payment.payment_status == 'cancelled':
            return JsonResponse({'success': False, 'message': '이미 취소된 결제입니다.'}, status=400)

        url = f"{settings.TOSS_PAYMENTS_API_URL}/payments/{payment_key}/cancel"
        secret_key = settings.TOSS_PAYMENTS_SECRET_KEY + ':'
        encoded_key = base64.b64encode(secret_key.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_key}',
            'Content-Type': 'application/json'
        }

        payload = {'cancelReason': cancel_reason}
        if cancel_amount:
            payload['cancelAmount'] = cancel_amount

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            payment.payment_status = 'cancelled'
            payment.cancelled_date = timezone.now()
            payment.memo = f'취소 사유: {cancel_reason}'
            payment.raw_response = json.dumps(response_data, ensure_ascii=False)
            payment.save()

            order = payment.order
            order.payment_status = 'refunded'
            order.order_status = 'cancelled'
            order.save()

            for item in order.items.all():
                update_stock(
                    product_code=item.product_code,
                    year=item.selected_year,
                    quantity=item.quantity,
                    operation='add'
                )

            return JsonResponse({
                'success': True,
                'message': '결제가 취소되었습니다.',
                'data': {
                    'payment_key': payment_key,
                    'cancelled_date': timezone.localtime(payment.cancelled_date).strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        else:
            error_code = response_data.get('code', 'UNKNOWN')
            error_message = response_data.get('message', '결제 취소에 실패했습니다.')
            return JsonResponse({'success': False, 'message': error_message, 'error_code': error_code}, status=400)

    except Payment.DoesNotExist:
        return JsonResponse({'success': False, 'message': '결제 정보를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'결제 취소 중 오류가 발생했습니다: {str(e)}'}, status=500)


@require_session_auth
@require_http_methods(["GET"])
def api_payment_status(request, payment_key):
    """결제 상태 조회 API"""
    try:
        import requests
        import base64
        from django.conf import settings

        url = f"{settings.TOSS_PAYMENTS_API_URL}/payments/{payment_key}"
        secret_key = settings.TOSS_PAYMENTS_SECRET_KEY + ':'
        encoded_key = base64.b64encode(secret_key.encode()).decode()

        headers = {'Authorization': f'Basic {encoded_key}'}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return JsonResponse({'success': True, 'data': response_data})
        else:
            return JsonResponse({'success': False, 'message': '결제 정보를 조회할 수 없습니다.'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'결제 조회 중 오류가 발생했습니다: {str(e)}'}, status=500)


# ============================================
# 배송지 주소 API
# ============================================

@require_http_methods(["GET"])
def api_shipping_addresses_list(request):
    """배송지 주소 목록 조회 API"""
    customer_code = request.GET.get('customer_code')

    if not customer_code:
        return JsonResponse({'success': False, 'message': '고객 코드가 필요합니다.'}, status=400)

    try:
        addresses = ShippingAddress.objects.filter(customer_code=customer_code).order_by('-is_default', '-created_at')

        addresses_data = []
        for addr in addresses:
            addresses_data.append({
                'id': addr.id,
                'recipient_name': addr.recipient_name,
                'phone_number': addr.phone_number,
                'postal_code': addr.postal_code,
                'address': addr.address,
                'address_detail': addr.address_detail,
                'full_address': addr.full_address,
                'is_default': addr.is_default,
                'created_at': timezone.localtime(addr.created_at).strftime('%Y-%m-%d %H:%M:%S')
            })

        return JsonResponse({
            'success': True,
            'data': {
                'addresses': addresses_data,
                'count': len(addresses_data)
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'배송지 목록 조회 중 오류가 발생했습니다: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_shipping_address_add(request):
    """배송지 주소 추가 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    customer_code = data.get('customer_code')
    recipient_name = data.get('recipient_name')
    phone_number = data.get('phone_number')
    address = data.get('address')

    if not all([customer_code, recipient_name, phone_number, address]):
        return JsonResponse({'success': False, 'message': '필수 항목을 입력해주세요.'}, status=400)

    try:
        # 고객이 첫 배송지를 추가하는 경우 자동으로 기본 배송지로 설정
        existing_count = ShippingAddress.objects.filter(customer_code=customer_code).count()
        is_default = data.get('is_default', existing_count == 0)

        address_obj = ShippingAddress.objects.create(
            customer_code=customer_code,
            recipient_name=recipient_name,
            phone_number=phone_number,
            postal_code=data.get('postal_code', ''),
            address=address,
            address_detail=data.get('address_detail', ''),
            is_default=is_default
        )

        return JsonResponse({
            'success': True,
            'message': '배송지가 추가되었습니다.',
            'data': {
                'id': address_obj.id,
                'recipient_name': address_obj.recipient_name,
                'phone_number': address_obj.phone_number,
                'postal_code': address_obj.postal_code,
                'address': address_obj.address,
                'address_detail': address_obj.address_detail,
                'full_address': address_obj.full_address,
                'is_default': address_obj.is_default
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'배송지 추가 중 오류가 발생했습니다: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST", "PUT"])
def api_shipping_address_update(request, address_id):
    """배송지 주소 수정 API"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    try:
        address_obj = ShippingAddress.objects.get(id=address_id)

        # 수정 가능한 필드 업데이트
        if 'recipient_name' in data:
            address_obj.recipient_name = data['recipient_name']
        if 'phone_number' in data:
            address_obj.phone_number = data['phone_number']
        if 'postal_code' in data:
            address_obj.postal_code = data['postal_code']
        if 'address' in data:
            address_obj.address = data['address']
        if 'address_detail' in data:
            address_obj.address_detail = data['address_detail']
        if 'is_default' in data:
            address_obj.is_default = data['is_default']

        address_obj.save()

        return JsonResponse({
            'success': True,
            'message': '배송지가 수정되었습니다.',
            'data': {
                'id': address_obj.id,
                'recipient_name': address_obj.recipient_name,
                'phone_number': address_obj.phone_number,
                'postal_code': address_obj.postal_code,
                'address': address_obj.address,
                'address_detail': address_obj.address_detail,
                'full_address': address_obj.full_address,
                'is_default': address_obj.is_default
            }
        })

    except ShippingAddress.DoesNotExist:
        return JsonResponse({'success': False, 'message': '배송지를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'배송지 수정 중 오류가 발생했습니다: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_shipping_address_delete(request, address_id):
    """배송지 주소 삭제 API"""
    try:
        address_obj = ShippingAddress.objects.get(id=address_id)
        customer_code = address_obj.customer_code
        was_default = address_obj.is_default

        address_obj.delete()

        # 삭제된 주소가 기본 배송지였다면, 다른 주소 중 하나를 기본 배송지로 설정
        if was_default:
            remaining_addresses = ShippingAddress.objects.filter(customer_code=customer_code).order_by('-created_at')
            if remaining_addresses.exists():
                first_address = remaining_addresses.first()
                first_address.is_default = True
                first_address.save()

        return JsonResponse({
            'success': True,
            'message': '배송지가 삭제되었습니다.'
        })

    except ShippingAddress.DoesNotExist:
        return JsonResponse({'success': False, 'message': '배송지를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'배송지 삭제 중 오류가 발생했습니다: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_shipping_address_set_default(request, address_id):
    """기본 배송지 설정 API"""
    try:
        address_obj = ShippingAddress.objects.get(id=address_id)

        # 이미 기본 배송지인 경우
        if address_obj.is_default:
            return JsonResponse({
                'success': True,
                'message': '이미 기본 배송지입니다.'
            })

        # 기본 배송지로 설정 (save() 메서드가 자동으로 다른 주소의 기본 설정 해제)
        address_obj.is_default = True
        address_obj.save()

        return JsonResponse({
            'success': True,
            'message': '기본 배송지로 설정되었습니다.'
        })

    except ShippingAddress.DoesNotExist:
        return JsonResponse({'success': False, 'message': '배송지를 찾을 수 없습니다.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'기본 배송지 설정 중 오류가 발생했습니다: {str(e)}'}, status=500)


# ============================================
# ERP 연동 상태 관리 API
# ============================================

@require_http_methods(["GET"])
def api_erp_status(request):
    """
    ERP 실시간 동기화 API 연결 상태 확인

    PythonAnywhere -> TgenAI -> ERP Server -> TgenAI -> PythonAnywhere
    """
    from django.conf import settings
    import requests
    import time

    status_info = {
        'success': False,
        'status': 'disconnected',
        'erp_api_url': settings.ERP_SYNC_API_URL,
        'response_time': None,
        'last_check': timezone.now().isoformat(),
        'error_message': None,
        'retry_count': 0
    }

    # ERP API 상태 확인 (헬스체크)
    retry_count = 0
    max_retries = settings.ERP_SYNC_RETRY_COUNT

    while retry_count < max_retries:
        try:
            start_time = time.time()

            # ERP API 헬스체크 엔드포인트 호출 (/health - 더 상세한 정보 제공)
            response = requests.get(
                f"{settings.ERP_SYNC_API_URL}/health",
                timeout=settings.ERP_SYNC_TIMEOUT
            )

            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)  # ms

            if response.status_code == 200:
                health_data = response.json()
                status_info.update({
                    'success': True,
                    'status': 'connected',
                    'response_time': response_time,
                    'retry_count': retry_count,
                    'database_status': health_data.get('database', 'unknown'),
                    'erp_goods_count': health_data.get('total_goods', 0)
                })
                break
            else:
                status_info['error_message'] = f'HTTP {response.status_code}'
                retry_count += 1

        except requests.exceptions.Timeout:
            status_info['error_message'] = 'Connection timeout'
            retry_count += 1

        except requests.exceptions.ConnectionError:
            status_info['error_message'] = 'Connection refused'
            retry_count += 1

        except Exception as e:
            status_info['error_message'] = str(e)
            retry_count += 1

        if retry_count < max_retries:
            time.sleep(settings.ERP_SYNC_RETRY_DELAY)

    status_info['retry_count'] = retry_count

    # 최근 상품 동기화 시간 조회
    try:
        latest_goods = Goods.objects.order_by('-updated_at').first()
        if latest_goods:
            status_info['last_sync_time'] = latest_goods.updated_at.isoformat()
            status_info['goods_count'] = Goods.objects.count()
    except Exception:
        pass

    return JsonResponse(status_info)


@csrf_exempt
@require_http_methods(["POST"])
def api_erp_reconnect(request):
    """
    ERP 연결 수동 재시도

    관리자가 수동으로 ERP 연결을 재시도할 수 있습니다.
    """
    from django.conf import settings
    import requests
    import time

    reconnect_info = {
        'success': False,
        'status': 'failed',
        'attempts': [],
        'total_attempts': 0,
        'reconnect_time': timezone.now().isoformat()
    }

    max_retries = settings.ERP_SYNC_RETRY_COUNT

    for attempt in range(max_retries):
        attempt_info = {
            'attempt_number': attempt + 1,
            'success': False,
            'response_time': None,
            'error': None
        }

        try:
            start_time = time.time()

            response = requests.get(
                f"{settings.ERP_SYNC_API_URL}/health",
                timeout=settings.ERP_SYNC_TIMEOUT
            )

            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)

            attempt_info['response_time'] = response_time

            if response.status_code == 200:
                health_data = response.json()
                attempt_info['success'] = True
                reconnect_info.update({
                    'success': True,
                    'status': 'connected',
                    'total_attempts': attempt + 1,
                    'database_status': health_data.get('database', 'unknown'),
                    'erp_goods_count': health_data.get('total_goods', 0)
                })
                reconnect_info['attempts'].append(attempt_info)
                break
            else:
                attempt_info['error'] = f'HTTP {response.status_code}'

        except requests.exceptions.Timeout:
            attempt_info['error'] = 'Connection timeout'

        except requests.exceptions.ConnectionError:
            attempt_info['error'] = 'Connection refused'

        except Exception as e:
            attempt_info['error'] = str(e)

        reconnect_info['attempts'].append(attempt_info)

        if attempt < max_retries - 1:
            time.sleep(settings.ERP_SYNC_RETRY_DELAY)

    reconnect_info['total_attempts'] = len(reconnect_info['attempts'])

    return JsonResponse(reconnect_info)

"""
모바일 API - ERP 실시간 연동
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .erp_api_client import ERPAPIClient
from .models import YearAllocation, ShoppingCart, Customers, PaymentMethod, GoodsDisplayName, Brand, BrandPattern
from .utils import calculate_discount_price
import json
import logging
import requests
import base64

logger = logging.getLogger(__name__)


# 브랜드 매핑
BRAND_MAPPING = {
    'kumho': {'keywords': ['금호', 'KUMHO'], 'code_prefix': ['K-']},
    'hankook': {'keywords': ['한국', 'HANKOOK'], 'code_prefix': ['H-']},
    'michelin': {'keywords': ['미쉐린', '미슐랭', 'MICHELIN'], 'code_prefix': ['M-']},
    'nexen': {'keywords': ['넥센', 'NEXEN'], 'code_prefix': ['N-']},
    'pirelli': {'keywords': ['피렐리', 'PIRELLI', 'P ZERO'], 'code_prefix': ['P-']},
    'bridgestone': {'keywords': ['브리지스톤', 'BRIDGESTONE'], 'code_prefix': ['BS-']},
    'continental': {'keywords': ['콘티넨탈', 'CONTINENTAL'], 'code_prefix': ['C-', 'CT-']},
    'dunlop': {'keywords': ['던롭', 'DUNLOP'], 'code_prefix': ['D-']},
    'yokohama': {'keywords': ['요코하마', 'YOKOHAMA'], 'code_prefix': ['Y-']},
    'goodyear': {'keywords': ['굳이어', 'GOODYEAR'], 'code_prefix': ['G-']},
}

# 타이어 코드 접두사 (사용 안 함 - 브랜드 기반 필터링으로 대체)
# TIRE_CODE_PREFIXES = [
#     'ANNAITE-', 'BFG-', 'BS-', 'C-', 'CT-', 'D-', 'G-', 'H-',
#     'HIFLY-', 'HILO-', 'K-', 'M-', 'MAXXIS-', 'N-', 'P-'
# ]


@require_http_methods(["GET"])
def api_products_erp(request):
    """
    ERP 실시간 상품 목록 API

    Query Parameters:
        - search: 검색어
        - brand: 단일 브랜드 (kumho, michelin 등)
        - brands: 다중 브랜드 (KUMHO,NEXEN,MICHELIN 등, 쉼표로 구분)
        - page: 페이지 번호 (기본값: 1)
        - page_size: 페이지 크기 (기본값: 20)
    """
    try:
        # 파라미터
        search = request.GET.get('search', '')
        brand = request.GET.get('brand', '').lower()
        brands = request.GET.get('brands', '')  # 다중 브랜드 지원
        customer_code = request.GET.get('customer_code', '')  # 고객 코드 추가
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        # 브랜드 리스트 구성
        brand_list = []
        if brands:
            # 다중 브랜드: KUMHO,NEXEN,MICHELIN -> [kumho, nexen, michelin]
            brand_list = [b.strip().lower() for b in brands.split(',') if b.strip()]
        elif brand:
            # 단일 브랜드
            brand_list = [brand]

        # ERP에서 상품 가져오기
        if brand_list:
            # 브랜드 필터: 전체 로드 후 필터링 (ERP search API 사용 안 함)
            erp_goods_count = ERPAPIClient.get_goods_count()
            erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=erp_goods_count)

            # 모든 브랜드의 키워드 및 코드 접두사 수집
            all_brand_keywords = []
            all_code_prefixes = []
            for brand_name in brand_list:
                brand_config = BRAND_MAPPING.get(brand_name, {})
                keywords = brand_config.get('keywords', [])
                code_prefixes = brand_config.get('code_prefix', [])
                all_brand_keywords.extend(keywords)
                all_code_prefixes.extend(code_prefixes)

            # 검색어 패턴 생성 (브랜드 + 검색어 조합)
            import re
            search_patterns = []
            if search:
                logger.info(f"📱 모바일 검색: 브랜드={brand_list}, 검색어='{search}'")
                numeric_only = re.sub(r'[^0-9]', '', search)
                search_patterns = [search]  # 원본 검색어

                # 3자리 이상 숫자: 타이어 사이즈 패턴 생성
                if len(numeric_only) >= 3 and numeric_only == search:
                    if len(numeric_only) == 3:
                        width = numeric_only
                        search_patterns.append(f"{width}/")
                    elif len(numeric_only) == 4:
                        width = numeric_only[:3]
                        aspect_partial = numeric_only[3]
                        search_patterns.append(f"{width}/{aspect_partial}")
                    elif len(numeric_only) == 5:
                        width = numeric_only[:3]
                        aspect_or_rim = numeric_only[3:5]
                        search_patterns.extend([
                            f"{width}/{aspect_or_rim}",
                            f"{width}R{aspect_or_rim}",
                        ])
                    elif len(numeric_only) == 6:
                        width = numeric_only[:3]
                        aspect = numeric_only[3:5]
                        rim_partial = numeric_only[5]
                        search_patterns.extend([
                            f"{width}/{aspect}R{rim_partial}",
                            f"{width}/{aspect}/{rim_partial}",
                        ])
                    else:
                        # 7자리 이상
                        width = numeric_only[:3]
                        aspect = numeric_only[3:5]
                        rim = numeric_only[5:7] if len(numeric_only) >= 7 else numeric_only[5:]
                        search_patterns.extend([
                            f"{width}/{aspect}R{rim}",
                            f"{width}/{aspect}/{rim}",
                            f"{width}-{aspect}-{rim}",
                        ])

                logger.info(f"🔍 검색 패턴: {search_patterns}")

            filtered_goods = []

            for goods in erp_goods_list:
                bun1 = (goods.get('bun1', '') or '').strip()
                name = (goods.get('name', '') or '').strip()
                code = (goods.get('code', '') or '').strip().upper()
                jaego = float(goods.get('jaego', 0))

                # 브랜드 매칭: 키워드 검색 + 코드 접두사 검색
                # bun1 필드 인코딩 문제 대비하여 name 필드에서도 검색
                keyword_match = any(
                    kw in bun1 or kw in bun1.upper() or kw in name or kw in name.upper()
                    for kw in all_brand_keywords
                )

                # 코드 접두사 매칭 (인코딩 문제와 무관한 안전장치)
                code_match = any(code.startswith(prefix) for prefix in all_code_prefixes)

                brand_match = keyword_match or code_match

                if not brand_match or jaego == 0:
                    continue

                # 검색어 필터링 (브랜드 매칭 후)
                if search_patterns:
                    search_matched = False
                    for pattern in search_patterns:
                        if pattern in code or pattern in name or pattern.upper() in name.upper():
                            search_matched = True
                            break
                    if not search_matched:
                        continue

                filtered_goods.append(goods)

            logger.info(f"✅ 브랜드+검색 필터 결과: {len(filtered_goods)}개")

            # 페이지네이션
            total_count = len(filtered_goods)
            start = (page - 1) * page_size
            end = start + page_size
            products_page = filtered_goods[start:end]

        else:
            # 검색 또는 일반 조회
            if search:
                # 검색어가 있으면 전체 로드 후 검색
                erp_goods_count = ERPAPIClient.get_goods_count()
                erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=erp_goods_count)

                # 검색 로직 (코드, 상품명에서 검색)
                # 숫자만 추출하여 타이어 사이즈 패턴 생성
                import re
                numeric_only = re.sub(r'[^0-9]', '', search)
                search_patterns = [search]  # 원본 검색어

                # 3자리 이상 숫자: 타이어 사이즈 패턴 생성
                if len(numeric_only) >= 3 and numeric_only == search:
                    if len(numeric_only) == 3:
                        # 3자리: width만 (예: 235)
                        width = numeric_only
                        search_patterns.append(f"{width}/")
                    elif len(numeric_only) == 4:
                        # 4자리: width (3) + aspect 일부 (1) (예: 2354 -> 235/4)
                        width = numeric_only[:3]
                        aspect_partial = numeric_only[3]
                        search_patterns.append(f"{width}/{aspect_partial}")
                    elif len(numeric_only) == 5:
                        # 5자리: width (3) + aspect (2) 또는 width (3) + rim (2)
                        width = numeric_only[:3]
                        aspect_or_rim = numeric_only[3:5]
                        search_patterns.extend([
                            f"{width}/{aspect_or_rim}",
                            f"{width}R{aspect_or_rim}",
                        ])
                    elif len(numeric_only) == 6:
                        # 6자리: width (3) + aspect (2) + rim 일부 (1)
                        width = numeric_only[:3]
                        aspect = numeric_only[3:5]
                        rim_partial = numeric_only[5]
                        search_patterns.extend([
                            f"{width}/{aspect}R{rim_partial}",
                            f"{width}/{aspect}/{rim_partial}",
                        ])
                    else:
                        # 7자리 이상: width (3) + aspect (2) + rim (2+)
                        width = numeric_only[:3]
                        aspect = numeric_only[3:5]
                        rim = numeric_only[5:7] if len(numeric_only) >= 7 else numeric_only[5:]
                        search_patterns.extend([
                            f"{width}/{aspect}R{rim}",
                            f"{width}/{aspect}/{rim}",
                            f"{width}-{aspect}-{rim}",
                        ])

                filtered_goods = []
                for goods in erp_goods_list:
                    code = (goods.get('code', '') or '').strip()
                    name = (goods.get('name', '') or '').strip()
                    jaego = float(goods.get('jaego', 0))

                    # 재고 없으면 제외
                    if jaego == 0:
                        continue

                    # 검색어 매칭 (모든 패턴 중 하나라도 매칭되면 포함)
                    matched = False
                    for pattern in search_patterns:
                        if pattern in code or pattern in name or pattern.upper() in name.upper():
                            matched = True
                            break

                    if matched:
                        filtered_goods.append(goods)

                # 페이지네이션
                total_count = len(filtered_goods)
                start = (page - 1) * page_size
                end = start + page_size
                products_page = filtered_goods[start:end]
            else:
                # 검색어 없으면 일반 조회 (페이지네이션)
                offset = (page - 1) * page_size
                erp_goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=page_size)
                erp_goods_count = ERPAPIClient.get_goods_count()

                # 재고 있는 것만
                products_page = [g for g in erp_goods_list if float(g.get('jaego', 0)) > 0]
                total_count = erp_goods_count

        # YearAllocation에서 할인율 가져오기
        goods_codes = [g.get('code') for g in products_page if g.get('code')]
        year_allocations_list = YearAllocation.objects.filter(goods_code__in=goods_codes)
        year_allocations = {ya.goods_code: ya for ya in year_allocations_list}

        # GoodsDisplayName 정보 가져오기 (한글명/영문명)
        display_names = {dn.goods_code: dn for dn in GoodsDisplayName.objects.filter(goods_code__in=goods_codes)}

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
        products = []
        for goods in products_page:
            code = goods.get('code')
            base_discount = 0.00
            final_discount_rate = 0.00
            final_price = int(goods.get('fixp', 0))

            # 고객 코드가 있으면 최종 할인가 계산 (기본할인+브랜드패턴할인+고객상품추가할인)
            if customer_code and code:
                discount_info = calculate_discount_price(code, customer_code)
                final_discount_rate = float(discount_info['total_discount_rate'])
                final_price = discount_info['discounted_price']
                base_discount = float(discount_info['basic_discount_rate'])
            else:
                # 고객 코드 없으면 기본할인만
                ya = year_allocations.get(code) if code else None
                if ya:
                    base_discount = float(ya.base_discount)
                    final_discount_rate = base_discount
                    final_price = int(int(goods.get('fixp', 0)) * (1 - base_discount / 100))

            # DOT 재고 정보 구성
            dot_inventory = []
            ya = year_allocations.get(code) if code else None
            if ya:
                base_price = int(goods.get('fixp', 0))

                # 2025년 (DOT 할인 없음, 상품 기본할인만)
                if ya.year_2025 > 0:
                    total_discount_2025 = base_discount
                    price_2025 = int(base_price * (1 - total_discount_2025 / 100))
                    dot_inventory.append({
                        'year': 2025,
                        'stock': ya.year_2025,
                        'discount': total_discount_2025,
                        'price': price_2025
                    })

                # 2024년
                if ya.year_2024 > 0:
                    total_discount_2024 = base_discount + float(ya.year_2024_discount)
                    price_2024 = int(base_price * (1 - total_discount_2024 / 100))
                    dot_inventory.append({
                        'year': 2024,
                        'stock': ya.year_2024,
                        'discount': total_discount_2024,
                        'price': price_2024
                    })

                # 2023년
                if ya.year_2023 > 0:
                    total_discount_2023 = base_discount + float(ya.year_2023_discount)
                    price_2023 = int(base_price * (1 - total_discount_2023 / 100))
                    dot_inventory.append({
                        'year': 2023,
                        'stock': ya.year_2023,
                        'discount': total_discount_2023,
                        'price': price_2023
                    })

                # 2022년
                if ya.year_2022 > 0:
                    total_discount_2022 = base_discount + float(ya.year_2022_discount)
                    price_2022 = int(base_price * (1 - total_discount_2022 / 100))
                    dot_inventory.append({
                        'year': 2022,
                        'stock': ya.year_2022,
                        'discount': total_discount_2022,
                        'price': price_2022
                    })

                # 2021년 이전
                if ya.year_2021_before > 0:
                    total_discount_2021 = base_discount + float(ya.year_2021_before_discount)
                    price_2021 = int(base_price * (1 - total_discount_2021 / 100))
                    dot_inventory.append({
                        'year': 2021,
                        'stock': ya.year_2021_before,
                        'discount': total_discount_2021,
                        'price': price_2021
                    })

            # 한글명/영문명 가져오기
            dn = display_names.get(code)
            korean_name = dn.korean_name if dn else None
            english_name = dn.english_name if dn else None

            # 브랜드/패턴별 성능표시 찾기
            brand_performance_boxes = []
            brand_logo_url = None
            product_brand_name = (goods.get('bun1') or '').strip()

            # 한글 브랜드명을 영문으로 변환 (BRAND_MAPPING 활용)
            normalized_brand_name = product_brand_name
            for eng_brand, mapping in BRAND_MAPPING.items():
                if product_brand_name in mapping['keywords']:
                    # Brand 모델에서 실제 브랜드명 찾기
                    for brand_key in all_brands.keys():
                        if brand_key.upper() == eng_brand.upper():
                            normalized_brand_name = brand_key
                            break
                    break

            if normalized_brand_name and normalized_brand_name in brand_performance_map:
                # 패턴 매칭 시도 (상품명에서 패턴명 찾기)
                matched_performance = None
                brand_patterns_dict = brand_performance_map[normalized_brand_name]['patterns']

                # 상품명에서 패턴명 검색 (가장 긴 패턴명부터 매칭)
                sorted_patterns = sorted(brand_patterns_dict.keys(), key=len, reverse=True)
                product_name = goods.get('name', '')
                for pattern_name in sorted_patterns:
                    if pattern_name in product_name or pattern_name in (korean_name or ''):
                        matched_performance = brand_patterns_dict[pattern_name]
                        break

                # 성능표시 박스 생성
                if matched_performance:
                    brand_performance_boxes = matched_performance.get_performance_boxes()
                    # 브랜드 로고는 Brand 모델에서 가져옴 (이미지 URL)
                    brand_logo_url = matched_performance.brand.logo_url

            products.append({
                'code': code,
                'name': goods.get('name', ''),
                'korean_name': korean_name,
                'english_name': english_name,
                'brand': goods.get('bun1', ''),
                'price': int(goods.get('fixp', 0)),
                'discount_rate': final_discount_rate,  # 최종 할인율 (기본+브랜드패턴+고객상품추가)
                'final_price': final_price,  # 최종 할인가
                'stock': int(goods.get('jaego', 0)),
                'brand_logo': f"/static/mobile/img/brands/{goods.get('bun1', 'default').lower()}.png",
                'dot_inventory': dot_inventory,
                'brand_performance_boxes': brand_performance_boxes,
                'brand_logo_url': brand_logo_url
            })

        return JsonResponse({
            'success': True,
            'data': {
                'products': products,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        })

    except Exception as e:
        logger.error(f"상품 목록 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_product_detail_erp(request, code):
    """
    ERP 실시간 상품 상세 API
    """
    try:
        # ERP에서 상품 조회
        erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=1, search=code)

        if not erp_goods_list:
            return JsonResponse({
                'success': False,
                'error': '상품을 찾을 수 없습니다.'
            }, status=404)

        goods = erp_goods_list[0]

        # YearAllocation에서 할인율 가져오기
        base_discount = 0.00
        try:
            year_allocation = YearAllocation.objects.get(goods_code=code)
            base_discount = float(year_allocation.base_discount)
        except YearAllocation.DoesNotExist:
            pass

        # 할인가 계산
        price = int(goods.get('fixp', 0))
        discount_amount = int(price * base_discount / 100)
        discounted_price = price - discount_amount

        return JsonResponse({
            'success': True,
            'data': {
                'code': code,
                'name': goods.get('name', ''),
                'brand': goods.get('bun1', ''),
                'price': price,
                'discount_rate': base_discount,
                'discount_amount': discount_amount,
                'discounted_price': discounted_price,
                'stock': int(goods.get('jaego', 0)),
                'brand_logo': f"/static/mobile/img/brands/{goods.get('bun1', 'default').lower()}.png"
            }
        })

    except Exception as e:
        logger.error(f"상품 상세 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_cart_add_simple(request):
    """
    장바구니 담기 (간단 버전)
    """
    try:
        data = json.loads(request.body)
        customer_code = data.get('customer_code')
        product_code = data.get('product_code')
        quantity = int(data.get('quantity', 1))

        if not customer_code or not product_code:
            return JsonResponse({
                'success': False,
                'error': '필수 파라미터가 없습니다.'
            }, status=400)

        # 고객 확인
        try:
            customer = Customers.objects.get(code=customer_code)
        except Customers.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '고객을 찾을 수 없습니다.'
            }, status=404)

        # 장바구니 추가 또는 업데이트
        cart_item, created = ShoppingCart.objects.get_or_create(
            customer=customer,
            product_code=product_code,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': '장바구니에 추가되었습니다.',
            'data': {
                'cart_id': cart_item.id,
                'quantity': cart_item.quantity
            }
        })

    except Exception as e:
        logger.error(f"장바구니 추가 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_payment_prepare_toss(request):
    """
    �佺���̸��� ���� �غ�
    """
    try:
        data = json.loads(request.body)
        customer_code = data.get('customer_code')
        amount = int(data.get('amount'))
        order_name = data.get('order_name', 'Ÿ�̾� �ֹ�')

        # �ֹ���ȣ ����
        import uuid
        order_id = f"ORDER_{uuid.uuid4().hex[:12].upper()}"

        return JsonResponse({
            'success': True,
            'data': {
                'order_id': order_id,
                'amount': amount,
                'order_name': order_name,
                'customer_name': customer_code
            }
        })

    except Exception as e:
        logger.error(f"���� �غ� ����: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_payment_confirm_toss(request):
    """
    �佺���̸��� ���� ����
    """
    try:
        data = json.loads(request.body)
        payment_key = data.get('paymentKey')
        order_id = data.get('orderId')
        amount = int(data.get('amount'))

        # �����δ� �佺���̸��� API�� ���� ��û
        # �׽�Ʈ ȯ�濡���� �ٷ� ���� ��ȯ
        
        return JsonResponse({
            'success': True,
            'message': '������ ���εǾ����ϴ�.',
            'data': {
                'payment_key': payment_key,
                'order_id': order_id,
                'amount': amount,
                'status': 'DONE'
            }
        })

    except Exception as e:
        logger.error(f"���� ���� ����: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def api_payment_methods_list(request):
    """결제 수단 목록 조회"""
    try:
        customer_code = request.GET.get('customer_code')
        if not customer_code:
            return JsonResponse({
                'success': False,
                'message': '고객코드가 필요합니다'
            }, status=400)

        methods = PaymentMethod.objects.filter(
            customer_code=customer_code,
            is_active=True
        ).order_by('-is_default', '-created_at')

        data = []
        for method in methods:
            data.append({
                'id': method.id,
                'payment_type': method.payment_type,
                'masked_info': method.masked_info,
                'nickname': method.nickname,
                'is_default': method.is_default,
                'card_company': method.card_company,
                'card_last4': method.card_last4,
                'account_bank': method.account_bank,
                'account_last4': method.account_last4,
                'created_at': method.created_at.strftime('%Y-%m-%d %H:%M:%S') if method.created_at else None
            })

        return JsonResponse({
            'success': True,
            'data': data
        })

    except Exception as e:
        logger.error(f"결제 수단 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '조회 중 오류가 발생했습니다',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_payment_method_delete(request, method_id):
    """결제 수단 삭제"""
    try:
        data = json.loads(request.body)
        customer_code = data.get('customer_code')

        if not customer_code:
            return JsonResponse({
                'success': False,
                'message': '고객코드가 필요합니다'
            }, status=400)

        method = PaymentMethod.objects.filter(
            id=method_id,
            customer_code=customer_code
        ).first()

        if not method:
            return JsonResponse({
                'success': False,
                'message': '결제 수단을 찾을 수 없습니다'
            }, status=404)

        method.delete()

        return JsonResponse({
            'success': True,
            'message': '결제 수단이 삭제되었습니다'
        })

    except Exception as e:
        logger.error(f"결제 수단 삭제 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '삭제 중 오류가 발생했습니다',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_payment_method_update_nickname(request, method_id):
    """결제 수단 별칭 수정"""
    try:
        data = json.loads(request.body)
        customer_code = data.get('customer_code')
        nickname = data.get('nickname', '')

        if not customer_code:
            return JsonResponse({
                'success': False,
                'message': '고객코드가 필요합니다'
            }, status=400)

        # 별칭 길이 체크
        if len(nickname) > 50:
            return JsonResponse({
                'success': False,
                'message': '별칭은 50자 이내로 입력해주세요'
            }, status=400)

        method = PaymentMethod.objects.filter(
            id=method_id,
            customer_code=customer_code
        ).first()

        if not method:
            return JsonResponse({
                'success': False,
                'message': '결제 수단을 찾을 수 없습니다'
            }, status=404)

        method.nickname = nickname
        method.save()

        return JsonResponse({
            'success': True,
            'message': '별칭이 수정되었습니다',
            'data': {
                'id': method.id,
                'nickname': method.nickname
            }
        })

    except Exception as e:
        logger.error(f"결제 수단 별칭 수정 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '수정 중 오류가 발생했습니다',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_payment_method_billing_auth(request):
    """빌링키 발급 (authKey 방식 - 토스페이먼츠 위젯)"""
    try:
        data = json.loads(request.body)
        auth_key = data.get('auth_key')
        customer_key = data.get('customer_key')

        if not auth_key or not customer_key:
            return JsonResponse({
                'success': False,
                'message': '필수 파라미터가 누락되었습니다 (auth_key, customer_key)'
            }, status=400)

        # 고객 확인
        try:
            customer = Customers.objects.get(code=customer_key)
        except Customers.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '고객을 찾을 수 없습니다'
            }, status=404)

        try:
            import requests
            import base64
            from django.conf import settings

            # 토스페이먼츠 빌링키 발급 API 호출 (authKey 사용)
            url = "https://api.tosspayments.com/v1/billing/authorizations/issue"

            # Secret Key를 Base64로 인코딩 (Basic Auth)
            secret_key = settings.TOSS_PAYMENTS_SECRET_KEY + ':'
            encoded_key = base64.b64encode(secret_key.encode()).decode()

            headers = {
                'Authorization': f'Basic {encoded_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'authKey': auth_key,
                'customerKey': customer_key
            }

            logger.info(f"빌링키 발급 요청 (authKey 방식): customerKey={customer_key}")

            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()

            logger.info(f"토스페이먼츠 응답 status_code: {response.status_code}")
            logger.info(f"토스페이먼츠 응답 body: {response_data}")

            if response.status_code == 200:
                # 빌링키 발급 성공
                billing_key = response_data.get('billingKey')
                card_company = response_data.get('card', {}).get('issuerCode', 'UNKNOWN')
                card_number = response_data.get('card', {}).get('number', '')

                if not billing_key:
                    raise ValueError('빌링키를 받지 못했습니다')

                logger.info(f"빌링키 발급 성공: customer_key={customer_key}, billing_key={billing_key[:20]}...")

                # 카드 마지막 4자리 추출
                card_last4 = card_number[-4:] if len(card_number) >= 4 else '0000'

                # PaymentMethod 생성
                method = PaymentMethod.objects.create(
                    customer_code=customer_key,
                    payment_type='CARD',
                    billing_key=billing_key,
                    card_company=card_company,
                    card_last4=card_last4,
                    card_type='신용',
                    nickname='',
                    is_default=True  # 첫 카드는 기본으로 설정
                )

                return JsonResponse({
                    'success': True,
                    'message': '카드가 등록되었습니다',
                    'data': {
                        'id': method.id,
                        'masked_info': method.masked_info,
                        'is_default': method.is_default
                    }
                })
            else:
                # 빌링키 발급 실패
                error_code = response_data.get('code', 'UNKNOWN')
                error_message = response_data.get('message', '카드 등록에 실패했습니다')

                logger.error(f"빌링키 발급 실패: code={error_code}, message={error_message}")

                return JsonResponse({
                    'success': False,
                    'message': f'카드 등록 실패: {error_message}'
                }, status=400)

        except requests.exceptions.RequestException as e:
            logger.error(f"빌링키 API 호출 오류: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': '카드 등록 중 네트워크 오류가 발생했습니다'
            }, status=500)
        except Exception as e:
            logger.error(f"카드 등록 오류: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'카드 등록 중 오류가 발생했습니다: {str(e)}'
            }, status=500)

    except Exception as e:
        logger.error(f"빌링키 발급 처리 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '등록 중 오류가 발생했습니다',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_payment_method_add(request):
    """결제 수단 등록 (카드/계좌)"""
    try:
        data = json.loads(request.body)
        customer_code = data.get('customer_code')
        payment_type = data.get('payment_type')  # 'CARD' or 'ACCOUNT'

        if not customer_code or not payment_type:
            return JsonResponse({
                'success': False,
                'message': '필수 파라미터가 누락되었습니다'
            }, status=400)

        # 고객 확인
        try:
            customer = Customers.objects.get(code=customer_code)
        except Customers.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '고객을 찾을 수 없습니다'
            }, status=404)

        if payment_type == 'CARD':
            # 카드 등록 (직접 입력 방식)
            card_number = data.get('card_number')  # 16자리 숫자
            card_expiry = data.get('card_expiry')  # MM/YY
            card_cvc = data.get('card_cvc')  # 3자리
            card_holder_name = data.get('card_holder_name')  # 카드 소유자 이름
            card_password = data.get('card_password')  # 카드 비밀번호 앞 2자리
            customer_identity_number = data.get('customer_identity_number')  # 생년월일 6자리 또는 사업자번호 10자리

            if not all([card_number, card_expiry, card_cvc, card_password, customer_identity_number]):
                return JsonResponse({
                    'success': False,
                    'message': '카드 정보를 모두 입력해주세요 (카드번호, 유효기간, CVC, 비밀번호 앞 2자리, 생년월일 또는 사업자번호)'
                }, status=400)

            # 카드번호 첫 자리로 카드사 자동 판별
            first_digit = card_number[0]
            card_company = {
                '4': 'VISA',
                '5': 'MasterCard',
                '3': 'American Express',
                '6': 'Discover',
                '9': 'BC카드'
            }.get(first_digit, '기타')

            # 카드번호 유효성 검사
            if len(card_number) != 16 or not card_number.isdigit():
                return JsonResponse({
                    'success': False,
                    'message': '카드번호는 16자리 숫자여야 합니다'
                }, status=400)

            # 유효기간 파싱
            try:
                expiry_month, expiry_year = card_expiry.split('/')
                if not (1 <= int(expiry_month) <= 12 and len(expiry_year) == 2):
                    raise ValueError
            except:
                return JsonResponse({
                    'success': False,
                    'message': '유효기간 형식이 올바르지 않습니다 (MM/YY)'
                }, status=400)

            # CVC 유효성 검사
            if len(card_cvc) != 3 or not card_cvc.isdigit():
                return JsonResponse({
                    'success': False,
                    'message': 'CVC는 3자리 숫자여야 합니다'
                }, status=400)

            # 카드 비밀번호 유효성 검사
            if len(card_password) != 2 or not card_password.isdigit():
                return JsonResponse({
                    'success': False,
                    'message': '카드 비밀번호 앞 2자리를 입력해주세요'
                }, status=400)

            # 생년월일/사업자번호 유효성 검사
            if len(customer_identity_number) not in [6, 10] or not customer_identity_number.isdigit():
                return JsonResponse({
                    'success': False,
                    'message': '생년월일 6자리 또는 사업자번호 10자리를 입력해주세요'
                }, status=400)

            try:
                import requests
                import base64
                from django.conf import settings

                # 토스페이먼츠 빌링키 발급 API 호출 (카드 정보 직접 전송)
                url = "https://api.tosspayments.com/v1/billing/authorizations/card"

                # Secret Key를 Base64로 인코딩 (Basic Auth)
                secret_key = settings.TOSS_PAYMENTS_SECRET_KEY + ':'
                encoded_key = base64.b64encode(secret_key.encode()).decode()

                headers = {
                    'Authorization': f'Basic {encoded_key}',
                    'Content-Type': 'application/json'
                }

                # 연도는 2자리로 유지 (30 그대로)
                # 월을 2자리로 패딩 (1 -> 01, 11 -> 11)
                padded_month = expiry_month.zfill(2)
                padded_year = expiry_year.zfill(2)  # YY 형식 (2자리)

                payload = {
                    'customerKey': customer_code,
                    'cardNumber': card_number,
                    'cardExpirationYear': padded_year,  # YY 형식으로 변경
                    'cardExpirationMonth': padded_month,
                    'cardPassword': card_password,
                    'customerIdentityNumber': customer_identity_number
                }

                # 디버깅: 민감정보 마스킹 후 전체 payload 로깅
                safe_payload = {
                    'customerKey': customer_code,
                    'cardNumber': f"{card_number[:4]}****{card_number[-4:]}",
                    'cardExpirationYear': padded_year,
                    'cardExpirationMonth': padded_month,
                    'cardPassword': '**',
                    'customerIdentityNumber': f"{customer_identity_number[:2]}****"
                }
                logger.info(f"빌링키 발급 요청 payload: {safe_payload}")

                response = requests.post(url, json=payload, headers=headers)
                response_data = response.json()

                # 디버깅: 응답 상태 코드와 전체 응답 로깅
                logger.info(f"토스페이먼츠 응답 status_code: {response.status_code}")
                logger.info(f"토스페이먼츠 응답 body: {response_data}")

                if response.status_code == 200:
                    # 빌링키 발급 성공
                    billing_key = response_data.get('billingKey')

                    if not billing_key:
                        raise ValueError('빌링키를 받지 못했습니다')

                    logger.info(f"빌링키 발급 성공: customer_code={customer_code}, billing_key={billing_key[:20]}...")

                    # PaymentMethod 생성 (실제 빌링키 저장)
                    method = PaymentMethod.objects.create(
                        customer_code=customer_code,
                        payment_type='CARD',
                        billing_key=billing_key,  # ✅ 실제 토스페이먼츠 빌링키
                        card_company=card_company,
                        card_last4=card_number[-4:],
                        card_type='신용',
                        nickname=data.get('nickname', ''),
                        is_default=data.get('is_default', False)
                    )

                    return JsonResponse({
                        'success': True,
                        'message': '카드가 등록되었습니다',
                        'data': {
                            'id': method.id,
                            'masked_info': method.masked_info,
                            'is_default': method.is_default
                        }
                    })
                else:
                    # 빌링키 발급 실패
                    error_code = response_data.get('code', 'UNKNOWN')
                    error_message = response_data.get('message', '카드 등록에 실패했습니다')

                    logger.error(f"빌링키 발급 실패: code={error_code}, message={error_message}")

                    return JsonResponse({
                        'success': False,
                        'message': f'카드 등록 실패: {error_message}'
                    }, status=400)

            except requests.exceptions.RequestException as e:
                logger.error(f"빌링키 API 호출 오류: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': '카드 등록 중 네트워크 오류가 발생했습니다'
                }, status=500)
            except Exception as e:
                logger.error(f"카드 등록 오류: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': f'카드 등록 중 오류가 발생했습니다: {str(e)}'
                }, status=500)

        elif payment_type == 'ACCOUNT':
            # 계좌 등록
            account_bank = data.get('account_bank')
            account_number = data.get('account_number')
            account_holder = data.get('account_holder')

            if not all([account_bank, account_number, account_holder]):
                return JsonResponse({
                    'success': False,
                    'message': '계좌 정보가 누락되었습니다'
                }, status=400)

            # 계좌번호 암호화 (간단히 마지막 4자리만 저장, 전체는 암호화)
            # TODO: 실제 운영에서는 암호화 라이브러리 사용
            from django.contrib.auth.hashers import make_password
            account_encrypted = make_password(account_number)
            account_last4 = account_number[-4:]

            # PaymentMethod 생성
            method = PaymentMethod.objects.create(
                customer_code=customer_code,
                payment_type='ACCOUNT',
                account_bank=account_bank,
                account_number_encrypted=account_encrypted,
                account_last4=account_last4,
                account_holder=account_holder,
                nickname=data.get('nickname', ''),
                is_default=data.get('is_default', False)
            )

            return JsonResponse({
                'success': True,
                'message': '계좌가 등록되었습니다',
                'data': {
                    'id': method.id,
                    'masked_info': method.masked_info,
                    'is_default': method.is_default
                }
            })

        else:
            return JsonResponse({
                'success': False,
                'message': '지원하지 않는 결제 수단입니다'
            }, status=400)

    except Exception as e:
        logger.error(f"결제 수단 등록 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '등록 중 오류가 발생했습니다',
            'error': str(e)
        }, status=500)


@csrf_exempt
def api_customer_info(request):
    """
    로그인한 사용자의 고객 정보 조회
    GET /api/mobile/customer/info/
    """
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'GET 요청만 가능합니다'
        }, status=405)

    # 세션에서 customer_code 가져오기
    customer_code = request.session.get('customer_code')

    if not customer_code:
        return JsonResponse({
            'success': False,
            'message': '로그인이 필요합니다'
        }, status=401)

    try:
        from .models import Customers

        customer = Customers.objects.get(code=customer_code)

        return JsonResponse({
            'success': True,
            'data': {
                'code': customer.code,
                'name': customer.name or '',
                'rep': customer.rep or '',
                'tel1': customer.tel1 or '',
                'tel3': customer.tel3 or '',
                'enno': customer.enno or ''
            }
        })

    except Customers.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '고객 정보를 찾을 수 없습니다'
        }, status=404)

    except Exception as e:
        logger.error(f"고객 정보 조회 오류: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '조회 중 오류가 발생했습니다',
            'error': str(e)
        }, status=500)

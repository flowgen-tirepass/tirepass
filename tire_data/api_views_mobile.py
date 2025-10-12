"""
모바일 API - ERP 실시간 연동
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .erp_api_client import ERPAPIClient
from .models import YearAllocation, ShoppingCart, Customers
import json
import logging

logger = logging.getLogger(__name__)


# 브랜드 매핑
BRAND_MAPPING = {
    'kumho': ['금호', 'KUMHO'],
    'hankook': ['한국', 'HANKOOK'],
    'michelin': ['미쉐린', '미슐랭', 'MICHELIN'],
    'nexen': ['넥센', 'NEXEN'],
    'pirelli': ['피렐리', 'PIRELLI'],
    'bridgestone': ['브리지스톤', 'BRIDGESTONE'],
    'continental': ['콘티넨탈', 'CONTINENTAL'],
    'dunlop': ['던롭', 'DUNLOP'],
    'yokohama': ['요코하마', 'YOKOHAMA'],
    'goodyear': ['굳이어', 'GOODYEAR'],
}

# 타이어 코드 접두사
TIRE_CODE_PREFIXES = [
    'ANNAITE-', 'BFG-', 'BS-', 'C-', 'CT-', 'D-', 'G-', 'H-',
    'HIFLY-', 'HILO-', 'K-', 'M-', 'MAXXIS-', 'N-', 'P-'
]


@require_http_methods(["GET"])
def api_products_erp(request):
    """
    ERP 실시간 상품 목록 API

    Query Parameters:
        - search: 검색어
        - brand: 브랜드 (kumho, michelin 등)
        - page: 페이지 번호 (기본값: 1)
        - page_size: 페이지 크기 (기본값: 20)
    """
    try:
        # 파라미터
        search = request.GET.get('search', '')
        brand = request.GET.get('brand', '').lower()
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        # ERP에서 상품 가져오기
        if brand:
            # 브랜드 필터: 전체 로드 후 필터링
            erp_goods_count = ERPAPIClient.get_goods_count()
            erp_goods_list = ERPAPIClient.get_goods_list(offset=0, limit=erp_goods_count, search=search)

            # 브랜드 필터링
            brand_keywords = BRAND_MAPPING.get(brand, [])
            filtered_goods = []

            for goods in erp_goods_list:
                bun1 = (goods.get('bun1', '') or '').strip()
                code = (goods.get('code', '') or '').strip().upper()
                jaego = float(goods.get('jaego', 0))

                # 브랜드 매칭 & 타이어 & 재고
                brand_match = any(kw in bun1 or kw in bun1.upper() for kw in brand_keywords)
                is_tire = any(code.startswith(prefix) for prefix in TIRE_CODE_PREFIXES)

                if brand_match and is_tire and jaego > 0:
                    filtered_goods.append(goods)

            # 페이지네이션
            total_count = len(filtered_goods)
            start = (page - 1) * page_size
            end = start + page_size
            products_page = filtered_goods[start:end]

        else:
            # 검색 또는 일반 조회
            offset = (page - 1) * page_size
            erp_goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=page_size, search=search)
            erp_goods_count = ERPAPIClient.get_goods_count()

            # 재고 있는 것만
            products_page = [g for g in erp_goods_list if float(g.get('jaego', 0)) > 0]
            total_count = erp_goods_count

        # YearAllocation에서 할인율 가져오기
        goods_codes = [g.get('code') for g in products_page if g.get('code')]
        year_allocations_list = YearAllocation.objects.filter(goods_code__in=goods_codes)
        year_allocations = {ya.goods_code: ya for ya in year_allocations_list}

        # 결과 구성
        products = []
        for goods in products_page:
            code = goods.get('code')
            base_discount = 0.00

            if code and code in year_allocations:
                base_discount = float(year_allocations[code].base_discount)

            products.append({
                'code': code,
                'name': goods.get('name', ''),
                'brand': goods.get('bun1', ''),
                'price': int(goods.get('fixp', 0)),
                'discount_rate': base_discount,
                'stock': int(goods.get('jaego', 0)),
                'brand_logo': f"/static/mobile/img/brands/{goods.get('bun1', 'default').lower()}.png"
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

"""
모바일 API - ERP 실시간 연동
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .erp_api_client import ERPAPIClient
from .models import YearAllocation, ShoppingCart, Customers, PaymentMethod
import json
import logging
import requests
import base64

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
            # 카드 등록 (토스 빌링키 사용)
            billing_key = data.get('billing_key')
            auth_key = data.get('auth_key')  # 카드 인증키 (토스 위젯에서 받은)

            if not auth_key:
                return JsonResponse({
                    'success': False,
                    'message': '카드 인증키가 필요합니다'
                }, status=400)

            # 토스 빌링키 발급 API 호출
            toss_secret = settings.TOSS_PAYMENTS_SECRET_KEY
            auth_header = base64.b64encode(f"{toss_secret}:".encode()).decode()

            try:
                # 빌링키 발급 요청
                response = requests.post(
                    f"{settings.TOSS_PAYMENTS_API_URL}/billing/authorizations/issue",
                    headers={
                        'Authorization': f'Basic {auth_header}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'authKey': auth_key,
                        'customerKey': customer_code
                    },
                    timeout=10
                )

                if response.status_code != 200:
                    logger.error(f"토스 빌링키 발급 실패: {response.text}")
                    return JsonResponse({
                        'success': False,
                        'message': '카드 등록에 실패했습니다. 카드 정보를 확인해주세요.'
                    }, status=400)

                toss_data = response.json()
                billing_key = toss_data.get('billingKey')
                card_info = toss_data.get('card', {})

                # PaymentMethod 생성
                method = PaymentMethod.objects.create(
                    customer_code=customer_code,
                    payment_type='CARD',
                    billing_key=billing_key,
                    card_company=card_info.get('issuerCode', ''),
                    card_last4=card_info.get('number', '')[-4:] if card_info.get('number') else '',
                    card_type=card_info.get('cardType', ''),
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

            except requests.RequestException as e:
                logger.error(f"토스 API 호출 오류: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': '카드 등록 중 오류가 발생했습니다'
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

"""
모바일 쇼핑몰 API Views
JSON 기반 REST API
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json

from tire_data.models import Goods, YearAllocation, Customers
from tire_data.models_shopping import ShoppingCart, Order, OrderItem, Payment


# ============================================
# 장바구니 API
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def cart_add(request):
    """
    장바구니에 상품 담기

    POST /mobile/api/cart/add
    Body: {
        "product_code": "상품코드",
        "quantity": 수량,
        "selected_year": "제조년도" (optional)
    }
    """
    try:
        data = json.loads(request.body)
        product_code = data.get('product_code')
        quantity = int(data.get('quantity', 1))
        selected_year = data.get('selected_year', '')

        # 고객 정보 조회
        customer = Customers.objects.filter(user_id=request.user.id).first()
        if not customer:
            return JsonResponse({
                'success': False,
                'error': '고객 정보를 찾을 수 없습니다.'
            }, status=400)

        # 상품 정보 조회
        try:
            goods = Goods.objects.get(code=product_code)
        except Goods.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '상품을 찾을 수 없습니다.'
            }, status=404)

        # 재고 확인
        if goods.jaego < quantity:
            return JsonResponse({
                'success': False,
                'error': f'재고가 부족합니다. (현재 재고: {goods.jaego}개)'
            }, status=400)

        # DOT 재고 확인 (선택한 경우)
        if selected_year:
            try:
                allocation = YearAllocation.objects.get(goods_code=product_code)
                year_field = f'year_{selected_year}'

                if hasattr(allocation, year_field):
                    year_qty = getattr(allocation, year_field)
                    if year_qty < quantity:
                        return JsonResponse({
                            'success': False,
                            'error': f'{selected_year}년 제조 재고가 부족합니다. (현재 재고: {year_qty}개)'
                        }, status=400)
            except YearAllocation.DoesNotExist:
                pass

        # 할인율 계산 (고객별 할인율 적용)
        discount_rate = calculate_discount_rate(customer.code, product_code, selected_year)

        # 가격 계산
        unit_price = goods.fixp
        discounted_price = int(unit_price * (1 - discount_rate / 100))
        final_price = discounted_price * quantity

        # 장바구니에 이미 있는 상품인지 확인
        cart_item, created = ShoppingCart.objects.get_or_create(
            customer_code=customer.enno,  # 사업자번호 사용
            product_code=product_code,
            selected_year=selected_year or None,
            defaults={
                'quantity': quantity,
                'unit_price': unit_price,
                'discount_rate': discount_rate,
                'final_price': final_price
            }
        )

        if not created:
            # 이미 있는 경우 수량 증가
            cart_item.quantity += quantity
            cart_item.final_price = discounted_price * cart_item.quantity
            cart_item.save()

        return JsonResponse({
            'success': True,
            'message': '장바구니에 담았습니다.',
            'cart_item': {
                'id': cart_item.id,
                'product_code': cart_item.product_code,
                'product_name': cart_item.product_name,
                'quantity': cart_item.quantity,
                'unit_price': int(cart_item.unit_price),
                'discount_rate': float(cart_item.discount_rate),
                'final_price': int(cart_item.final_price)
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
@login_required
def cart_list(request):
    """
    장바구니 조회

    GET /mobile/api/cart
    """
    try:
        # 고객 정보 조회
        customer = Customers.objects.filter(user_id=request.user.id).first()
        if not customer:
            return JsonResponse({
                'success': False,
                'error': '고객 정보를 찾을 수 없습니다.'
            }, status=400)

        # 장바구니 조회
        cart_items = ShoppingCart.objects.filter(
            customer_code=customer.enno
        ).order_by('-created_at')

        # JSON 변환
        items = []
        total_amount = 0

        for item in cart_items:
            item_data = {
                'id': item.id,
                'product_code': item.product_code,
                'product_name': item.product_name,
                'quantity': item.quantity,
                'selected_year': item.selected_year or '',
                'unit_price': int(item.unit_price),
                'discount_rate': float(item.discount_rate),
                'final_price': int(item.final_price)
            }
            items.append(item_data)
            total_amount += item.final_price

        return JsonResponse({
            'success': True,
            'items': items,
            'total_amount': int(total_amount),
            'count': len(items)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
@login_required
def cart_update(request, cart_id):
    """
    장바구니 수량 변경

    PUT /mobile/api/cart/<id>
    Body: {
        "quantity": 새로운_수량
    }
    """
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))

        if quantity < 1:
            return JsonResponse({
                'success': False,
                'error': '수량은 1개 이상이어야 합니다.'
            }, status=400)

        # 고객 정보 조회
        customer = Customers.objects.filter(user_id=request.user.id).first()
        if not customer:
            return JsonResponse({
                'success': False,
                'error': '고객 정보를 찾을 수 없습니다.'
            }, status=400)

        # 장바구니 항목 조회
        try:
            cart_item = ShoppingCart.objects.get(
                id=cart_id,
                customer_code=customer.enno
            )
        except ShoppingCart.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '장바구니 항목을 찾을 수 없습니다.'
            }, status=404)

        # 재고 확인
        goods = Goods.objects.get(code=cart_item.product_code)
        if goods.jaego < quantity:
            return JsonResponse({
                'success': False,
                'error': f'재고가 부족합니다. (현재 재고: {goods.jaego}개)'
            }, status=400)

        # 수량 및 가격 업데이트
        cart_item.quantity = quantity
        discounted_price = int(cart_item.unit_price * (1 - cart_item.discount_rate / 100))
        cart_item.final_price = discounted_price * quantity
        cart_item.save()

        return JsonResponse({
            'success': True,
            'message': '수량이 변경되었습니다.',
            'cart_item': {
                'id': cart_item.id,
                'quantity': cart_item.quantity,
                'final_price': int(cart_item.final_price)
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def cart_delete(request, cart_id):
    """
    장바구니에서 삭제

    DELETE /mobile/api/cart/<id>
    """
    try:
        # 고객 정보 조회
        customer = Customers.objects.filter(user_id=request.user.id).first()
        if not customer:
            return JsonResponse({
                'success': False,
                'error': '고객 정보를 찾을 수 없습니다.'
            }, status=400)

        # 장바구니 항목 조회 및 삭제
        try:
            cart_item = ShoppingCart.objects.get(
                id=cart_id,
                customer_code=customer.enno
            )
            cart_item.delete()

            return JsonResponse({
                'success': True,
                'message': '장바구니에서 삭제되었습니다.'
            })
        except ShoppingCart.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '장바구니 항목을 찾을 수 없습니다.'
            }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# 할인율 계산 함수
# ============================================

def calculate_discount_rate(customer_code, product_code, selected_year=None):
    """
    고객별 할인율 계산

    Args:
        customer_code: 고객 코드
        product_code: 상품 코드
        selected_year: 제조년도 (DOT)

    Returns:
        총 할인율 (%)
    """
    from tire_data.models import CustomerDiscount, CustomerProductDiscount, BrandGroup
    from datetime import date

    total_discount = Decimal('0.00')

    # 1. 상품 정보 조회
    try:
        goods = Goods.objects.get(code=product_code)
    except Goods.DoesNotExist:
        return total_discount

    # 2. 개별 상품 할인율 (우선순위 최상)
    try:
        product_discount = CustomerProductDiscount.objects.get(
            customer_code=customer_code,
            product_code=product_code,
            is_active=True
        )
        if product_discount.is_valid:
            total_discount += product_discount.additional_discount_rate
    except CustomerProductDiscount.DoesNotExist:
        pass

    # 3. 브랜드/그룹 할인율
    try:
        customer_discount = CustomerDiscount.objects.filter(
            customer_code=customer_code,
            brand=goods.brand,
            is_active=True
        ).order_by('-priority').first()

        if customer_discount and customer_discount.is_valid:
            total_discount += customer_discount.discount_rate
    except Exception:
        pass

    # 4. DOT 할인율 (제조년도별)
    if selected_year:
        try:
            allocation = YearAllocation.objects.get(goods_code=product_code)
            year_discount_field = f'year_{selected_year}_discount'

            if hasattr(allocation, year_discount_field):
                dot_discount = getattr(allocation, year_discount_field)
                if dot_discount:
                    total_discount += dot_discount
        except YearAllocation.DoesNotExist:
            pass

    # 5. 상품 기본 할인율
    try:
        allocation = YearAllocation.objects.get(goods_code=product_code)
        if allocation.base_discount:
            total_discount += allocation.base_discount
    except YearAllocation.DoesNotExist:
        pass

    return total_discount


# ============================================
# 주문 API
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
@login_required
@transaction.atomic
def order_create(request):
    """
    장바구니에서 주문 생성

    POST /mobile/api/order/create
    Body: {
        "cart_item_ids": [장바구니_ID_목록],
        "shipping_address": "배송지",
        "shipping_memo": "배송메모" (optional)
    }
    """
    try:
        data = json.loads(request.body)
        cart_item_ids = data.get('cart_item_ids', [])
        shipping_address = data.get('shipping_address', '')
        shipping_memo = data.get('shipping_memo', '')

        if not cart_item_ids:
            return JsonResponse({
                'success': False,
                'error': '주문할 상품을 선택해주세요.'
            }, status=400)

        # 고객 정보 조회
        customer = Customers.objects.filter(user_id=request.user.id).first()
        if not customer:
            return JsonResponse({
                'success': False,
                'error': '고객 정보를 찾을 수 없습니다.'
            }, status=400)

        # 장바구니 항목 조회
        cart_items = ShoppingCart.objects.filter(
            id__in=cart_item_ids,
            customer_code=customer.enno
        )

        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'error': '선택한 장바구니 항목을 찾을 수 없습니다.'
            }, status=404)

        # 재고 확인
        for item in cart_items:
            goods = Goods.objects.get(code=item.product_code)
            if goods.jaego < item.quantity:
                return JsonResponse({
                    'success': False,
                    'error': f'{goods.name} 상품의 재고가 부족합니다.'
                }, status=400)

            # DOT 재고 확인
            if item.selected_year:
                try:
                    allocation = YearAllocation.objects.get(goods_code=item.product_code)
                    year_field = f'year_{item.selected_year}'
                    if hasattr(allocation, year_field):
                        year_qty = getattr(allocation, year_field)
                        if year_qty < item.quantity:
                            return JsonResponse({
                                'success': False,
                                'error': f'{goods.name} ({item.selected_year}년 제조)의 재고가 부족합니다.'
                            }, status=400)
                except YearAllocation.DoesNotExist:
                    pass

        # 주문번호 생성 (TP + YYYYMMDD + 일련번호)
        from datetime import datetime
        today_str = datetime.now().strftime('%Y%m%d')
        last_order = Order.objects.filter(
            order_number__startswith=f'TP{today_str}'
        ).order_by('-order_number').first()

        if last_order:
            last_seq = int(last_order.order_number[-3:])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        order_number = f'TP{today_str}{new_seq:03d}'

        # 금액 계산
        total_amount = sum(item.unit_price * item.quantity for item in cart_items)
        final_amount = sum(item.final_price for item in cart_items)
        total_discount = total_amount - final_amount

        # 주문 생성
        order = Order.objects.create(
            order_number=order_number,
            customer_code=customer.code,
            customer_name=customer.name,
            total_amount=total_amount,
            total_discount=total_discount,
            final_amount=final_amount,
            order_status='pending',
            payment_status='unpaid',
            shipping_address=shipping_address,
            shipping_memo=shipping_memo,
            order_source='mobile'
        )

        # 주문 상세 생성
        for item in cart_items:
            goods = Goods.objects.get(code=item.product_code)

            OrderItem.objects.create(
                order=order,
                product_code=item.product_code,
                product_name=goods.name,
                brand=goods.brand,
                quantity=item.quantity,
                selected_year=item.selected_year or '',
                unit_price=item.unit_price,
                total_discount_rate=item.discount_rate,
                discounted_price=int(item.unit_price * (1 - item.discount_rate / 100)),
                final_price=item.final_price
            )

        # 장바구니에서 삭제
        cart_items.delete()

        return JsonResponse({
            'success': True,
            'message': '주문이 생성되었습니다.',
            'order': {
                'id': order.id,
                'order_number': order.order_number,
                'final_amount': int(order.final_amount),
                'order_status': order.order_status
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# 결제 API (토스페이먼츠)
# ============================================

@require_http_methods(["GET"])
def payment_success(request):
    """
    토스페이먼츠 결제 성공 콜백

    GET /mobile/payment/success?paymentKey=xxx&orderId=xxx&amount=xxx
    """
    try:
        payment_key = request.GET.get('paymentKey')
        order_id = request.GET.get('orderId')
        amount = request.GET.get('amount')

        if not all([payment_key, order_id, amount]):
            return JsonResponse({
                'success': False,
                'error': '필수 파라미터가 누락되었습니다.'
            }, status=400)

        # 주문 조회
        try:
            order = Order.objects.get(order_number=order_id)
        except Order.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '주문을 찾을 수 없습니다.'
            }, status=404)

        # 금액 검증
        if int(amount) != order.final_amount:
            return JsonResponse({
                'success': False,
                'error': '결제 금액이 일치하지 않습니다.'
            }, status=400)

        # 토스 승인 API 호출
        import requests
        import base64
        from django.conf import settings

        secret_key = getattr(settings, 'TOSS_SECRET_KEY', '')
        if not secret_key:
            return JsonResponse({
                'success': False,
                'error': '토스 시크릿 키가 설정되지 않았습니다.'
            }, status=500)

        # Base64 인코딩
        encoded = base64.b64encode(f"{secret_key}:".encode()).decode()

        # 승인 API 호출
        response = requests.post(
            f"https://api.tosspayments.com/v1/payments/{payment_key}",
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/json"
            },
            json={
                "orderId": order_id,
                "amount": amount
            },
            timeout=10
        )

        if response.status_code == 200:
            payment_data = response.json()

            # Payment 레코드 생성
            with transaction.atomic():
                Payment.objects.create(
                    order=order,
                    payment_method=payment_data.get('method', 'card'),
                    payment_amount=payment_data['totalAmount'],
                    payment_status='completed',
                    payment_key=payment_key,
                    order_id_toss=order_id,
                    transaction_id=payment_data.get('transactionKey'),
                    pg_name='토스페이먼츠',
                    payment_date=timezone.now(),
                    raw_response=json.dumps(payment_data, ensure_ascii=False)
                )

                # 주문 상태 변경
                order.order_status = 'confirmed'
                order.payment_status = 'paid'
                order.payment_method = payment_data.get('method', 'card')
                order.confirmed_date = timezone.now()
                order.save()

                # 재고 감소
                decrease_inventory(order)

            # 성공 페이지로 리다이렉트
            from django.shortcuts import redirect
            return redirect('payment_complete', order_id=order.id)

        else:
            # 승인 실패
            error_data = response.json()
            return JsonResponse({
                'success': False,
                'error': error_data.get('message', '결제 승인에 실패했습니다.'),
                'code': error_data.get('code')
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def payment_fail(request):
    """
    토스페이먼츠 결제 실패 콜백

    GET /mobile/payment/fail?code=xxx&message=xxx&orderId=xxx
    """
    code = request.GET.get('code', '')
    message = request.GET.get('message', '결제에 실패했습니다.')
    order_id = request.GET.get('orderId', '')

    return JsonResponse({
        'success': False,
        'error': message,
        'code': code,
        'order_id': order_id
    }, status=400)


# ============================================
# 재고 감소 함수
# ============================================

def decrease_inventory(order):
    """
    주문 완료 시 재고 감소

    Args:
        order: Order 객체
    """
    for item in order.items.all():
        # 1. Goods 재고 감소
        goods = Goods.objects.select_for_update().get(code=item.product_code)
        goods.jaego -= item.quantity
        goods.save()

        # 2. DOT 재고 감소 (YearAllocation)
        if item.selected_year:
            try:
                allocation = YearAllocation.objects.select_for_update().get(
                    goods_code=item.product_code
                )
                year_field = f'year_{item.selected_year}'

                if hasattr(allocation, year_field):
                    current_qty = getattr(allocation, year_field)
                    new_qty = max(0, current_qty - item.quantity)
                    setattr(allocation, year_field, new_qty)
                    allocation.save()
            except YearAllocation.DoesNotExist:
                pass

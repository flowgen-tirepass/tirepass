"""
유틸리티 함수 모듈
"""
from decimal import Decimal
from .models import (
    Goods, CustomerDiscount, CustomerProductDiscount,
    YearAllocation, BrandGroup, BrandGroupPattern
)


def calculate_discount_price(product_code, customer_code, selected_year=None, quantity=1):
    """
    할인율을 계산하여 최종 가격 반환

    Args:
        product_code: 상품 코드
        customer_code: 고객 코드
        selected_year: 선택한 제조년도 (DOT) - None이면 최신년도
        quantity: 수량

    Returns:
        dict: {
            'unit_price': 단가,
            'basic_discount_rate': 기본 할인율,
            'customer_discount_rate': 고객 브랜드/그룹 할인율,
            'additional_discount_rate': 고객 추가 할인율,
            'dot_discount_rate': DOT 할인율,
            'total_discount_rate': 총 할인율,
            'discounted_price': 할인 적용 단가,
            'final_price': 최종가격 (수량 포함),
            'available_years': 선택 가능한 제조년도 목록
        }
    """
    result = {
        'unit_price': 0,
        'basic_discount_rate': Decimal('0.00'),
        'customer_discount_rate': Decimal('0.00'),
        'additional_discount_rate': Decimal('0.00'),
        'dot_discount_rate': Decimal('0.00'),
        'total_discount_rate': Decimal('0.00'),
        'discounted_price': 0,
        'final_price': 0,
        'available_years': [],
        'brand': '',
        'product_name': ''
    }

    # 1. 상품 정보 조회
    try:
        product = Goods.objects.get(code=product_code)
    except Goods.DoesNotExist:
        return result

    result['unit_price'] = product.fixp
    result['brand'] = product.bun1 or ''
    result['product_name'] = product.name

    # 2. 기본 할인율 조회 (YearAllocation의 base_discount 우선, 없으면 Goods의 discount_rate)
    try:
        year_allocation = YearAllocation.objects.get(goods_code=product_code)
        # YearAllocation의 base_discount가 있으면 사용
        if year_allocation.base_discount is not None and year_allocation.base_discount > 0:
            result['basic_discount_rate'] = year_allocation.base_discount
        else:
            result['basic_discount_rate'] = product.discount_rate
    except YearAllocation.DoesNotExist:
        # YearAllocation이 없으면 Goods의 discount_rate 사용
        result['basic_discount_rate'] = product.discount_rate
        year_allocation = None

    # 3. 고객 브랜드/그룹 할인율 조회
    customer_discount = get_customer_discount(customer_code, product)
    if customer_discount:
        result['customer_discount_rate'] = customer_discount

    # 4. 고객 추가 할인율 조회 (개별 상품)
    try:
        product_discount = CustomerProductDiscount.objects.get(
            customer_code=customer_code,
            product_code=product_code,
            is_active=True
        )
        if product_discount.is_valid:
            result['additional_discount_rate'] = product_discount.additional_discount_rate
    except CustomerProductDiscount.DoesNotExist:
        pass

    # 5. DOT 할인율 조회
    if year_allocation:
        # 선택 가능한 제조년도 목록 (재고가 있는 년도만)
        available_years = []
        if year_allocation.year_2025 > 0:
            available_years.append({'year': 2025, 'quantity': year_allocation.year_2025, 'discount': Decimal('0.00')})
        if year_allocation.year_2024 > 0:
            available_years.append({'year': 2024, 'quantity': year_allocation.year_2024, 'discount': year_allocation.year_2024_discount})
        if year_allocation.year_2023 > 0:
            available_years.append({'year': 2023, 'quantity': year_allocation.year_2023, 'discount': year_allocation.year_2023_discount})
        if year_allocation.year_2022 > 0:
            available_years.append({'year': 2022, 'quantity': year_allocation.year_2022, 'discount': year_allocation.year_2022_discount})
        if year_allocation.year_2021_before > 0:
            available_years.append({'year': 2021, 'quantity': year_allocation.year_2021_before, 'discount': year_allocation.year_2021_before_discount})

        result['available_years'] = available_years

        # 선택된 년도의 할인율 적용 (문자열/정수 모두 처리)
        if selected_year:
            try:
                # selected_year를 정수로 변환
                year_int = int(selected_year)
                if year_int == 2024:
                    result['dot_discount_rate'] = year_allocation.year_2024_discount
                elif year_int == 2023:
                    result['dot_discount_rate'] = year_allocation.year_2023_discount
                elif year_int == 2022:
                    result['dot_discount_rate'] = year_allocation.year_2022_discount
                elif year_int == 2021:
                    result['dot_discount_rate'] = year_allocation.year_2021_before_discount
            except (ValueError, TypeError):
                # 변환 실패 시 무시
                pass

    # 6. 최종 가격 계산
    # 공식: 단가 × (1 - 기본할인/100) × (1 - 고객할인/100) × (1 - 추가할인/100) × (1 - DOT할인/100)
    unit_price = Decimal(str(result['unit_price']))
    basic_rate = Decimal(str(result['basic_discount_rate'])) / Decimal('100')
    customer_rate = Decimal(str(result['customer_discount_rate'])) / Decimal('100')
    additional_rate = Decimal(str(result['additional_discount_rate'])) / Decimal('100')
    dot_rate = Decimal(str(result['dot_discount_rate'])) / Decimal('100')

    # 단계별 할인 적용
    price_after_basic = unit_price * (Decimal('1') - basic_rate)
    price_after_customer = price_after_basic * (Decimal('1') - customer_rate)
    price_after_additional = price_after_customer * (Decimal('1') - additional_rate)
    price_after_dot = price_after_additional * (Decimal('1') - dot_rate)

    result['discounted_price'] = int(price_after_dot)
    result['final_price'] = int(price_after_dot) * quantity

    # 총 할인율 계산
    if unit_price > 0:
        total_discount = ((unit_price - price_after_dot) / unit_price) * Decimal('100')
        result['total_discount_rate'] = total_discount.quantize(Decimal('0.01'))

    return result


def get_customer_discount(customer_code, product):
    """
    고객별 브랜드/그룹 할인율 조회

    Args:
        customer_code: 고객 코드
        product: Goods 모델 인스턴스

    Returns:
        Decimal: 할인율 (0.00 ~ 100.00)
    """
    brand = product.bun1
    if not brand:
        return Decimal('0.00')

    # 상품이 속한 그룹 찾기
    product_groups = find_product_groups(product)

    # 고객 할인 정보 조회 (우선순위 높은 순)
    discounts = CustomerDiscount.objects.filter(
        customer_code=customer_code,
        brand=brand,
        is_active=True
    ).order_by('-priority')

    for discount in discounts:
        if not discount.is_valid:
            continue

        # 그룹이 지정된 경우
        if discount.group:
            if discount.group.id in product_groups:
                return discount.discount_rate
        # 브랜드 전체 할인
        else:
            return discount.discount_rate

    return Decimal('0.00')


def find_product_groups(product):
    """
    상품이 속한 그룹 ID 목록 반환

    Args:
        product: Goods 모델 인스턴스

    Returns:
        list: 그룹 ID 목록
    """
    brand = product.bun1
    product_code = product.code
    product_name = product.name

    if not brand:
        return []

    group_ids = []

    # 해당 브랜드의 모든 그룹 조회
    groups = BrandGroup.objects.filter(brand=brand, is_active=True)

    for group in groups:
        # 그룹의 패턴 조회
        patterns = BrandGroupPattern.objects.filter(group=group)

        for pattern in patterns:
            # 패턴 매칭 (상품코드 또는 상품명에 패턴이 포함되어 있는지)
            if pattern.pattern.upper() in product_code.upper() or pattern.pattern in product_name:
                group_ids.append(group.id)
                break  # 한 패턴이라도 매칭되면 해당 그룹에 포함

    return group_ids


def generate_order_number():
    """
    주문번호 생성
    형식: ORD20251007001 (ORD + 날짜 + 일련번호)

    Returns:
        str: 주문번호
    """
    from datetime import datetime
    from .models_shopping import Order

    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    prefix = f'ORD{date_str}'

    # 오늘 날짜의 마지막 주문번호 조회
    last_order = Order.objects.filter(
        order_number__startswith=prefix
    ).order_by('-order_number').first()

    if last_order:
        # 마지막 일련번호 추출 후 +1
        last_seq = int(last_order.order_number[-3:])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f'{prefix}{new_seq:03d}'


def update_stock(product_code, selected_year, quantity, operation='subtract'):
    """
    재고 업데이트

    Args:
        product_code: 상품 코드
        selected_year: 제조년도
        quantity: 수량
        operation: 'subtract'(차감) 또는 'add'(추가)

    Returns:
        bool: 성공 여부
    """
    try:
        allocation = YearAllocation.objects.get(goods_code=product_code)
    except YearAllocation.DoesNotExist:
        return False

    # 수량 계산
    change = quantity if operation == 'add' else -quantity

    # 해당 년도 재고 업데이트
    if selected_year == 2025:
        allocation.year_2025 = max(0, allocation.year_2025 + change)
    elif selected_year == 2024:
        allocation.year_2024 = max(0, allocation.year_2024 + change)
    elif selected_year == 2023:
        allocation.year_2023 = max(0, allocation.year_2023 + change)
    elif selected_year == 2022:
        allocation.year_2022 = max(0, allocation.year_2022 + change)
    elif selected_year == 2021:
        allocation.year_2021_before = max(0, allocation.year_2021_before + change)
    else:
        return False

    allocation.save()

    # 전체 재고도 업데이트
    try:
        product = Goods.objects.get(code=product_code)
        product.jaego = max(0, product.jaego + change)
        product.save()
    except Goods.DoesNotExist:
        pass

    return True

"""
유틸리티 함수 모듈
"""
from decimal import Decimal
from .models import (
    Goods, CustomerDiscount, CustomerProductDiscount,
    YearAllocation, BrandGroup, BrandGroupPattern, Customers
)


def calculate_discount_price(product_code, customer_code, selected_year=None, quantity=1):
    result = {
        'unit_price': 0,
        'basic_discount_rate': Decimal('0.00'),
        'customer_discount_rate': Decimal('0.00'),
        'additional_discount_rate': Decimal('0.00'),
        'membership_discount_rate': Decimal('0.00'),
        'dot_discount_rate': Decimal('0.00'),
        'total_discount_rate': Decimal('0.00'),
        'discounted_price': 0,
        'final_price': 0,
        'available_years': [],
        'brand': '',
        'product_name': ''
    }

    try:
        product = Goods.objects.get(code=product_code)
    except Goods.DoesNotExist:
        return result

    result['unit_price'] = product.fixp
    result['brand'] = product.bun1 or ''
    result['product_name'] = product.name
    result['basic_discount_rate'] = product.discount_rate

    try:
        year_allocation = YearAllocation.objects.get(goods_code=product_code)
    except YearAllocation.DoesNotExist:
        year_allocation = None

    customer_discount = get_customer_discount(customer_code, product)
    if customer_discount:
        result['customer_discount_rate'] = customer_discount

    # 4. 고객 추가 할인율 조회 (개별 상품)
    product_discount = None
    try:
        product_discount = CustomerProductDiscount.objects.get(
            customer_code=customer_code,
            product_code=product_code,
            is_active=True
        )
    except CustomerProductDiscount.DoesNotExist:
        if product.bun1 and product.name:
            candidate_discounts = CustomerProductDiscount.objects.filter(
                customer_code=customer_code,
                brand=product.bun1,
                is_active=True
            )
            for discount in candidate_discounts:
                try:
                    discount_product = Goods.objects.get(code=discount.product_code)
                    if discount_product.name == product.name:
                        product_discount = discount
                        break
                except Goods.DoesNotExist:
                    continue

    if product_discount and product_discount.is_valid:
        result['additional_discount_rate'] = product_discount.additional_discount_rate

    try:
        customer = Customers.objects.get(code=customer_code)
        result['membership_discount_rate'] = Decimal(str(customer.membership_discount_rate))
    except Customers.DoesNotExist:
        pass

    if year_allocation:
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

        if selected_year:
            try:
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
                pass

    unit_price = Decimal(str(result['unit_price']))
    total_discount_rate = (
        Decimal(str(result['basic_discount_rate'])) +
        Decimal(str(result['customer_discount_rate'])) +
        Decimal(str(result['additional_discount_rate'])) +
        Decimal(str(result['membership_discount_rate'])) +
        Decimal(str(result['dot_discount_rate']))
    )
    result['total_discount_rate'] = total_discount_rate.quantize(Decimal('0.01'))
    discounted_price = unit_price * (Decimal('1') - total_discount_rate / Decimal('100'))
    result['discounted_price'] = int(discounted_price)
    result['final_price'] = int(discounted_price) * quantity
    return result


def get_customer_discount(customer_code, product):
    brand_name = product.bun1
    if not brand_name:
        return Decimal('0.00')
    try:
        from .models import Brand, BrandPattern, CustomerBrandDiscount
        brand = Brand.objects.get(name=brand_name, is_active=True)
    except Brand.DoesNotExist:
        return Decimal('0.00')

    discounts = CustomerBrandDiscount.objects.filter(
        customer__code=customer_code,
        brand=brand,
        is_active=True
    ).order_by('-priority')

    for discount in discounts:
        if not discount.is_valid:
            continue
        if discount.pattern:
            pattern_name = discount.pattern.pattern_name
            if pattern_name and (pattern_name in product.name or pattern_name in product.code):
                return discount.discount_rate

    for discount in discounts:
        if not discount.is_valid:
            continue
        if not discount.pattern:
            return discount.discount_rate

    return Decimal('0.00')


def find_product_groups(product):
    brand = product.bun1
    product_code = product.code
    product_name = product.name
    if not brand:
        return []
    group_ids = []
    groups = BrandGroup.objects.filter(brand=brand, is_active=True)
    for group in groups:
        patterns = BrandGroupPattern.objects.filter(group=group)
        for pattern in patterns:
            if pattern.pattern.upper() in product_code.upper() or pattern.pattern in product_name:
                group_ids.append(group.id)
                break
    return group_ids


def generate_order_number():
    from datetime import datetime
    from .models_shopping import Order
    today = datetime.now()
    date_str = today.strftime('%Y%m%d')
    prefix = f'ORD{date_str}'
    last_order = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()
    if last_order:
        last_seq = int(last_order.order_number[-3:])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    return f'{prefix}{new_seq:03d}'


def update_stock(product_code, selected_year, quantity, operation='subtract'):
    try:
        allocation = YearAllocation.objects.get(goods_code=product_code)
    except YearAllocation.DoesNotExist:
        return False
    try:
        if isinstance(selected_year, str):
            year_int = int(selected_year.split('/')[0])
        else:
            year_int = int(selected_year)
    except (ValueError, TypeError):
        return False
    change = quantity if operation == 'add' else -quantity
    if year_int == 2025:
        allocation.year_2025 = max(0, allocation.year_2025 + change)
    elif year_int == 2024:
        allocation.year_2024 = max(0, allocation.year_2024 + change)
    elif year_int == 2023:
        allocation.year_2023 = max(0, allocation.year_2023 + change)
    elif year_int == 2022:
        allocation.year_2022 = max(0, allocation.year_2022 + change)
    elif year_int == 2021:
        allocation.year_2021_before = max(0, allocation.year_2021_before + change)
    else:
        return False
    allocation.save()
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"재고 업데이트 완료: {product_code} (년도={year_int}, 변경량={change})")
    return True

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from tire_data.models import Goods, Customers, YearAllocation
from tire_data.models_shopping import Order, OrderItem, Payment, ShippingAddress
import re

def mobile_intro(request):
    """모바일 인트로/스플래시 페이지"""
    # 로그인된 사용자는 홈으로 리다이렉트
    if request.user.is_authenticated:
        return redirect('mobile_index')
    return render(request, 'mobile/intro.html')

def mobile_login(request):
    """모바일 로그인 페이지"""
    if request.user.is_authenticated:
        return redirect('mobile_index')

    if request.method == 'POST':
        business_number = request.POST.get('business_number', '')
        password = request.POST.get('password', '')

        # 사업자번호를 username으로 사용
        user = authenticate(request, username=business_number, password=password)

        if user is not None:
            login(request, user)

            # 비밀번호 변경이 필요한지 확인
            try:
                customer = Customers.objects.get(enno__contains=business_number)
                if customer.must_change_password:
                    messages.warning(request, '보안을 위해 비밀번호를 변경해주세요.')
                    return redirect('mobile_change_password')
            except Customers.DoesNotExist:
                pass

            next_url = request.GET.get('next', 'mobile_index')
            return redirect(next_url)
        else:
            messages.error(request, '사업자번호 또는 비밀번호가 올바르지 않습니다.')

    return render(request, 'mobile/login.html')

def mobile_logout(request):
    """모바일 로그아웃"""
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('mobile_intro')

@login_required
def mobile_change_password(request):
    """비밀번호 변경 페이지"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # 현재 비밀번호 확인
        if not request.user.check_password(current_password):
            messages.error(request, '현재 비밀번호가 올바르지 않습니다.')
            return render(request, 'mobile/change_password.html')

        # 새 비밀번호 확인
        if new_password != confirm_password:
            messages.error(request, '새 비밀번호가 일치하지 않습니다.')
            return render(request, 'mobile/change_password.html')

        # 비밀번호 강도 체크
        if len(new_password) < 8:
            messages.error(request, '비밀번호는 최소 8자 이상이어야 합니다.')
            return render(request, 'mobile/change_password.html')

        # 비밀번호 변경
        request.user.set_password(new_password)
        request.user.save()

        # 고객 정보 업데이트
        try:
            customer = Customers.objects.get(enno__contains=request.user.username)
            customer.must_change_password = False
            customer.save()
        except Customers.DoesNotExist:
            pass

        messages.success(request, '비밀번호가 성공적으로 변경되었습니다. 다시 로그인해주세요.')
        logout(request)
        return redirect('mobile_login')

    return render(request, 'mobile/change_password.html')

def fix_storage(request):
    """localStorage 초기화 긴급 수정 페이지"""
    return render(request, 'mobile/fix_storage.html')

def mobile_index(request):
    """모바일 메인 페이지"""
    goods_count = Goods.objects.count()
    customers_count = Customers.objects.count()

    context = {
        'goods_count': goods_count,
        'customers_count': customers_count,
    }
    return render(request, 'mobile/index.html', context)

def mobile_search(request):
    """모바일 검색 페이지"""
    # 페이지당 표시 수 (기본값 30)
    per_page = int(request.GET.get('per_page', 30))

    # 정렬 옵션 (기본값 default)
    sort_order = request.GET.get('sort', 'default')

    # 검색어
    search_query = request.GET.get('q', '')

    # 브랜드 필터
    brand_filter = request.GET.get('brand', '')

    # 타이어만 보기 옵션
    tire_only = request.GET.get('tire_only', '')

    # 재고 있는 상품만 보기
    in_stock = request.GET.get('in_stock', '')

    # 기본 쿼리셋
    goods = Goods.objects.all()

    # 검색어 필터링
    if search_query:
        # 숫자만 추출하여 검색 (특수문자, 영문 제거)
        numeric_query = re.sub(r'[^0-9]', '', search_query)

        if numeric_query:  # 숫자가 포함된 검색어
            # 숫자를 기반으로 여러 패턴 생성
            # 예: 2057015 -> 205/70R15, 205/70/15, 205-70-15 등
            search_patterns = []

            # 타이어 사이즈 패턴 매칭 (예: 2057015 -> 205/70*15)
            if len(numeric_query) >= 6:
                # 첫 3자리는 폭, 다음 2자리는 편평비, 나머지는 인치
                width = numeric_query[:3]
                if len(numeric_query) >= 5:
                    aspect = numeric_query[3:5]
                    if len(numeric_query) >= 7:
                        rim = numeric_query[5:7]
                        # 다양한 패턴으로 검색
                        search_patterns.extend([
                            f"{width}/{aspect}R{rim}",
                            f"{width}/{aspect}/{rim}",
                            f"{width}-{aspect}-{rim}",
                            f"{width} {aspect} {rim}",
                        ])

            # 정확한 숫자 포함 검색
            q_filter = Q()

            # 원본 검색어로도 검색
            q_filter |= Q(code__icontains=search_query)
            q_filter |= Q(name__icontains=search_query)

            # 숫자만으로도 검색
            q_filter |= Q(name__icontains=numeric_query)

            # 생성된 패턴들로 검색
            for pattern in search_patterns:
                q_filter |= Q(name__icontains=pattern)

            goods = goods.filter(q_filter)
        else:
            # 숫자가 없는 경우 일반 검색 (브랜드명 등)
            goods = goods.filter(
                Q(code__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(bun1__icontains=search_query) |
                Q(brand__icontains=search_query)
            )

    # 브랜드 필터
    if brand_filter:
        goods = goods.filter(Q(brand=brand_filter) | Q(bun1=brand_filter))

    # 타이어만 보기
    if tire_only:
        goods = goods.filter(is_tire=True)

    # 재고가 있는 상품만
    if in_stock:
        goods = goods.filter(jaego__gt=0)

    # 정렬 적용
    if sort_order == 'price_asc':
        goods = goods.order_by('fixp')
    elif sort_order == 'price_desc':
        goods = goods.order_by('-fixp')
    elif sort_order == 'stock_desc':
        goods = goods.order_by('-jaego')
    elif sort_order == 'name':
        goods = goods.order_by('name')
    else:  # default
        goods = goods.order_by('code')

    # 페이지네이션
    paginator = Paginator(goods, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 브랜드 목록 (필터용)
    brands = Goods.objects.values_list('bun1', flat=True).distinct().exclude(
        bun1__isnull=True).exclude(bun1='').order_by('bun1')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'brand_filter': brand_filter,
        'tire_only': tire_only,
        'in_stock': in_stock,
        'sort_order': sort_order,
        'per_page': per_page,
        'brands': brands,
        'total_count': goods.count(),
    }
    return render(request, 'mobile/search.html', context)

@login_required
def product_detail(request, product_code):
    """상품 상세 페이지"""
    product = get_object_or_404(Goods, code=product_code)

    # 고객 정보 조회
    try:
        customer = Customers.objects.get(user_id=request.user.id)
    except Customers.DoesNotExist:
        messages.error(request, '고객 정보를 찾을 수 없습니다.')
        return redirect('mobile_index')

    # DOT 재고 정보 조회
    dot_years = []
    try:
        allocation = YearAllocation.objects.get(goods_code=product_code)
        current_year = 2018
        while hasattr(allocation, f'year_{current_year}'):
            stock = getattr(allocation, f'year_{current_year}', 0)
            if stock > 0:  # 재고가 있는 것만 표시
                dot_years.append({
                    'year': current_year,
                    'stock': stock
                })
            current_year += 1
            if current_year > 2030:  # 최대 2030년까지
                break
    except YearAllocation.DoesNotExist:
        pass

    # 할인율 계산 (api_views의 calculate_discount_rate 로직 간소화)
    from mobile.api_views import calculate_discount_rate
    discount_rate = calculate_discount_rate(customer.code, product_code, None)

    # 최종 가격 계산
    final_price = int(product.fixp * (1 - discount_rate / 100))

    context = {
        'product': product,
        'customer': customer,
        'dot_years': dot_years,
        'discount_rate': discount_rate,
        'final_price': final_price,
    }
    return render(request, 'mobile/product_detail.html', context)

@login_required
def cart_view(request):
    """장바구니 페이지"""
    return render(request, 'mobile/cart.html')

@login_required
def checkout_view(request):
    """주문/결제 페이지"""
    # 고객 정보 조회
    try:
        customer = Customers.objects.get(user_id=request.user.id)
    except Customers.DoesNotExist:
        messages.error(request, '고객 정보를 찾을 수 없습니다.')
        return redirect('mobile_index')

    context = {
        'customer': customer,
        'toss_client_key': settings.TOSS_CLIENT_KEY,
    }
    return render(request, 'mobile/checkout.html', context)

@login_required
def order_complete_view(request, order_id):
    """주문 완료 페이지"""
    order = get_object_or_404(Order, id=order_id)

    # 본인 주문인지 확인
    try:
        customer = Customers.objects.get(user_id=request.user.id)
        if order.customer_code != customer.code:
            messages.error(request, '잘못된 접근입니다.')
            return redirect('mobile_index')
    except Customers.DoesNotExist:
        messages.error(request, '고객 정보를 찾을 수 없습니다.')
        return redirect('mobile_index')

    # 결제 정보 조회
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None

    # 배송지 정보 조회
    try:
        shipping = ShippingAddress.objects.get(order=order)
    except ShippingAddress.DoesNotExist:
        shipping = None

    context = {
        'order': order,
        'payment': payment,
        'shipping': shipping,
    }
    return render(request, 'mobile/order_complete.html', context)

@login_required
def orders_view(request):
    """주문 내역 페이지"""
    return render(request, 'mobile/orders.html')

@login_required
def order_detail_view(request, order_id):
    """주문 상세 페이지"""
    order = get_object_or_404(Order, id=order_id)

    # 본인 주문인지 확인
    try:
        customer = Customers.objects.get(user_id=request.user.id)
        if order.customer_code != customer.code:
            messages.error(request, '잘못된 접근입니다.')
            return redirect('mobile_orders')
    except Customers.DoesNotExist:
        messages.error(request, '고객 정보를 찾을 수 없습니다.')
        return redirect('mobile_index')

    # 결제 정보 조회
    try:
        payment = Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        payment = None

    # 배송지 정보 조회
    try:
        shipping = ShippingAddress.objects.get(order=order)
    except ShippingAddress.DoesNotExist:
        shipping = None

    context = {
        'order': order,
        'payment': payment,
        'shipping': shipping,
    }
    return render(request, 'mobile/order_detail.html', context)

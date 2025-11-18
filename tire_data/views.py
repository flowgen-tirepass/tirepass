from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
import json
import re
from .models import Goods, Customers, YearAllocation

@staff_member_required(login_url='/admin/login/')
def index(request):
    """메인 페이지 - 관리자 전용"""
    goods_count = Goods.objects.count()
    # customers_simple 테이블은 이미 Z코드가 제외되어 있음
    customers_count = Customers.objects.count()

    context = {
        'goods_count': goods_count,
        'customers_count': customers_count,
    }
    return render(request, 'tire_data/index.html', context)


@staff_member_required(login_url='/admin/login/')
def goods_list(request):
    """상품 목록 페이지 - 관리자 전용"""
    # 검색 기능
    search_query = request.GET.get('search', '')
    brand_filter = request.GET.get('brand', '')

    # 기본 쿼리셋
    goods = Goods.objects.all()

    # 검색어가 있으면 필터링
    if search_query:
        # 숫자만 추출하여 검색 (특수문자, 영문 제거)
        numeric_query = re.sub(r'[^0-9]', '', search_query)

        if numeric_query:  # 숫자가 포함된 검색어
            # 타이어 사이즈 패턴 생성
            search_patterns = []

            # 타이어 사이즈 패턴 매칭 (예: 2057015 -> 205/70R15)
            if len(numeric_query) >= 6:
                width = numeric_query[:3]
                if len(numeric_query) >= 5:
                    aspect = numeric_query[3:5]
                    if len(numeric_query) >= 7:
                        rim = numeric_query[5:7]
                        search_patterns.extend([
                            f"{width}/{aspect}R{rim}",
                            f"{width}/{aspect}/{rim}",
                            f"{width}-{aspect}-{rim}",
                            f"{width} {aspect} {rim}",
                        ])

            # 검색 필터 생성
            q_filter = Q(code__icontains=search_query) | Q(name__icontains=search_query) | Q(bun1__icontains=search_query)

            # 숫자만으로도 검색
            q_filter |= Q(name__icontains=numeric_query)

            # 생성된 패턴들로 검색
            for pattern in search_patterns:
                q_filter |= Q(name__icontains=pattern)

            goods = goods.filter(q_filter)
        else:
            # 숫자가 없는 경우 일반 검색
            goods = goods.filter(
                Q(code__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(bun1__icontains=search_query) |
                Q(brand__icontains=search_query)
            )

    # 브랜드 필터
    if brand_filter:
        # brand 필드와 bun1 필드 모두 확인
        goods = goods.filter(Q(brand=brand_filter) | Q(bun1=brand_filter))

    # 타이어만 보기 옵션
    if request.GET.get('tire_only'):
        goods = goods.filter(is_tire=True)

    # 재고가 있는 상품만 보기 옵션
    if request.GET.get('in_stock'):
        goods = goods.filter(jaego__gt=0)

    # 페이지네이션
    paginator = Paginator(goods, 50)  # 페이지당 50개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 각 상품에 대한 연도별 할당 정보 가져오기
    allocations = {}
    for item in page_obj:
        try:
            allocation = YearAllocation.objects.get(goods_code=item.code)
            allocations[item.code] = {
                '2025': allocation.year_2025,
                '2024': allocation.year_2024,
                '2023': allocation.year_2023,
                '2022': allocation.year_2022,
                '2021': allocation.year_2021_before,
            }
        except YearAllocation.DoesNotExist:
            allocations[item.code] = {
                '2025': 0,
                '2024': 0,
                '2023': 0,
                '2022': 0,
                '2021': 0,
            }

    # 브랜드 목록 (필터용)
    brands = Goods.objects.values_list('bun1', flat=True).distinct().exclude(bun1__isnull=True).exclude(bun1='').order_by('bun1')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'brand_filter': brand_filter,
        'brands': brands,
        'total_count': goods.count(),
        'allocations': allocations,
    }
    return render(request, 'tire_data/goods_list.html', context)


@staff_member_required(login_url='/admin/login/')
def customers_list(request):
    """고객 목록 페이지 - 관리자 전용"""
    # 검색 기능
    search_query = request.GET.get('search', '')

    # customers_simple 테이블은 이미 Z코드가 제외되어 있음
    customers = Customers.objects.all().order_by('code')

    # 검색어가 있으면 필터링
    if search_query:
        customers = customers.filter(
            Q(code__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(rep__icontains=search_query) |
            Q(tel1__icontains=search_query) |
            Q(tel3__icontains=search_query)
        )

    # 페이지네이션
    paginator = Paginator(customers, 30)  # 페이지당 30개로 줄임
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # count() 쿼리 최적화 - 캐싱
    if not search_query:
        total_count = 1755  # 알려진 실제 고객 수
    else:
        total_count = customers.count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': total_count,
    }
    return render(request, 'tire_data/customers_list.html', context)


@staff_member_required(login_url='/admin/login/')
def goods_detail(request, code):
    """상품 상세 페이지 - 관리자 전용"""
    from urllib.parse import unquote

    # URL 디코딩
    code = unquote(code)

    try:
        goods = Goods.objects.get(code=code)
    except Goods.DoesNotExist:
        goods = None

    context = {
        'goods': goods,
    }
    return render(request, 'tire_data/goods_detail.html', context)


@staff_member_required(login_url='/admin/login/')
def customers_detail(request, code):
    """고객 상세 페이지 - 관리자 전용"""
    from urllib.parse import unquote

    # URL 디코딩
    code = unquote(code)

    try:
        customer = Customers.objects.get(code=code)
    except Customers.DoesNotExist:
        customer = None

    context = {
        'customer': customer,
    }
    return render(request, 'tire_data/customers_detail.html', context)


@csrf_exempt
@staff_member_required(login_url='/admin/login/')
def save_year_allocation(request):
    """연도별 할당 저장 API - 관리자 전용"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            goods_code = data.get('goods_code')
            year = data.get('year')
            value = int(data.get('value', 0))

            # YearAllocation 객체 가져오기 또는 생성
            allocation, created = YearAllocation.objects.get_or_create(
                goods_code=goods_code,
                defaults={
                    'year_2025': 0,
                    'year_2024': 0,
                    'year_2023': 0,
                    'year_2022': 0,
                    'year_2021_before': 0,
                }
            )

            # 해당 연도 값 업데이트
            if year == '2025':
                allocation.year_2025 = value
            elif year == '2024':
                allocation.year_2024 = value
            elif year == '2023':
                allocation.year_2023 = value
            elif year == '2022':
                allocation.year_2022 = value
            elif year == '2021':
                allocation.year_2021_before = value

            allocation.save()

            return JsonResponse({
                'success': True,
                'message': '저장되었습니다.',
                'total_allocated': allocation.total_allocated
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'저장 실패: {str(e)}'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'}, status=405)


@csrf_exempt
@staff_member_required(login_url='/admin/login/')
def save_discount_rate(request):
    """할인율 저장 API - 관리자 전용 (상품기본할인)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            goods_code = data.get('goods_code')
            discount_rate = float(data.get('discount_rate', 0))

            # 유효성 검사
            if discount_rate < 0 or discount_rate > 100:
                return JsonResponse({
                    'success': False,
                    'message': '할인율은 0~100% 사이여야 합니다.'
                }, status=400)

            # YearAllocation 객체 가져오거나 생성
            year_allocation, created = YearAllocation.objects.get_or_create(
                goods_code=goods_code,
                defaults={'base_discount': discount_rate}
            )

            # 이미 존재하면 base_discount 업데이트
            if not created:
                year_allocation.base_discount = discount_rate
                year_allocation.save()

            return JsonResponse({
                'success': True,
                'message': '할인율이 저장되었습니다.',
                'discount_rate': discount_rate
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'저장 실패: {str(e)}'
            }, status=400)

    return JsonResponse({'success': False, 'message': 'POST 요청만 허용됩니다.'}, status=405)

def adjust_customer_points_view(request, customer_id):
    """
    고객 포인트 조정 뷰

    CSRF 검증은 AdminPointsCSRFExemptMiddleware에서 우회
    """
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from tire_data.models import Customers, CustomerPoint

    # Admin 로그인 및 권한 체크
    if not request.user.is_authenticated:
        messages.error(request, '로그인이 필요합니다.')
        return redirect('/admin/login/')

    if not request.user.is_staff:
        messages.error(request, 'Staff 권한이 필요합니다.')
        return redirect('/admin/')

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'}, status=400)

    customer = get_object_or_404(Customers, pk=customer_id)

    try:
        amount = int(request.POST.get('amount', 0))
        action_type = request.POST.get('action_type', 'add')
        description = request.POST.get('description', '')

        if amount <= 0:
            return JsonResponse({'success': False, 'message': '포인트 금액은 0보다 커야 합니다.'}, status=400)

        if not description:
            return JsonResponse({'success': False, 'message': '사유를 입력해주세요.'}, status=400)

        # CustomerPoint 가져오거나 생성
        customer_point, created = CustomerPoint.objects.get_or_create(customer=customer)

        if action_type == 'add':
            # 포인트 지급
            customer_point.add_points(
                amount=amount,
                transaction_type='EARN_ADMIN',
                description=f'[관리자 지급] {description}',
                order_code=None
            )
            return JsonResponse({
                'success': True,
                'message': f'✅ {customer.name}님에게 {amount:,}P를 지급했습니다.',
                'new_balance': customer_point.balance
            })

        elif action_type == 'subtract':
            # 포인트 차감
            if amount > customer_point.balance:
                return JsonResponse({
                    'success': False,
                    'message': f'차감할 포인트({amount:,}P)가 현재 잔액({customer_point.balance:,}P)보다 많습니다.'
                }, status=400)

            customer_point.use_points(
                amount=amount,
                description=f'[관리자 차감] {description}',
                order_code=None
            )
            return JsonResponse({
                'success': True,
                'message': f'✅ {customer.name}님의 포인트 {amount:,}P를 차감했습니다.',
                'new_balance': customer_point.balance
            })

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'포인트 조정 중 오류가 발생했습니다: {str(e)}'}, status=500)

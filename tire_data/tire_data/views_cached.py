from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Goods, Customers

# 캐시된 고객 데이터
CACHED_CUSTOMERS = None

def get_cached_customers():
    """고객 데이터를 메모리에 캐시"""
    global CACHED_CUSTOMERS
    if CACHED_CUSTOMERS is None:
        try:
            # 실제 고객만 가져오기 (Z로 시작하지 않는 것)
            CACHED_CUSTOMERS = list(
                Customers.objects.exclude(code__startswith='Z')
                .values('code', 'name', 'rep', 'tel1', 'tel3', 'enno')
            )
        except:
            CACHED_CUSTOMERS = []
    return CACHED_CUSTOMERS


def customers_list_fast(request):
    """고객 목록 페이지 (캐시 버전)"""
    # 검색 기능
    search_query = request.GET.get('search', '')

    # 캐시된 데이터 가져오기
    customers_data = get_cached_customers()

    # 검색어가 있으면 필터링
    if search_query:
        search_lower = search_query.lower()
        customers_data = [
            c for c in customers_data
            if (search_lower in (c.get('code', '') or '').lower() or
                search_lower in (c.get('name', '') or '').lower() or
                search_lower in (c.get('rep', '') or '').lower() or
                search_lower in (c.get('tel1', '') or '').lower() or
                search_lower in (c.get('tel3', '') or '').lower())
        ]

    # 페이지네이션
    paginator = Paginator(customers_data, 50)  # 페이지당 50개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_count': len(customers_data),
    }
    return render(request, 'tire_data/customers_list.html', context)
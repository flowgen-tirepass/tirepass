"""
관리자 페이지 커스텀 뷰
ERP 실시간 데이터 조회
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.core.paginator import Paginator
from .erp_api_client import ERPAPIClient
import logging

logger = logging.getLogger(__name__)


@staff_member_required
def erp_goods_list(request):
    """ERP 실시간 상품 목록"""
    page = int(request.GET.get('page', 1))
    per_page = 100
    search = request.GET.get('search', '')

    # FastAPI를 통해 ERP 데이터 조회
    offset = (page - 1) * per_page

    if search:
        goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=per_page, search=search)
        total_count = len(goods_list)  # 검색 시 정확한 total은 별도 API 필요
    else:
        goods_list = ERPAPIClient.get_goods_list(offset=offset, limit=per_page)
        total_count = ERPAPIClient.get_goods_count()

    # 페이지네이션 정보
    total_pages = (total_count + per_page - 1) // per_page
    has_previous = page > 1
    has_next = page < total_pages

    context = {
        'title': 'ERP 실시간 상품 목록',
        'goods_list': goods_list,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_previous': has_previous,
        'has_next': has_next,
        'search': search,
    }

    return render(request, 'admin/erp_goods_list.html', context)


@staff_member_required
def erp_customers_list(request):
    """ERP 실시간 고객 목록"""
    page = int(request.GET.get('page', 1))
    per_page = 100
    search = request.GET.get('search', '')

    # FastAPI를 통해 ERP 데이터 조회
    offset = (page - 1) * per_page

    if search:
        customers_list = ERPAPIClient.get_customers_list(offset=offset, limit=per_page, search=search)
        total_count = len(customers_list)
    else:
        customers_list = ERPAPIClient.get_customers_list(offset=offset, limit=per_page)
        total_count = ERPAPIClient.get_customers_count()

    # 페이지네이션 정보
    total_pages = (total_count + per_page - 1) // per_page
    has_previous = page > 1
    has_next = page < total_pages

    context = {
        'title': 'ERP 실시간 고객 목록',
        'customers_list': customers_list,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_previous': has_previous,
        'has_next': has_next,
        'search': search,
    }

    return render(request, 'admin/erp_customers_list.html', context)


@staff_member_required
def erp_orders_list(request):
    """ERP 실시간 주문 목록"""
    page = int(request.GET.get('page', 1))
    per_page = 50
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # FastAPI를 통해 ERP 데이터 조회
    offset = (page - 1) * per_page

    orders_list = ERPAPIClient.get_orders_list(
        offset=offset,
        limit=per_page,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    total_count = ERPAPIClient.get_orders_count(
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    # 페이지네이션 정보
    total_pages = (total_count + per_page - 1) // per_page
    has_previous = page > 1
    has_next = page < total_pages

    context = {
        'title': 'ERP 실시간 주문 내역',
        'orders_list': orders_list,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_previous': has_previous,
        'has_next': has_next,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'admin/erp_orders_list.html', context)

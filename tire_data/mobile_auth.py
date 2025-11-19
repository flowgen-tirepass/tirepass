"""
모바일 API 인증 데코레이터 및 유틸리티
"""
from functools import wraps
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def mobile_login_required(view_func):
    """
    모바일 API 로그인 필수 데코레이터

    세션에 customer_code가 있는지 확인
    없으면 401 Unauthorized 반환

    사용법:
        @mobile_login_required
        @require_http_methods(["POST"])
        def api_cart_add(request):
            customer_code = request.session.get('customer_code')
            # ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        customer_code = request.session.get('customer_code')

        if not customer_code:
            logger.warning(f"Unauthorized API access attempt: {request.path}")
            return JsonResponse({
                'success': False,
                'error': '로그인이 필요합니다.',
                'redirect': '/mobile/login/'
            }, status=401)

        # customer_code를 request에 추가하여 뷰에서 쉽게 접근 가능
        request.customer_code = customer_code

        return view_func(request, *args, **kwargs)

    return wrapper


def get_customer_code_from_session(request):
    """
    세션에서 customer_code를 안전하게 가져오기

    Returns:
        str | None: customer_code 또는 None
    """
    return request.session.get('customer_code')


def is_mobile_user_logged_in(request):
    """
    모바일 사용자 로그인 상태 확인

    Returns:
        bool: 로그인 상태
    """
    return 'customer_code' in request.session

"""
모바일 고객의 관리자 페이지 접근 제한 미들웨어
"""
from django.shortcuts import redirect
from django.urls import reverse
from tire_data.models import Customers


class RestrictAdminAccessMiddleware:
    """
    모바일 사용자(카센터)의 관리자 페이지 접근을 차단하는 미들웨어
    - admin 계정이 아닌 일반 고객은 /admin/ 접근 금지
    - 모바일 로그인 페이지로 리다이렉트
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # /admin/ 경로 접근 시도
        if request.path.startswith('/admin/'):
            # 로그인되어 있는 경우만 체크
            if request.user.is_authenticated:
                # 슈퍼유저나 스태프 권한이 없으면 차단
                if not request.user.is_superuser and not request.user.is_staff:
                    # 모바일 홈으로 리다이렉트
                    return redirect('mobile_home')
            # 로그인되지 않은 경우는 Django 기본 동작(admin 로그인 페이지)으로 진행

        response = self.get_response(request)
        return response


class MobileUserCheckMiddleware:
    """
    모바일 사용자 여부를 체크하여 request에 추가하는 미들웨어
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 모바일 사용자 여부 체크
        request.is_mobile_user = False

        if request.user.is_authenticated:
            # 슈퍼유저나 스태프가 아닌 경우 모바일 사용자로 간주
            if not request.user.is_superuser and not request.user.is_staff:
                request.is_mobile_user = True

                # 고객 정보 가져오기
                try:
                    customer = Customers.objects.filter(
                        enno__contains=request.user.username
                    ).first()
                    request.customer = customer
                except:
                    request.customer = None

        response = self.get_response(request)
        return response

"""
TirePass 커스텀 미들웨어
"""
from django.conf import settings
from django.http import HttpResponseForbidden
from django.contrib import messages


class AdminPointsCSRFExemptMiddleware:
    """
    Admin 포인트 조정 URL에 대해 CSRF 검증 제외

    보안:
    - Admin 로그인 필수 (뷰에서 체크)
    - Staff 권한 필수 (뷰에서 체크)
    - 특정 URL만 제외
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Admin 포인트 조정 URL인 경우 CSRF 검증 제외
        if '/admin/adjust-points/' in request.path:
            setattr(request, '_dont_enforce_csrf_checks', True)

        response = self.get_response(request)
        return response


class ReadOnlyMiddleware:
    """
    읽기 전용 모드에서 데이터 변경 요청 차단

    settings.READ_ONLY_MODE = True일 때 활성화
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.read_only = getattr(settings, 'READ_ONLY_MODE', False)

    def __call__(self, request):
        # 읽기 전용 모드가 아니면 바로 통과
        if not self.read_only:
            return self.get_response(request)

        # 읽기 전용 모드에서 POST, PUT, DELETE, PATCH 요청 차단
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # 로그인 요청은 허용
            if request.path.startswith('/admin/login/') or request.path.startswith('/mobile/login/'):
                return self.get_response(request)

            # API 상태 확인 요청은 허용 (읽기만)
            if request.path.startswith('/api/admin/erp/status/'):
                return self.get_response(request)

            # 읽기 전용 API는 허용
            if request.method == 'POST' and any([
                '/auth/login/' in request.path,
                '/auth/logout/' in request.path,
            ]):
                return self.get_response(request)

            # 그 외 모든 변경 요청 차단
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1>'
                '<p>읽기 전용 모드입니다. 데이터를 변경할 수 없습니다.</p>'
                '<p>Read-only mode: Data modification is not allowed.</p>'
                '<hr>'
                '<p><a href="/admin/">관리자 페이지로 돌아가기</a></p>'
            )

        response = self.get_response(request)
        return response


class ReadOnlyAdminMiddleware:
    """
    Admin 페이지에서 읽기 전용 경고 표시
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.read_only = getattr(settings, 'READ_ONLY_MODE', False)

    def __call__(self, request):
        response = self.get_response(request)

        # 읽기 전용 모드이고 admin 페이지인 경우
        if self.read_only and request.path.startswith('/admin/'):
            # Admin 메시지 추가
            if hasattr(request, 'user') and request.user.is_authenticated:
                # 첫 방문 시에만 메시지 표시
                if not request.session.get('read_only_warned'):
                    messages.warning(
                        request,
                        '🔒 읽기 전용 모드: PythonAnywhere 데이터를 조회만 할 수 있습니다. '
                        '데이터 추가/수정/삭제가 차단됩니다.'
                    )
                    request.session['read_only_warned'] = True

        return response

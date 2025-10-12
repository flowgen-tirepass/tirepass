"""
커스텀 인증 백엔드
Django admin에서 사업자등록번호(고객 계정) 로그인 차단
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import CustomersSimple

User = get_user_model()


class AdminAuthBackend(ModelBackend):
    """
    Django admin 전용 인증 백엔드
    사업자등록번호(고객 계정)로 admin 로그인 시도 차단
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 1. 사업자등록번호 형식 체크 (10자리 숫자)
        if username and username.isdigit() and len(username) == 10:
            # CustomersSimple 테이블에 해당 code가 있는지 확인
            if CustomersSimple.objects.filter(code=username).exists():
                # 고객 계정이므로 admin 로그인 차단
                return None

        # 2. 일반 인증 진행
        return super().authenticate(request, username, password, **kwargs)

"""
커스텀 인증 백엔드
Django admin에서 사업자등록번호(고객 계정) 로그인 차단
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import Customers

User = get_user_model()


class AdminAuthBackend(ModelBackend):
    """
    Django admin 전용 인증 백엔드
    사업자등록번호(고객 계정)로 admin 로그인 시도 차단
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username:
            return super().authenticate(request, username, password, **kwargs)

        # 공백과 하이픈 제거
        import re
        cleaned_username = re.sub(r'[\s-]', '', username)

        # 1. 10자리 숫자 (사업자등록번호) 차단
        if re.match(r'^\d{10}$', cleaned_username):
            # Customers 테이블에 해당 code가 있는지 확인
            if Customers.objects.filter(code=cleaned_username).exists():
                # 고객 계정이므로 admin 로그인 차단
                return None
            # Customers 테이블에 없어도 10자리 숫자는 차단
            return None

        # 2. 13자리 숫자 (주민등록번호) 차단
        if re.match(r'^\d{13}$', cleaned_username):
            return None

        # 3. enno(사업자등록번호)로 로그인 시도 차단
        if Customers.objects.filter(enno=cleaned_username).exists():
            return None

        # 4. 일반 인증 진행
        return super().authenticate(request, username, password, **kwargs)

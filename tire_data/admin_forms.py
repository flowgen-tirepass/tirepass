"""
Admin 폼 커스터마이징
"""
from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError
import re


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    """
    사업자등록번호 입력을 차단하는 관리자 로그인 폼
    """

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            return username

        # 공백과 하이픈 제거
        cleaned_username = re.sub(r'[\s-]', '', username)

        # 10자리 숫자 (사업자등록번호) 차단
        if re.match(r'^\d{10}$', cleaned_username):
            raise ValidationError(
                '🚫 사업자등록번호로는 관리자 페이지에 접근할 수 없습니다. '
                '관리자 계정 아이디를 사용해주세요.',
                code='business_number_not_allowed'
            )

        # 13자리 숫자 (주민등록번호) 차단
        if re.match(r'^\d{13}$', cleaned_username):
            raise ValidationError(
                '🚫 주민등록번호로는 관리자 페이지에 접근할 수 없습니다. '
                '관리자 계정 아이디를 사용해주세요.',
                code='resident_number_not_allowed'
            )

        return username

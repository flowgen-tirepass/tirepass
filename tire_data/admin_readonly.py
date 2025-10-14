"""
읽기 전용 Admin 믹스인
"""
from django.conf import settings
from django.contrib import admin


class ReadOnlyAdminMixin:
    """
    읽기 전용 모드에서 Admin 권한 제한

    settings.READ_ONLY_MODE = True일 때 활성화
    - 추가 불가
    - 수정 불가
    - 삭제 불가
    """

    def has_add_permission(self, request):
        """추가 권한 체크"""
        if getattr(settings, 'READ_ONLY_MODE', False):
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        """수정 권한 체크"""
        if getattr(settings, 'READ_ONLY_MODE', False):
            # 조회는 허용
            if obj is None:
                return True
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """삭제 권한 체크"""
        if getattr(settings, 'READ_ONLY_MODE', False):
            return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        """액션 제거 (읽기 전용 모드)"""
        actions = super().get_actions(request)
        if getattr(settings, 'READ_ONLY_MODE', False):
            # 삭제 액션 제거
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

    def changelist_view(self, request, extra_context=None):
        """목록 화면에 읽기 전용 경고 추가"""
        extra_context = extra_context or {}
        if getattr(settings, 'READ_ONLY_MODE', False):
            extra_context['read_only_mode'] = True
            extra_context['read_only_message'] = (
                '🔒 읽기 전용 모드: PythonAnywhere의 데이터를 조회만 할 수 있습니다.'
            )
        return super().changelist_view(request, extra_context=extra_context)

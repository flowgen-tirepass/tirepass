from django import template
from tire_data.models import PolicyPage

register = template.Library()


@register.simple_tag
def get_footer_policies():
    """푸터에 표시할 정책 페이지 목록 반환"""
    return PolicyPage.objects.filter(
        is_active=True,
        show_in_footer=True
    ).order_by('display_order', 'title')

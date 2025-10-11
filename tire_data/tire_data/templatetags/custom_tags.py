from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Dictionary에서 key로 값을 가져오는 템플릿 필터"""
    if dictionary:
        return dictionary.get(key)
    return None
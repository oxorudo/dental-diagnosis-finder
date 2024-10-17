import re
from django import template

register = template.Library()

@register.filter
def get_subcategories(middle_data):
    """하위 분류만 반환하는 필터."""
    pattern = r'^[A-Z][0-9]{2}\.[0-9]{2}'
    subcategories = {}

    # middle_data가 dict인 경우 처리
    if isinstance(middle_data, dict) and 'children' in middle_data:
        children = middle_data['children']
        
        for code, data in children.items():
            if re.search(pattern, code):
                subcategories[code] = data

    return subcategories

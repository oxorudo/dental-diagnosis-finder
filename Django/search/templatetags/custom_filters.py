from django import template

register = template.Library()

@register.filter
def remove_last_char(value):
    return value[:-2] if isinstance(value, str) else value
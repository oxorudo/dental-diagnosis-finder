from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    """Returns the value split by the given delimiter."""
    return value.split(delimiter)

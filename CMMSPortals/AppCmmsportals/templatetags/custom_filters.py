from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def nl2br(value):
    if not value:
        return ''
    return mark_safe(value.replace('\n', '<br>'))
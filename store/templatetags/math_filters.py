# app/templatetags/math_filters.py
from django import template
register = template.Library()

@register.filter
def mul(value, arg):
    return value * arg

@register.filter
def div(value, arg):
    try:
        return value / arg
    except ZeroDivisionError:
        return 0

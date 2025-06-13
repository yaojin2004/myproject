from django import template

register = template.Library()

@register.filter
def class_name(obj):
    return obj.__class__.__name__

@register.filter
def truncate_title(value):
    """截取标题，保留前8个字符，超出部分用...代替"""
    if len(value) > 8:
        return value[:8] + '...'
    return value 
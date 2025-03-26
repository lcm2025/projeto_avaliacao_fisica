from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def previous(list, index):
    try:
        return list[index-1]
    except (IndexError, TypeError):
        return None
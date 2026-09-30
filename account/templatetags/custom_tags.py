from django import template

register = template.Library()


@register.filter
def range_to(value, max_value):
    return range(value-1, max_value)


@register.filter
def zip_lists(a, b):
    return zip(a, b)
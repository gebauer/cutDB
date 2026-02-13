from django import template
register = template.Library()

@register.filter
def in_list(value, the_list):
    value = str(value)
    return value in the_list.split(',')


@register.filter_function
def order_by(queryset, args):
    args = [x.strip() for x in args.split(',')]
    return queryset.order_by(*args)
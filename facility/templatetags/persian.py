from django import template

register = template.Library()



@register.filter
def to_persian_numbers(value):
    value = str(value)
    fa_numbers = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return value.translate(fa_numbers)


@register.filter
def to_persian_date(value):
    tmp = to_persian_numbers(value).split('-')
    return f'{tmp[0]}/{tmp[1]}/{tmp[2]}'


@register.filter
def bold(value):
    return f'<b>{value}</b>'

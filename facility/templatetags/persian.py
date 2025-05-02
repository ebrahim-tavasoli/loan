from django import template

register = template.Library()


@register.filter
def to_persian_numbers(value):
    value = str(value)
    fa_numbers = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return value.translate(fa_numbers)

@register.filter
def to_persian_thousand_sepraded_number(value):
    return to_persian_numbers(f"{value:,}")

from datetime import datetime, date


@register.filter
def to_persian_date(value):
    if value is None:
        return ""

    if isinstance(value, (datetime, date)):
        value = value.strftime("%Y-%m-%d")

    # تبدیل به اعداد فارسی و تقسیم‌بندی
    tmp = to_persian_numbers(value).split("-")

    if len(tmp) == 3:
        return f"{tmp[0]}/{tmp[1]}/{tmp[2]}"
    else:
        return value


@register.filter
def bold(value):
    return f"<b>{value}</b>"

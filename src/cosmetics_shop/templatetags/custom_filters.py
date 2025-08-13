from django import template


register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ""


@register.filter
def number_format(value):
    try:
        value = str(value)
        value = float(value[:-2]+"."+value[-2:])
        if value.is_integer():
            return f"{int(value):,}".replace(",", " ")
        else:
            return f"{value:,}".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return value

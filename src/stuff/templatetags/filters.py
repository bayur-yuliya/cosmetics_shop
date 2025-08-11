from django import template


register = template.Library()


@register.filter
def number_format(value):
    try:
        return f"{float(value):,.2f}".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return value

from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    try:
        result = value * arg
        return f"{result:.2f}"
    except (ValueError, TypeError):
        return ""


@register.filter
def number_format(value):
    try:
        value = float(value)
        return f"{value:.2f}".replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return value


@register.filter(name="add_class")
def add_class(field, css_class):
    """
    Добавляет CSS-класс к полю формы.
    """
    return field.as_widget(attrs={"class": css_class})

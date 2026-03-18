from unittest.mock import Mock

import pytest

from cosmetics_shop.templatetags.custom_filters import (
    add_class,
    multiply,
    number_format,
)


@pytest.mark.django_db
def test_multiply():
    result = multiply(10, 2)

    assert result == "20.00"


@pytest.mark.django_db
def test_multiply_invalid():
    result = multiply("a", 2)

    assert result == ""


@pytest.mark.django_db
def test_number_format():
    result = number_format(1234.5)

    assert result == "1234,50"


@pytest.mark.django_db
def test_add_class():
    field = Mock()
    field.as_widget.return_value = "<input class='test'>"

    add_class(field, "form-control")

    field.as_widget.assert_called_once()

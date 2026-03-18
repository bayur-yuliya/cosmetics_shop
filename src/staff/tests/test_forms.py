from decimal import Decimal
from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from cosmetics_shop.models import Product
from staff.forms import (
    AdminCreateUserForm,
    CategoryForm,
    OrderStatusUpdateForm,
    ProductFilterForm,
    ProductForm,
)


class FakeUser:
    def __init__(self, perms):
        self.perms = perms

    def has_perm(self, perm):
        return perm in self.perms


def test_product_form_price_permission():
    user = FakeUser(perms=["cosmetics_shop.can_change_product_price"])
    form = ProductForm(user=user)

    assert "price" in form.fields


def test_product_form_price_removed_without_permission():
    user = FakeUser(perms=[])
    form = ProductForm(user=user)

    assert "price" not in form.fields


def test_product_form_clean_price_valid():
    form = ProductForm(data={"price": "123,45"})
    form.cleaned_data = {"price": "123,45"}
    price = form.clean_price()

    assert price == Decimal("123.45")


def test_product_form_clean_price_invalid():
    form = ProductForm()
    form.cleaned_data = {"price": "abc"}

    with pytest.raises(ValidationError):
        form.clean_price()


def test_order_status_field_removed_without_permission():
    user = FakeUser(perms=[])
    form = OrderStatusUpdateForm(user=user)

    assert "status" not in form.fields


def test_order_status_update_calls_service():
    user = FakeUser(perms=["cosmetics_shop.change_orderstatuslog"])
    order = object()
    form = OrderStatusUpdateForm(
        data={"status": 1, "comment": "test"}, user=user, order=order
    )

    assert form.is_valid()

    with patch("staff.forms.change_order_status_log") as mock:
        form.save()

        mock.assert_called_once_with(order, user, 1, "test")


@pytest.mark.django_db
def test_product_filter_by_name(products):
    form = ProductFilterForm(data={"name": "cream"})
    queryset = Product.objects.all()
    result = form.apply_filters(queryset)

    for product in result:
        assert "cream" in product.name.lower()


@pytest.mark.django_db
def test_product_filter_min_price(products):
    form = ProductFilterForm(data={"min_price": 100})
    result = form.apply_filters(Product.objects.all())

    for product in result:
        assert product.price >= 100


def test_product_filter_invalid_form_returns_original_queryset():
    form = ProductFilterForm(data={"code": "invalid"})  # не int
    qs = Product.objects.all()
    result = form.apply_filters(qs)

    assert result == qs


@pytest.mark.django_db
def test_admin_create_user_form():
    form = AdminCreateUserForm(data={"email": "test@test.com"})

    assert form.is_valid()

    user = form.save()

    assert user.email == "test@test.com"
    assert user.is_active is False
    assert not user.has_usable_password()


@pytest.mark.django_db
def test_category_form_valid():
    form = CategoryForm(data={"name": "Test"})

    assert form.is_valid()

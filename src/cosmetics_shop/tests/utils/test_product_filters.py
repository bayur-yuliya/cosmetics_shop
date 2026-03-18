import pytest
from django.test import RequestFactory

from cosmetics_shop.models import Product
from cosmetics_shop.utils.product_filters import ProductFilter


@pytest.mark.django_db
def test_filter_min_price(group, brand):
    factory = RequestFactory()

    Product.objects.create(name="Cheap", price=10, group=group, brand=brand)
    Product.objects.create(name="Expensive", price=100, group=group, brand=brand)

    request = factory.get("/", {"min_price": 50})

    queryset = Product.objects.all()
    pf = ProductFilter(request, queryset)

    class FakeForm:
        cleaned_data = {
            "group": None,
            "tags": None,
            "min_price": 50,
            "max_price": None,
            "brand": None,
            "name": None,
        }

        def is_valid(self):
            return True

    pf.apply_filters(FakeForm())

    result = list(pf.queryset)

    assert len(result) == 1
    assert result[0].name == "Expensive"


@pytest.mark.django_db
def test_sort_by_price(group, brand):
    factory = RequestFactory()

    Product.objects.create(name="A", price=50, group=group, brand=brand)
    Product.objects.create(name="B", price=10, group=group, brand=brand)

    request = factory.get("/", {"sort": "price", "direction": "asc"})

    queryset = Product.objects.all()
    pf = ProductFilter(request, queryset)

    sorted_qs = pf.apply_sorting()

    prices = list(sorted_qs.values_list("price", flat=True))

    assert prices == [10, 50]


@pytest.mark.django_db
def test_build_sort_url():
    factory = RequestFactory()

    request = factory.get("/", {"page": 2})

    pf = ProductFilter(request, [])

    url = pf._build_sort_url("price")

    assert "sort=price" in url
    assert "direction=asc" in url


@pytest.mark.django_db
def test_clear_sort_url():
    factory = RequestFactory()

    request = factory.get("/", {"sort": "price", "direction": "asc", "page": 2})

    pf = ProductFilter(request, [])

    url = pf.get_clear_sort_url()

    assert "sort" not in url
    assert "direction" not in url
    assert "page=2" in url


@pytest.mark.django_db
def test_invalid_sort_field():
    factory = RequestFactory()

    request = factory.get("/", {"sort": "DROP_TABLE"})

    pf = ProductFilter(request, [])

    sort_by, direction = pf.get_sort_params()

    assert sort_by is None

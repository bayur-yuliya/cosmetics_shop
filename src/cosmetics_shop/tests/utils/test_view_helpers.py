import json

import pytest
from django.http import JsonResponse
from django.test import RequestFactory

from cosmetics_shop.utils.view_helpers import (
    build_context,
    clean_query_params,
    handle_ajax,
    processing_product_page,
)


@pytest.mark.django_db
def test_removes_empty_values():
    factory = RequestFactory()
    request = factory.get("/products/?brand=&category=None&price=100")

    query_params, clean_url = clean_query_params(request)

    assert query_params.dict() == {"price": "100"}
    assert clean_url == "/products/?price=100"


@pytest.mark.django_db
def test_no_params():
    factory = RequestFactory()
    request = factory.get("/products/")

    query_params, clean_url = clean_query_params(request)

    assert query_params == {}
    assert clean_url == "/products/"


@pytest.mark.django_db
def test_build_context(mocker):
    factory = RequestFactory()
    request = factory.get("/products/")
    request.user = mocker.Mock(is_authenticated=False)
    request.session = mocker.Mock(session_key="test_session")

    mock_form_class = mocker.patch(
        "cosmetics_shop.utils.view_helpers.ProductFilterForm"
    )
    mock_form = mock_form_class.return_value
    mock_form.is_valid.return_value = True

    mock_filter_class = mocker.patch("cosmetics_shop.utils.view_helpers.ProductFilter")
    mock_filter = mock_filter_class.return_value
    mock_filter.apply_sorting.return_value = ["product_obj"]
    mock_filter.current_sort = "price"
    mock_filter.current_direction = "asc"

    mocker.patch(
        "cosmetics_shop.utils.view_helpers.context_categories", return_value=["cat1"]
    )
    mocker.patch("cosmetics_shop.utils.view_helpers.get_cart", return_value="cart_obj")
    mocker.patch(
        "cosmetics_shop.utils.view_helpers.get_id_products_in_cart",
        return_value=[1, 2],
    )
    mocker.patch(
        "cosmetics_shop.utils.view_helpers.get_paginator_page",
        return_value=["page_obj"],
    )

    context = build_context(request, products=[], title="Catalog")

    assert context["title"] == "Catalog"
    assert context["current_sort"] == "price"
    assert context["current_direction"] == "asc"
    assert context["cart_products"] == [1, 2]
    assert context["products"] == ["page_obj"]
    assert context["context_categories"] == ["cat1"]

    mock_filter_class.assert_called_once_with(request, [])
    mock_filter.apply_sorting.assert_called_once()


@pytest.mark.django_db
def test_ajax_response(mocker):
    factory = RequestFactory()
    request = factory.get("/products/")

    mock_render = mocker.patch("cosmetics_shop.utils.view_helpers.render_to_string")
    mock_render.return_value = "<html></html>"

    response = handle_ajax(request, {"a": 1}, "/products/")

    data = json.loads(response.content)

    assert response.status_code == 200

    assert data["html"] == "<html></html>"
    assert data["sorting_html"] == "<html></html>"
    assert data["url"] == "/products/"


@pytest.mark.django_db
def test_redirect(mocker):  # noqa
    factory = RequestFactory()
    request = factory.get("/products/?brand=")

    mocker.patch("cosmetics_shop.utils.view_helpers.build_context")

    response = processing_product_page(
        request,
        products=[],
        template_name="test.html",
        title="Test",
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_ajax(mocker):
    factory = RequestFactory()
    request = factory.get("/products/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    mock_context = mocker.patch("cosmetics_shop.utils.view_helpers.build_context")
    mock_ajax = mocker.patch("cosmetics_shop.utils.view_helpers.handle_ajax")

    mock_context.return_value = {"ctx": 1}
    mock_ajax.return_value = JsonResponse({"ok": True})

    response = processing_product_page(
        request,
        products=[],
        template_name="test.html",
        title="Test",
    )

    assert response.status_code == 200
    mock_ajax.assert_called_once()


@pytest.mark.django_db
def test_render(mocker):
    factory = RequestFactory()
    request = factory.get("/products/")

    mock_context = mocker.patch("cosmetics_shop.utils.view_helpers.build_context")
    mock_render = mocker.patch("cosmetics_shop.utils.view_helpers.render")

    mock_context.return_value = {"ctx": 1}
    mock_render.return_value = "response"

    processing_product_page(
        request,
        products=[],
        template_name="test.html",
        title="Test",
    )

    mock_render.assert_called_once()

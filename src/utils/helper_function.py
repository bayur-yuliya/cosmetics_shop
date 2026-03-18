from typing import Sequence

from django.core.paginator import Page, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest

from config.settings.base import PRODUCTS_PER_PAGE


def get_paginator_page(
    request: HttpRequest,
    object_list: QuerySet | Sequence,
    per_page: int = PRODUCTS_PER_PAGE,
) -> Page:
    paginator = Paginator(object_list, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)

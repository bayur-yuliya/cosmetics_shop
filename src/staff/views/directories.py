from django.urls import reverse_lazy

from cosmetics_shop.models import Tag, Brand, GroupProduct, Category
from staff.forms import TagForm, BrandForm, GroupProductForm, CategoryForm
from staff.services.list_service import (
    BaseStaffDeleteView,
    BaseStaffChangeView,
    BaseStaffCreateView,
    BaseStaffListView,
)


# Category
class CategoryListView(BaseStaffListView):
    model = Category
    page_title = "Список категорий"
    permission_required = "cosmetics_shop.view_category"


class CategoryCreateView(BaseStaffCreateView):
    page_title = "Создание категории"
    model = Category
    form_class = CategoryForm
    permission_required = "cosmetics_shop.add_category"
    success_url = reverse_lazy("categories_list")


class CategoryChangeView(BaseStaffChangeView):
    page_title = "Изменение категории"
    model = Category
    form_class = CategoryForm
    permission_required = "cosmetics_shop.change_category"
    success_url = reverse_lazy("categories_list")


class CategoryDeleteView(BaseStaffDeleteView):
    model = Category
    permission_required = "cosmetics_shop.delete_category"
    success_url = reverse_lazy("categories_list")


# GroupProduct
class GroupProductListView(BaseStaffListView):
    model = GroupProduct
    page_title = "Список групп"
    permission_required = "cosmetics_shop.view_groupproduct"


class GroupProductCreateView(BaseStaffCreateView):
    page_title = "Создание группы"
    model = GroupProduct
    form_class = GroupProductForm
    permission_required = "cosmetics_shop.add_groupproduct"
    success_url = reverse_lazy("groups_list")


class GroupProductChangeView(BaseStaffChangeView):
    page_title = "Изменение группы"
    model = GroupProduct
    form_class = GroupProductForm
    permission_required = "cosmetics_shop.add_groupproduct"
    success_url = reverse_lazy("groups_list")


class GroupProductDeleteView(BaseStaffDeleteView):
    model = GroupProduct
    permission_required = "cosmetics_shop.delete_groupproduct"
    success_url = reverse_lazy("groups_list")


# Brand
class BrandListView(BaseStaffListView):
    model = Brand
    page_title = "Список брендов"
    permission_required = "cosmetics_shop.view_brand"


class BrandCreateView(BaseStaffCreateView):
    page_title = "Создание бренда"
    model = Brand
    form_class = BrandForm
    permission_required = "cosmetics_shop.add_brand"
    success_url = reverse_lazy("brands_list")


class BrandChangeView(BaseStaffChangeView):
    page_title = "Изменение бренда"
    model = Brand
    form_class = BrandForm
    permission_required = "cosmetics_shop.change_brand"
    success_url = reverse_lazy("brands_list")


class BrandDeleteView(BaseStaffDeleteView):
    model = Brand
    permission_required = "cosmetics_shop.delete_brand"
    success_url = reverse_lazy("brands_list")


# Tag
class TagListView(BaseStaffListView):
    model = Tag
    page_title = "Список тегов"
    permission_required = "cosmetics_shop.view_tag"


class TagCreateView(BaseStaffCreateView):
    page_title = "Создание тега"
    model = Tag
    form_class = TagForm
    permission_required = "cosmetics_shop.add_tag"
    success_url = reverse_lazy("tags_list")


class TagChangeView(BaseStaffChangeView):
    page_title = "Изменение тега"
    model = Tag
    form_class = TagForm
    permission_required = "cosmetics_shop.change_tag"
    success_url = reverse_lazy("tags_list")


class TagDeleteView(BaseStaffDeleteView):
    model = Tag
    permission_required = "cosmetics_shop.delete_tag"
    success_url = reverse_lazy("tags_list")

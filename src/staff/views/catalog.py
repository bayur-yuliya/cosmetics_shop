from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from cosmetics_shop.models import Brand, Category, GroupProduct, Tag
from staff.forms import BrandForm, CategoryForm, GroupProductForm, TagForm
from staff.services.list_service import (
    BaseStaffDeleteView,
    BaseStaffListView,
    BaseStaffManageView,
)


# Category
class CategoryListView(BaseStaffListView):
    model = Category
    page_title = "Список категорий"
    permission_required = "cosmetics_shop.view_category"


class CategoryCreateView(BaseStaffManageView, CreateView):
    page_title = "Создание категории"
    model = Category
    form_class = CategoryForm
    permission_required = "cosmetics_shop.add_category"
    success_url = reverse_lazy("categories_list")


class CategoryChangeView(BaseStaffManageView, UpdateView):
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


class GroupProductCreateView(BaseStaffManageView, CreateView):
    page_title = "Создание группы"
    model = GroupProduct
    form_class = GroupProductForm
    permission_required = "cosmetics_shop.add_groupproduct"
    success_url = reverse_lazy("groups_list")


class GroupProductChangeView(BaseStaffManageView, UpdateView):
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


class BrandCreateView(BaseStaffManageView, CreateView):
    page_title = "Создание бренда"
    model = Brand
    form_class = BrandForm
    permission_required = "cosmetics_shop.add_brand"
    success_url = reverse_lazy("brands_list")


class BrandChangeView(BaseStaffManageView, UpdateView):
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


class TagCreateView(BaseStaffManageView, CreateView):
    page_title = "Создание тега"
    model = Tag
    form_class = TagForm
    permission_required = "cosmetics_shop.add_tag"
    success_url = reverse_lazy("tags_list")


class TagChangeView(BaseStaffManageView, UpdateView):
    page_title = "Изменение тега"
    model = Tag
    form_class = TagForm
    permission_required = "cosmetics_shop.change_tag"
    success_url = reverse_lazy("tags_list")


class TagDeleteView(BaseStaffDeleteView):
    model = Tag
    permission_required = "cosmetics_shop.delete_tag"
    success_url = reverse_lazy("tags_list")

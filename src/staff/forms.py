from decimal import Decimal

from django import forms
from django.contrib.auth.models import Group

from cosmetics_shop.models import (
    Product,
    Category,
    GroupProduct,
    Brand,
    OrderStatusLog,
    Tag,
)
from staff.services.permission_service import get_individually_assigned_permits_names


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]


class GroupProductForm(forms.ModelForm):
    class Meta:
        model = GroupProduct
        fields = ["name", "category"]


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name"]


class ProductForm(forms.ModelForm):
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), initial=0)
    tags = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, queryset=Tag.objects.all(), required=False
    )
    price = forms.CharField(max_length=20)

    class Meta:
        model = Product
        fields = [
            "name",
            "image",
            "group",
            "brand",
            "tags",
            "price",
            "description",
            "stock",
        ]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            self.user = user
            if not user.has_perm("cosmetics_shop.can_change_product_price"):
                self.fields.pop("price")
            if not user.has_perm("cosmetics_shop.can_manage_product_stock"):
                self.fields.pop("stock")

    def clean_price(self):
        price = self.cleaned_data["price"]
        if isinstance(price, str):
            price = price.replace(" ", "").replace(",", ".")

        price = Decimal(price)
        return int(price * 100)


class OrderStatusForm(forms.ModelForm):
    date_from = forms.DateField(
        required=False, label="Дата с", widget=forms.DateInput(attrs={"type": "date"})
    )
    date_to = forms.DateField(
        required=False, label="Дата по", widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = OrderStatusLog
        fields = ["status", "comment", "date_from", "date_to"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            if not user.has_perm("cosmetics_shop.can_change_order_status"):
                self.fields.pop("status")


class ProductStuffFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Название содержит: ")
    code = forms.IntegerField(required=False, label="Код товара: ")
    min_price = forms.DecimalField(required=False, label="Минимальная цена: ")
    max_price = forms.DecimalField(required=False, label="Максимальная цена: ")


class FilterStockForm(forms.Form):
    min_stock = forms.IntegerField(required=False, label="Мин. остаток")
    max_stock = forms.IntegerField(required=False, label="Макс. остаток")


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]


class GroupForm(forms.ModelForm):
    name = forms.CharField(max_length=200)
    permissions = forms.ModelMultipleChoiceField(
        queryset=get_individually_assigned_permits_names(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]

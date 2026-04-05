from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from accounts.models import ActivationToken
from cosmetics_shop.models import (
    Brand,
    Category,
    GroupProduct,
    OrderStatusLog,
    Product,
    Status,
    Tag,
)
from staff.services.order_service import change_order_status_log
from staff.services.permission_service import get_individually_assigned_permits


class PermissionMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return str(obj.name)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        labels = {"name": "Введите название категории: "}


class GroupProductForm(forms.ModelForm):
    class Meta:
        model = GroupProduct
        fields = ["name", "category"]
        labels = {
            "name": "Введите название группы: ",
            "category": "Выберите категорию: ",
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name"]
        labels = {"name": "Введите название бренда: "}


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]
        labels = {"name": "Введите название тега: "}


class ProductForm(forms.ModelForm):
    brand = forms.ModelChoiceField(label="Бренд", queryset=Brand.objects.all())
    tags = forms.ModelMultipleChoiceField(
        label="Теги",
        widget=forms.CheckboxSelectMultiple,
        queryset=Tag.objects.all(),
        required=False,
    )
    price = forms.CharField(label="Цена", max_length=20)

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
        labels = {
            "name": "Название",
            "image": "Изображение ",
            "group": "Группа",
            "description": "Описание",
            "stock": "Количество товара на складе",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            if "price" in self.fields:
                self.initial["price"] = str(self.instance.price)

        if user:
            if not user.has_perm("cosmetics_shop.can_change_product_price"):
                self.fields.pop("price", None)
            if not user.has_perm("cosmetics_shop.can_manage_product_stock"):
                self.fields.pop("stock", None)

    def clean_price(self):
        price_value = self.cleaned_data.get("price")

        if price_value is None:
            return Decimal("0.00")

        price_str = str(price_value).replace(",", ".")

        try:
            price = Decimal(price_str)
        except (InvalidOperation, ValueError):
            raise ValidationError("Введите корректное число.")

        return price


class OrderFilterForm(forms.Form):
    status = forms.ChoiceField(
        label="Статус заказа", choices=Status.choices, required=False
    )
    date_from = forms.DateField(
        label="Дата с", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    date_to = forms.DateField(
        label="Дата по", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )


class OrderStatusUpdateForm(forms.ModelForm):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control"}), required=False
    )

    class Meta:
        model = OrderStatusLog
        fields = ["status", "comment"]

    def __init__(self, *args, user=None, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.order = order

        if self.user and not self.user.has_perm("cosmetics_shop.change_orderstatuslog"):
            self.fields.pop("status")

    def save(self, commit=True):
        status = self.cleaned_data["status"]
        comment = self.cleaned_data["comment"]

        return change_order_status_log(self.order, self.user, status, comment)


class ProductFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Название содержит")
    code = forms.IntegerField(required=False, label="Код товара")
    brand = forms.CharField(required=False, label="Бренд")
    min_price = forms.DecimalField(required=False, label="Мин. цена")
    max_price = forms.DecimalField(required=False, label="Макс. цена")

    min_stock = forms.IntegerField(required=False, label="Мин. остаток")
    max_stock = forms.IntegerField(required=False, label="Макс. остаток")

    def apply_filters(self, queryset):
        if not self.is_valid():
            return queryset

        data = self.cleaned_data

        if data.get("name"):
            queryset = queryset.filter(name__icontains=data["name"])
        if data.get("brand"):
            queryset = queryset.filter(brand__name__icontains=data["brand"])
        if data.get("min_price"):
            queryset = queryset.filter(price__gte=data["min_price"], stock__gte=1)
        if data.get("max_price"):
            queryset = queryset.filter(price__lte=data["max_price"])
        if data.get("code"):
            queryset = queryset.filter(code=data["code"])
        if data.get("min_stock"):
            queryset = queryset.filter(stock__gte=data["min_stock"])
        if data.get("max_stock"):
            queryset = queryset.filter(stock__lte=data["max_stock"])

        return queryset


class GroupForm(forms.ModelForm):
    name = forms.CharField(label="Группы", max_length=200)
    permissions = PermissionMultipleChoiceField(
        label="Разрешения",
        queryset=get_individually_assigned_permits(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Group
        fields = ["name", "permissions"]


class AdminCreateTokenForm(forms.ModelForm):
    class Meta:
        model = ActivationToken
        fields = ("email",)

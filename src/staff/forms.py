from decimal import Decimal, InvalidOperation

from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from cosmetics_shop.models import (
    Product,
    Category,
    GroupProduct,
    Brand,
    OrderStatusLog,
    Tag,
)
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
    brand = forms.ModelChoiceField(
        label="Бренд", queryset=Brand.objects.all(), initial=0
    )
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
        try:
            price = Decimal(price)
            ready_price = int(price * 100)
            return ready_price
        except (InvalidOperation, ValueError):
            raise ValidationError("Некорректная цена")


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
        labels = {
            "status": "Текущий статус заказа",
            "comment": "Добавить комментарий",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user:
            if not user.has_perm("cosmetics_shop.change_orderstatuslog"):
                self.fields.pop("status")


class ProductStuffFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Название содержит")
    code = forms.IntegerField(required=False, label="Код товара")
    brand = forms.CharField(required=False, label="Бренд")
    min_price = forms.DecimalField(required=False, label="Минимальная цена")
    max_price = forms.DecimalField(required=False, label="Максимальная цена")


class FilterStockForm(forms.Form):
    min_stock = forms.IntegerField(required=False, label="Мин. остаток")
    max_stock = forms.IntegerField(required=False, label="Макс. остаток")


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


class AdminCreateUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        user.is_active = False
        if commit:
            user.save()
        return user

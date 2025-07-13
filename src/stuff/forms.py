from django import forms

from cosmetics_shop.models import (
    Product,
    Category,
    GroupProduct,
    Brand,
    OrderStatusLog,
)


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

    class Meta:
        model = Product
        fields = ["name", "image", "group", "brand", "price", "description", "stock"]


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderStatusLog
        fields = ["status", "comment"]

from django import forms

from cosmetics_shop.models import Product, Category, GroupProduct, Brand, Order


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class GroupProductForm(forms.ModelForm):
    class Meta:
        model = GroupProduct
        fields = ['name', 'category']


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'group', 'brand', 'price', 'description']


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

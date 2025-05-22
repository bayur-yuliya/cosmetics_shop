from django.db import models


class Category(models.Model):
    name_category = models.CharField(max_length=50)

    def __str__(self):
        return self.name_category


class GroupProduct(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category.name_category} - {self.name}'


class Brand(models.Model):
    name_brand = models.CharField(max_length=100)

    def __str__(self):
        return self.name_brand


class Product(models.Model):
    name_product = models.CharField(max_length=100)
    product_code = models.PositiveIntegerField(default=0)
    group_product = models.ForeignKey(GroupProduct, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    description = models.TextField()
    slug = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.group_product.name} - {self.name_product}'

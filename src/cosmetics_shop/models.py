from django.db import models


class Category(models.Model):
    name_category = models.CharField(max_length=50)


class GroupProduct(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Product(models.Model):
    name_product = models.CharField(max_length=100)
    group_product = models.ForeignKey(GroupProduct, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    description = models.TextField()

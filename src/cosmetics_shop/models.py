from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Status(models.IntegerChoices):
    NEW = 0, 'New'
    PAYMENT_RECEIVED = 1, 'Payment received'
    PAYMENT_FAILED = 2, 'Payment failed'
    IN_PROGRESS = 3, 'In progress'
    COMPLETED = 4, 'Completed'
    CLOSED = 5, 'Closed'
    CANCELED = 6, 'Canceled'


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class GroupProduct(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.category.name} - {self.name}'


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(GroupProduct, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    description = models.TextField()
    slug = models.SlugField(max_length=120)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.group.name} - {self.name}'


class Card(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f'{self.created_at} - {self.user}'


class CardItem(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.product} - {self.quantity}'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)

    def __str__(self):
        return f'{self.created_at} - {self.get_status_display()} - {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.order} - {self.product}'

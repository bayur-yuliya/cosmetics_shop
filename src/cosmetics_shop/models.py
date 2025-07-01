from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Status(models.IntegerChoices):
    NEW = 0, "New"
    PAYMENT_RECEIVED = 1, "Payment received"
    PAYMENT_FAILED = 2, "Payment failed"
    IN_PROGRESS = 3, "In progress"
    COMPLETED = 4, "Completed"
    CLOSED = 5, "Closed"
    CANCELED = 6, "Canceled"


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    was_registered = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class DeliveryAddress(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    post_office = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.city}, {self.street}"


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class GroupProduct(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


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
    stock = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.group.name} - {self.name}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.created_at} - {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} - {self.quantity}"


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    delivery_address = models.ForeignKey(
        DeliveryAddress, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)

    snapshot_name = models.CharField(max_length=100)
    snapshot_email = models.EmailField()
    snapshot_phone = models.CharField(max_length=20)
    snapshot_address = models.TextField()

    def __str__(self):
        return f"{self.created_at} - {self.get_status_display()} - {self.snapshot_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.CharField(max_length=100)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order} - {self.product}"


class OrderStatusLog(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='status_log')
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-changed_at']

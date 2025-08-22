import random

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Status(models.IntegerChoices):
    NEW = 0, "New"
    PAYMENT_RECEIVED = 1, "Payment received"
    PAYMENT_FAILED = 2, "Payment failed"
    IN_PROGRESS = 3, "In progress"
    COMPLETED = 4, "Completed"
    CLOSED = 5, "Closed"
    CANCELED = 6, "Canceled"


class ProductQuerySet(models.QuerySet):
    def with_stock_order(self):
        return self.annotate(
            stock_zero=models.Case(
                models.When(stock=0, then=models.Value(1)),
                default=models.Value(0),
                output_field=models.IntegerField(),
            )
        ).order_by("stock_zero")


class ProductManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                stock_zero=models.Case(
                    models.When(stock=0, then=models.Value(1)),
                    default=models.Value(0),
                    output_field=models.IntegerField(),
                )
            )
            .order_by("stock_zero")
        )


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
        return f"{self.name}"


class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(GroupProduct, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    code = models.PositiveIntegerField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="product_images/", default="default/image.jpg")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")

    objects = ProductManager.from_queryset(ProductQuerySet)()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_unique_code()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        while True:
            code = random.randint(10000, 99999)
            if not Product.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return f"{self.group.name} - {self.name}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "product")


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
    code = models.CharField(max_length=100, unique=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0)

    snapshot_name = models.CharField(max_length=100)
    snapshot_email = models.EmailField()
    snapshot_phone = models.CharField(max_length=20)
    snapshot_address = models.TextField()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        """
        Code generation: ORD-20250715-XXXX (date + serial number)
        """
        date_str = now().strftime("%Y%m%d")
        prefix = f"ORD-{date_str}-"
        for i in range(1, 10000):
            code_candidate = f"{prefix}{str(i).zfill(4)}"
            if not Order.objects.filter(code=code_candidate).exists():
                return code_candidate
        raise ValueError("Failed to generate unique order code")

    def __str__(self):
        return f"{self.created_at} - {self.code}"

    class Meta:
        ordering = ["-id"]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order} - {self.product}"


class OrderStatusLog(models.Model):
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="status_log"
    )
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_status_display()}"

    class Meta:
        ordering = ["-changed_at"]

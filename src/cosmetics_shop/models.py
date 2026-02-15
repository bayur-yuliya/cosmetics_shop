import random
import uuid
from itertools import count

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from slugify import slugify

from accounts.models import CustomUser
from accounts.utils.validators import validate_phone_number


class Status(models.IntegerChoices):
    NEW = 0, "New"
    PAYMENT_RECEIVED = 1, "Payment received"
    PAYMENT_FAILED = 2, "Payment failed"
    IN_PROGRESS = 3, "In progress"
    COMPLETED = 4, "Completed"
    CLOSED = 5, "Closed"
    CANCELED = 6, "Canceled"

    @classmethod
    def badge_class(cls, status):
        return {
            cls.NEW: "info",
            cls.PAYMENT_RECEIVED: "primary",
            cls.PAYMENT_FAILED: "warning",
            cls.IN_PROGRESS: "info",
            cls.COMPLETED: "success",
            cls.CLOSED: "warning",
            cls.CANCELED: "danger",
        }.get(status)


class ProductQuerySet(models.QuerySet):
    def with_stock_order(self):
        return self.annotate(
            stock_zero=models.Case(
                models.When(stock=0, then=models.Value(1)),
                default=models.Value(0),
                output_field=models.IntegerField(),
            )
        ).order_by("stock_zero")


class SlugRedirectModel(models.Model):
    """
    An abstract model that handles:
    1. The slug field
    2. Generating a unique slug upon saving
    3. Creating a redirect when the slug changes
    """

    slug = models.SlugField(max_length=200, unique=True, blank=True)

    url_name_for_edit = None

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            name_val = getattr(self, "name", "")
            self.slug = slugify(name_val)

        orig_slug = self.slug
        for i in count(1):
            qs = self.__class__.objects.filter(slug=self.slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if not qs.exists():
                break
            self.slug = f"{orig_slug}-{i}"

        super().save(*args, **kwargs)

        if self.pk and self.url_name_for_edit:
            self._handle_redirects()

    def _handle_redirects(self):
        old_obj = self.__class__.objects.filter(pk=self.pk).first()

        if old_obj and old_obj.slug != self.slug:
            old_path = reverse(self.url_name_for_edit, kwargs={"slug": old_obj.slug})
            new_path = reverse(self.url_name_for_edit, kwargs={"slug": self.slug})

            if old_path != new_path:
                site = Site.objects.get_current()
                Redirect.objects.update_or_create(
                    site=site, old_path=old_path, defaults={"new_path": new_path}
                )

    def get_absolute_edit_url(self):
        if self.url_name_for_edit:
            return reverse(self.url_name_for_edit, kwargs={"slug": self.slug})
        return ""


class Client(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=10, validators=[validate_phone_number])
    is_active = models.BooleanField(default=True)
    was_registered = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name = _("клиента")
        verbose_name_plural = _("Клиенты")


class DeliveryAddress(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    post_office = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.street}"

    class Meta:
        verbose_name = _("адрес доставки")
        verbose_name_plural = _("Адреса доставки")


class Category(SlugRedirectModel):
    name = models.CharField(max_length=50, unique=True)

    url_name_for_edit = "edit_categories"

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("категорию")
        verbose_name_plural = _("Категории")


class GroupProduct(SlugRedirectModel):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    url_name_for_edit = "edit_groups"

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]
        verbose_name = _("группу товаров")
        verbose_name_plural = _("Группы товаров")


class Brand(SlugRedirectModel):
    name = models.CharField(max_length=100, unique=True)

    url_name_for_edit = "edit_brands"

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("бренд")
        verbose_name_plural = _("Бренды")


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("тег")
        verbose_name_plural = _("Теги")


class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(GroupProduct, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    code = models.PositiveIntegerField(unique=True, blank=True, null=True)
    image = models.ImageField(upload_to="product_images/", default="default/image.jpg")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    is_active = models.BooleanField(default=True)

    objects = ProductQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_unique_code():
        while True:
            code = random.randint(0000000, 9999999)
            if not Product.objects.filter(code=code).exists():
                return code

    def __str__(self):
        return f"{self.group} - {self.name}"

    class Meta:
        verbose_name = _("товар")
        verbose_name_plural = _("Товары")
        permissions = [
            ("can_change_product_price", "Может изменять цену товара"),
            ("can_manage_product_stock", "Может управлять остатками товара"),
        ]


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "product")


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    created_at = models.DateField(auto_now_add=True)

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
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    snapshot_name = models.CharField(max_length=200)
    snapshot_phone = models.CharField(max_length=20)
    snapshot_email = models.EmailField()
    snapshot_address = models.TextField()

    def __str__(self):
        return f"{self.created_at} - {self.code}"

    class Meta:
        ordering = ["-id"]
        verbose_name = _("заказ")
        verbose_name_plural = _("Заказы")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Цена на момент покупки"
    )
    quantity = models.PositiveIntegerField()
    snapshot_product = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.order} - {self.product}"

    def save(self, *args, **kwargs):
        if not self.pk and self.product:
            self.snapshot_product = self.product.name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("товар в заказе")
        verbose_name_plural = _("товары в заказе")


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

    def status_badge_class(self):
        return Status.badge_class(self.status)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name = _("статус заказа")
        verbose_name_plural = _("Статусы заказов")

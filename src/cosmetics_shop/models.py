import uuid
from itertools import count

from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.db.models import Sum, F, Q
from django.urls import reverse, NoReverseMatch
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

    def for_catalog(self):
        return (
            self.select_related("group", "brand")
            .prefetch_related("tags")
            .with_stock_order()
        )


class SlugRedirectModel(models.Model):
    """
    An abstract model that handles:
    1. The slug field
    2. Generating a unique slug upon saving
    3. Creating a redirect when the slug changes
    """

    slug = models.SlugField(max_length=200, unique=True, blank=True)

    redirect_url_configs: list[tuple[str, str]] = []

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        old_slug = None

        if self.pk:
            old_slug = (
                self.__class__._default_manager.filter(pk=self.pk)
                .values_list("slug", flat=True)
                .first()
            )

        if not self.slug:
            name_val = getattr(self, "name", "")
            self.slug = slugify(name_val)

        base_slug = self.slug

        for i in count(0):
            try:
                with transaction.atomic():
                    if i > 0:
                        self.slug = f"{base_slug}-{i}"

                    super().save(*args, **kwargs)
                    break
            except IntegrityError:
                if i > 100:
                    raise
                continue

        if old_slug and old_slug != self.slug and self.redirect_url_configs:
            self._handle_redirects(old_slug)

    def _handle_redirects(self, old_slug):
        from django.contrib.redirects.models import Redirect
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        for url_name, slug_param in self.redirect_url_configs:
            try:
                old_path = reverse(url_name, kwargs={slug_param: old_slug})
                new_path = reverse(url_name, kwargs={slug_param: self.slug})

                if old_path != new_path:
                    Redirect.objects.update_or_create(
                        site=site, old_path=old_path, defaults={"new_path": new_path}
                    )
            except NoReverseMatch:
                print(
                    f"Redirect failed: URL name '{url_name}' not found. "
                    f"Check your urls.py for model {self.__class__.__name__}."
                )
            except IntegrityError as e:
                print(f"Database error while creating redirect for {self.slug}: {e}")

    def get_absolute_url(self):
        if self.redirect_url_configs:
            url_name, slug_param = self.redirect_url_configs[0]
            return reverse(url_name, kwargs={slug_param: self.slug})
        return ""


class Client(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=10, validators=[validate_phone_number])
    email = models.EmailField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_registered(self):
        return self.user is not None

    def save(self, *args, **kwargs):
        if self.user and not self.email:
            with transaction.atomic():
                user_email = getattr(self.user, 'email', "")
                self.email = user_email or ""
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("клиента")
        verbose_name_plural = _("Клиенты")
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                condition=Q(user__isnull=False),
                name='unique_registered_email'
            )
        ]


class DeliveryAddress(models.Model):
    client = models.ForeignKey(
        Client, related_name="addresses", on_delete=models.CASCADE
    )
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    post_office = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.city}, {self.post_office}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            with transaction.atomic():
                DeliveryAddress.objects.filter(
                    client=self.client, is_primary=True
                ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("адрес доставки")
        verbose_name_plural = _("Адреса доставки")


class Category(SlugRedirectModel):
    name = models.CharField(max_length=50, unique=True)

    redirect_url_configs = [
        ("category_page", "category_slug"),
        ("edit_categories", "slug"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = _("категорию")
        verbose_name_plural = _("Категории")


class GroupProduct(SlugRedirectModel):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    redirect_url_configs = [
        ("group_page", "group_slug"),
        ("edit_groups", "slug"),
    ]

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ["name"]
        verbose_name = _("группу товаров")
        verbose_name_plural = _("Группы товаров")


class Brand(SlugRedirectModel):
    name = models.CharField(max_length=100, unique=True)

    redirect_url_configs = [
        ("brand_detail", "brand_slug"),
        ("edit_brands", "slug"),
    ]

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
    code = models.PositiveIntegerField(unique=True, editable=False, db_index=True)
    image = models.ImageField(upload_to="product_images/", default="default/image.jpg")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    is_active = models.BooleanField(default=True, db_index=True)

    objects = ProductQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                self.code = 0
                super().save(*args, **kwargs)

                A = 4_827_137
                B = 1_234_567
                MOD = 10_000_000

                self.code = (A * self.pk + B) % MOD
                Product.objects.filter(pk=self.pk).update(code=self.code)
        else:
            super().save(*args, **kwargs)

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
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at} - {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product} - {self.quantity}"

    class Meta:
        unique_together = ("cart", "product")


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=Status.choices, default=Status.NEW, db_index=True
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    snapshot_name = models.CharField(max_length=200)
    snapshot_phone = models.CharField(max_length=20)
    snapshot_email = models.EmailField()
    snapshot_address = models.TextField()

    def __str__(self):
        return f"{self.created_at} - {self.code}"

    def save(self, *args, **kwargs):
        if not self.pk and self.client:
            self.snapshot_name = (
                f"{self.client.first_name} {self.client.last_name}".strip()
            )
            self.snapshot_phone = self.client.phone if self.client.phone else ""
            self.snapshot_email = self.client.email if self.client.email else ""

            address = self.client.addresses.filter(is_primary=True)
            if address:
                self.snapshot_address = str(address)

        super().save(*args, **kwargs)

    def update_total_price(self):
        total = (
            self.order_items.aggregate(
                total=Sum(
                    F("price") * F("quantity"), output_field=models.DecimalField()
                )
            )["total"]
            or 0
        )

        self.total_price = total
        self.save(update_fields=["total_price"])

    class Meta:
        ordering = ["-id"]
        verbose_name = _("заказ")
        verbose_name_plural = _("Заказы")


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Цена на момент покупки"
    )
    quantity = models.PositiveIntegerField()
    snapshot_product = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.order} - {self.product}"

    def save(self, *args, **kwargs):
        if not self.pk and self.product and not self.price:
            self.price = self.product.price

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

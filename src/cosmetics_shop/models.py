import uuid
from decimal import Decimal
from random import randint

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import IntegrityError, models, transaction
from django.db.models import F, Sum
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
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
    CANCELED = 5, "Canceled"

    @classmethod
    def badge_class(cls, status):
        return {
            cls.NEW: "info",
            cls.PAYMENT_RECEIVED: "primary",
            cls.PAYMENT_FAILED: "warning",
            cls.IN_PROGRESS: "info",
            cls.COMPLETED: "success",
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
        ).order_by("stock_zero", "-stock")

    def for_catalog(self):
        return (
            self.select_related("group", "brand")
            .prefetch_related("tags")
            .with_stock_order()
        )


class SlugRedirectModel(models.Model):
    """
    An abstract model that handles:
    1. The automatically generated slug field
    2. Uniqueness check
    3. Creating a redirect when the slug changes
    """

    slug = models.SlugField(max_length=200, unique=True, blank=True)

    redirect_url_configs: list[tuple[str, str]] = []
    slug_source_field = "name"

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        source_val = getattr(self, self.slug_source_field, "")

        if not source_val and not self.slug:
            return

        if source_val:
            new_slug = slugify(source_val)
            exists = (
                self.__class__.objects.filter(slug=new_slug)
                .exclude(pk=self.pk)
                .exists()
            )
            if exists:
                raise ValidationError(
                    {self.slug_source_field: _("Такое название уже используется.")}
                )

    def save(self, *args, **kwargs):
        old_slug = None

        if self.pk:
            old_instance = (
                self.__class__.objects.filter(pk=self.pk).only("slug").first()
            )
            if old_instance:
                old_slug = old_instance.slug

        if not self.slug:
            self.slug = slugify(getattr(self, self.slug_source_field, "object"))

        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError("Слаг не уникален.")

        if old_slug and old_slug != self.slug and self.redirect_url_configs:
            self._handle_redirects(old_slug)

    def _handle_redirects(self, old_slug):
        # print replace to logging
        from django.contrib.redirects.models import Redirect
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        for url_name, slug_param in self.redirect_url_configs:
            try:
                old_path = reverse(url_name, kwargs={slug_param: old_slug})
                new_path = reverse(url_name, kwargs={slug_param: self.slug})

                if old_path != new_path:
                    Redirect.objects.filter(site=site, new_path=old_path).update(
                        new_path=new_path
                    )
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


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(
        _("дата создания"),
        auto_now_add=True,
        db_index=True,
        editable=False,
    )

    class Meta:
        abstract = True
        get_latest_by = "created_at"
        ordering = ["-created_at"]


class Client(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=13, validators=[validate_phone_number])
    email = models.EmailField(verbose_name="Контактный email клиента")
    is_active = models.BooleanField(default=True)
    is_pending_deletion = models.BooleanField(default=False)
    deletion_scheduled_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.user and self.is_active and not self.email:
            self.email = self.user.email
        elif self.user and self.is_active:
            self.user.email = self.email
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("клиента")
        verbose_name_plural = _("Клиенты")


class DeliveryAddress(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="addresses"
    )
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    post_office = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.city}, {self.post_office}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_other_client_addresses_as_non_primary()

    def update_other_client_addresses_as_non_primary(self):
        if self.is_primary:
            with transaction.atomic():
                DeliveryAddress.objects.filter(
                    client=self.client, is_primary=True
                ).exclude(pk=self.pk).update(is_primary=False)

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


class Product(TimestampedModel):
    name = models.CharField(max_length=250, unique=True)
    group = models.ForeignKey(
        GroupProduct, on_delete=models.CASCADE, related_name="products"
    )
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    code = models.PositiveIntegerField(unique=True, editable=False, db_index=True)
    image = models.ImageField(upload_to="product_images/", default="default/image.jpg")
    tags = models.ManyToManyField(Tag, blank=True, related_name="products")
    is_active = models.BooleanField(default=True, db_index=True)

    objects = ProductQuerySet.as_manager()

    def save(self, *args, **kwargs):
        # 10,000,000 records should be enough
        if not self.pk:
            with transaction.atomic():
                self.code = randint(0, 9999)
                super().save(*args, **kwargs)

                A = 4_827_137
                B = 1_234_567
                MOD = 10_000_000

                self.code = (A * self.pk + B) % MOD
                Product.objects.filter(pk=self.pk).update(code=self.code)
        else:
            super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_active = False
        self.save()

    def __str__(self):
        return f"{self.group} - {self.name}"

    class Meta:
        verbose_name = _("товар")
        verbose_name_plural = _("Товары")
        permissions = [
            ("can_change_product_price", "Может изменять цену товара"),
            ("can_manage_product_stock", "Может управлять остатками товара"),
        ]


class Favorite(TimestampedModel):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="favorites"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "product")


class Cart(TimestampedModel):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, null=True, related_name="cart"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)

    def __str__(self):
        return f"{self.created_at} - {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product} - {self.quantity}"

    class Meta:
        unique_together = ("cart", "product")


class Order(TimestampedModel):
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL, null=True, related_name="orders"
    )
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.IntegerField(
        choices=Status.choices, default=Status.NEW, db_index=True
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    completed_at = models.DateTimeField(null=True, blank=True, editable=False)
    comment = models.TextField(max_length=300, null=True, blank=True)

    snapshot_name = models.CharField(max_length=200)
    snapshot_phone = models.CharField(max_length=20)
    snapshot_email = models.EmailField()
    snapshot_address = models.TextField()

    def __str__(self):
        return f"{self.created_at} - {self.code}"

    def save(self, *args, **kwargs):
        is_new = not self.pk

        if is_new and self.client:
            self.snapshot_name = (
                f"{self.client.first_name} {self.client.last_name}".strip()
            )
            self.snapshot_phone = getattr(self.client, "phone", "")
            self.snapshot_email = getattr(self.client, "email", "")

            address = self.client.addresses.filter(is_primary=True).first()
            if address:
                self.snapshot_address = str(address)

        if self.status == Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)

        if is_new:
            self.set_status(self.status, commit=False)

    def update_total_price(self):
        # NOTE: Automatic recalculation of the order total is intentionally moved out
        # of the save method.
        # This avoids the N+1 problem during bulk operations.
        # Don't forget to call order.update_total_price()
        # at the end of View or Service function.
        total = (
            self.order_items.aggregate(
                total=Sum(
                    F("price") * F("quantity"), output_field=models.DecimalField()
                )
            )["total"]
            or 0
        )

        self.total_price = total

    def set_status(self, new_status, user=None, comment="", commit=True):
        with transaction.atomic():
            self.status = new_status
            if commit:
                self.save(update_fields=["status"])
            OrderStatusLog.objects.create(
                order=self, status=new_status, changed_by=user, comment=comment
            )

    def status_badge_class(self):
        return Status.badge_class(self.status)

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
    snapshot_product = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.product} - {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.snapshot_product and self.product:
            self.snapshot_product = self.product.name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("товар в заказе")
        verbose_name_plural = _("товары в заказе")


class OrderStatusLog(models.Model):
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="order_status_log"
    )
    status = models.IntegerField(choices=Status.choices, default=Status.NEW)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_logs",
    )
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_status_display()}"

    def status_badge_class(self):
        return Status.badge_class(self.status)

    class Meta:
        ordering = ["-changed_at", "-id"]
        verbose_name = _("статус заказа")
        verbose_name_plural = _("Статусы заказов")

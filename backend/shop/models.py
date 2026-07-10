from decimal import Decimal
import re

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.utils.text import slugify


def _unique_slug(instance, source_value, slug_field="slug"):
    base_slug = slugify(source_value) or "item"
    slug = base_slug
    counter = 2
    model = instance.__class__

    while model.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    stock = models.PositiveIntegerField(default=0)
    weight_grams = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if self.sku == "":
            self.sku = None
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_profile",
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name


class Address(models.Model):
    customer = models.ForeignKey(Customer, related_name="addresses", on_delete=models.CASCADE)
    label = models.CharField(max_length=50, blank=True)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name_plural = "addresses"
        constraints = [
            models.UniqueConstraint(
                fields=["customer"],
                condition=Q(is_default=True),
                name="unique_default_address_per_customer",
            )
        ]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.city}, {self.postal_code}"


class SavedPaymentMethod(models.Model):
    customer = models.ForeignKey(Customer, related_name="saved_payment_methods", on_delete=models.CASCADE)
    provider = models.CharField(max_length=50, default="stripe")
    token_reference = models.CharField(max_length=255, unique=True)
    nickname = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=50, blank=True)
    last4 = models.CharField(max_length=4, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["customer"],
                condition=Q(is_default=True),
                name="unique_default_payment_method_per_customer",
            )
        ]

    def __str__(self) -> str:
        label = self.nickname or self.brand or self.provider
        return f"{self.customer.full_name} - {label}"


class Cart(models.Model):
    customer = models.OneToOneField(
        Customer, related_name="cart", on_delete=models.CASCADE, null=True, blank=True
    )
    session_key = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(customer__isnull=False) | Q(session_key__isnull=False),
                name="cart_has_customer_or_session",
            )
        ]

    def __str__(self) -> str:
        return f"Cart #{self.pk}"

    @property
    def total_amount(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="cart_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.quantity * self.product.price


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer = models.ForeignKey(
        Customer, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True
    )
    shipping_address = models.ForeignKey(
        Address, related_name="orders", on_delete=models.SET_NULL, null=True, blank=True
    )
    shipping_address_snapshot = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} - {self.customer_name}"

    @property
    def total_amount(self):
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.line_total
        return total

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def contact_phone(self):
        if self.shipping_address and self.shipping_address.phone:
            return self.shipping_address.phone
        if self.customer and self.customer.phone:
            return self.customer.phone

        lines = self.shipping_address_lines
        if len(lines) >= 2:
            candidate = lines[1]
            if re.search(r"\d", candidate) and not any(part in candidate.lower() for part in ("street", "road", "lane")):
                return candidate
        return ""

    @property
    def shipping_address_lines(self):
        if self.shipping_address:
            address = self.shipping_address
            lines = [
                address.full_name,
                address.phone,
                address.line1,
                address.line2,
                f"{address.city}, {address.state} {address.postal_code}",
                address.country,
            ]
            return [line for line in lines if line]
        return [line for line in self.shipping_address_snapshot.splitlines() if line]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.product_name} x {self.quantity}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price

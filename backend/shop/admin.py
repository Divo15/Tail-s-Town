from django.contrib import admin
from django.utils.html import format_html_join

from .models import (
    Address,
    BundleEnquiry,
    Cart,
    CartItem,
    Category,
    Customer,
    Order,
    OrderItem,
    Product,
    SavedPaymentMethod,
)

admin.site.site_header = "Tail's Town Admin"
admin.site.site_title = "Tail's Town Admin"
admin.site.index_title = "Store management"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sku", "price", "stock", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    list_editable = ("price", "stock", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "sku", "brand", "description")
    radio_fields = {"category": admin.VERTICAL}
    fieldsets = (
        ("Product", {"fields": ("category", "name", "slug", "sku", "brand", "description", "image")}),
        ("Selling", {"fields": ("price", "stock", "weight_grams", "is_active")}),
    )


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class SavedPaymentMethodInline(admin.TabularInline):
    model = SavedPaymentMethod
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "updated_at")
    search_fields = ("full_name", "email", "phone")
    inlines = [AddressInline, SavedPaymentMethodInline]


@admin.register(BundleEnquiry)
class BundleEnquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "bundle_type", "phone", "email", "created_at")
    list_filter = ("bundle_type", "created_at")
    search_fields = ("full_name", "phone", "email")
    readonly_fields = ("bundle_type", "full_name", "phone", "email", "created_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("product", "product_name", "quantity", "unit_price", "line_total_display")
    readonly_fields = ("line_total_display",)
    extra = 0

    @admin.display(description="Line total")
    def line_total_display(self, obj):
        if not obj.pk:
            return "-"
        return f"Rs. {obj.line_total}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_email",
        "contact_phone_display",
        "status",
        "item_count_display",
        "order_total",
        "created_at",
    )
    list_display_links = ("id", "customer_name")
    list_editable = ("status",)
    list_filter = ("status", "created_at", "updated_at")
    search_fields = (
        "customer_name",
        "customer_email",
        "customer__full_name",
        "customer__email",
        "shipping_address__phone",
        "shipping_address_snapshot",
    )
    readonly_fields = (
        "contact_phone_display",
        "shipping_address_display",
        "item_count_display",
        "order_total",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        ("Customer", {"fields": ("customer", "customer_name", "customer_email", "contact_phone_display")}),
        ("Shipping", {"fields": ("shipping_address", "shipping_address_display", "shipping_address_snapshot")}),
        ("Fulfillment", {"fields": ("status",)}),
        ("Totals", {"fields": ("item_count_display", "order_total")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    inlines = [OrderItemInline]
    actions = ["mark_processing", "mark_shipped", "mark_completed", "mark_cancelled"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("customer", "shipping_address").prefetch_related("items")

    @admin.display(description="Phone")
    def contact_phone_display(self, obj):
        return obj.contact_phone or "-"

    @admin.display(description="Ship to")
    def shipping_address_display(self, obj):
        lines = obj.shipping_address_lines
        if not lines:
            return "-"
        return format_html_join("", "{}<br>", ((line,) for line in lines))

    @admin.display(description="Items")
    def item_count_display(self, obj):
        count = obj.item_count
        return f"{count} item" if count == 1 else f"{count} items"

    @admin.display(description="Total")
    def order_total(self, obj):
        return f"Rs. {obj.total_amount}"

    def _set_status(self, request, queryset, status):
        updated = queryset.update(status=status)
        self.message_user(request, f"{updated} order(s) updated.")

    @admin.action(description="Mark selected orders as processing")
    def mark_processing(self, request, queryset):
        self._set_status(request, queryset, Order.Status.PROCESSING)

    @admin.action(description="Mark selected orders as shipped")
    def mark_shipped(self, request, queryset):
        self._set_status(request, queryset, Order.Status.SHIPPED)

    @admin.action(description="Mark selected orders as completed")
    def mark_completed(self, request, queryset):
        self._set_status(request, queryset, Order.Status.COMPLETED)

    @admin.action(description="Mark selected orders as cancelled")
    def mark_cancelled(self, request, queryset):
        self._set_status(request, queryset, Order.Status.CANCELLED)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "quantity", "unit_price", "line_total_display")

    @admin.display(description="Line total")
    def line_total_display(self, obj):
        return f"Rs. {obj.line_total}"


@admin.register(SavedPaymentMethod)
class SavedPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("customer", "provider", "brand", "last4", "is_default", "updated_at")
    list_filter = ("provider", "brand", "is_default")
    search_fields = ("customer__full_name", "customer__email", "token_reference", "nickname")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("customer", "full_name", "city", "postal_code", "is_default")
    list_filter = ("country", "state", "is_default")
    search_fields = ("customer__full_name", "customer__email", "full_name", "city", "postal_code")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "session_key", "updated_at")
    search_fields = ("customer__full_name", "customer__email", "session_key")
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "added_at")
    search_fields = ("product__name", "cart__session_key", "cart__customer__email")

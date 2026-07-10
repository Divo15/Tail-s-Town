from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CartAddForm, CartUpdateForm
from ..models import CartItem, Product
from ..services.carts import get_cart


def cart_detail(request):
    cart = get_cart(request)
    items = list(cart.items.select_related("product", "product__category").order_by("added_at"))
    product_ids = [item.product_id for item in items]
    recommended_products = Product.objects.filter(is_active=True).select_related("category").exclude(pk__in=product_ids)[:3]
    return render(
        request,
        "store/cart_detail.html",
        {
            "cart": cart,
            "items": items,
            "cart_quantity_count": sum(item.quantity for item in items),
            "recommended_products": recommended_products,
        },
    )


def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    form = CartAddForm(request.POST or None)

    if request.method != "POST" or not form.is_valid():
        messages.error(request, "Choose a valid quantity.")
        return redirect("store:product_detail", slug=product.slug)

    quantity = form.cleaned_data["quantity"]
    if quantity > product.stock:
        messages.error(request, f"Only {product.stock} available.")
        return redirect("store:product_detail", slug=product.slug)

    cart = get_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )
    if not created:
        new_quantity = item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f"Only {product.stock} available.")
            return redirect("store:cart_detail")
        item.quantity = new_quantity
        item.save(update_fields=["quantity"])

    messages.success(request, "Added to cart.")
    return redirect("store:cart_detail")


def cart_update(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem.objects.select_related("product"), pk=item_id, cart=cart)
    form = CartUpdateForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        quantity = form.cleaned_data["quantity"]
        if quantity <= item.product.stock:
            item.quantity = quantity
            item.save(update_fields=["quantity"])
            messages.success(request, "Cart updated.")
        else:
            messages.error(request, f"Only {item.product.stock} available.")

    return redirect("store:cart_detail")


def cart_remove(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Item removed.")
    return redirect("store:cart_detail")

from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CheckoutForm
from ..models import Order, Product
from ..services.carts import get_cart
from ..services.checkout import checkout_initial_data, create_order_from_cart
from ..services.customers import get_customer

GUEST_ORDER_SESSION_KEY = "guest_order_success_ids"
MAX_GUEST_ORDER_IDS = 20


def _remember_guest_order(request, order):
    order_ids = [str(order_id) for order_id in request.session.get(GUEST_ORDER_SESSION_KEY, [])]
    order_id = str(order.pk)
    if order_id in order_ids:
        order_ids.remove(order_id)
    request.session[GUEST_ORDER_SESSION_KEY] = [*order_ids, order_id][-MAX_GUEST_ORDER_IDS:]
    request.session.modified = True


def _can_view_order_success(request, order):
    if request.user.is_authenticated:
        customer = get_customer(request.user)
        return order.customer_id == customer.pk

    allowed_order_ids = {str(order_id) for order_id in request.session.get(GUEST_ORDER_SESSION_KEY, [])}
    return order.customer_id is None and str(order.pk) in allowed_order_ids


def checkout(request):
    cart = get_cart(request)
    items = list(cart.items.select_related("product"))

    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("store:product_list")

    customer = get_customer(request.user) if request.user.is_authenticated else None
    form = CheckoutForm(request.POST or None, initial=checkout_initial_data(customer))

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            for item in items:
                product = Product.objects.select_for_update().get(pk=item.product_id)
                if item.quantity > product.stock:
                    messages.error(request, f"Only {product.stock} available for {product.name}.")
                    return redirect("store:cart_detail")

            order = create_order_from_cart(cart, items, customer, form.cleaned_data)

        if customer is None:
            _remember_guest_order(request, order)
        messages.success(request, f"Order #{order.pk} created.")
        return redirect("store:order_success", pk=order.pk)

    return render(
        request,
        "store/checkout.html",
        {
            "cart": cart,
            "items": items,
            "form": form,
            "cart_quantity_count": sum(item.quantity for item in items),
        },
    )


def order_success(request, pk):
    order = get_object_or_404(Order.objects.select_related("customer").prefetch_related("items"), pk=pk)
    if not _can_view_order_success(request, order):
        raise Http404("Order not found.")
    return render(request, "store/order_success.html", {"order": order})

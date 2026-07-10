from ..models import Cart, CartItem
from .customers import get_customer


def ensure_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_cart(request):
    if request.user.is_authenticated:
        customer = get_customer(request.user)
        cart, _ = Cart.objects.get_or_create(customer=customer, defaults={"session_key": None})

        session_key = request.session.session_key
        if session_key:
            session_cart = Cart.objects.filter(session_key=session_key, customer__isnull=True).first()
            if session_cart and session_cart.pk != cart.pk:
                for item in session_cart.items.select_related("product"):
                    existing, created = CartItem.objects.get_or_create(
                        cart=cart,
                        product=item.product,
                        defaults={"quantity": item.quantity},
                    )
                    if not created:
                        existing.quantity += item.quantity
                        existing.save(update_fields=["quantity"])
                session_cart.delete()

        return cart

    session_key = ensure_session_key(request)
    cart, _ = Cart.objects.get_or_create(session_key=session_key, customer=None)
    return cart

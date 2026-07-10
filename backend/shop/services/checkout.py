from ..models import Address, Order, OrderItem, Product


def address_snapshot(data):
    lines = [
        data["full_name"],
        data.get("phone", ""),
        data["line1"],
        data.get("line2", ""),
        f"{data['city']}, {data['state']} {data['postal_code']}",
        data["country"],
    ]
    return "\n".join(line for line in lines if line)


def checkout_initial_data(customer):
    if not customer:
        return {}

    address = customer.addresses.first()
    initial = {
        "full_name": customer.full_name,
        "email": customer.email,
        "phone": customer.phone,
    }
    if address:
        initial.update(
            {
                "full_name": address.full_name,
                "phone": address.phone,
                "line1": address.line1,
                "line2": address.line2,
                "city": address.city,
                "state": address.state,
                "postal_code": address.postal_code,
                "country": address.country,
            }
        )
    return initial


def create_order_from_cart(cart, items, customer, data):
    address = None
    if customer:
        address = Address.objects.create(
            customer=customer,
            label="Checkout",
            full_name=data["full_name"],
            phone=data.get("phone", ""),
            line1=data["line1"],
            line2=data.get("line2", ""),
            city=data["city"],
            state=data["state"],
            postal_code=data["postal_code"],
            country=data["country"],
            is_default=not customer.addresses.exists(),
        )

    order = Order.objects.create(
        customer=customer,
        customer_name=data["full_name"],
        customer_email=data["email"],
        shipping_address=address,
        shipping_address_snapshot=address_snapshot(data),
    )

    for item in items:
        product = Product.objects.select_for_update().get(pk=item.product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=item.quantity,
            unit_price=product.price,
        )
        product.stock -= item.quantity
        product.save(update_fields=["stock"])

    cart.items.all().delete()
    return order

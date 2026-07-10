from ..models import Customer


def get_customer(user):
    customer, _ = Customer.objects.get_or_create(
        user=user,
        defaults={
            "full_name": user.get_full_name() or user.username,
            "email": user.email or user.username,
        },
    )
    return customer

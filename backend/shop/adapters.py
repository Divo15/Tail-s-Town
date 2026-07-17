from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

from .models import Customer


User = get_user_model()


class CustomerSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = (data.get("email") or user.email or "").strip().lower()
        full_name = (data.get("name") or "").strip()

        if email:
            user.email = email
            user.username = email
        if full_name and not user.first_name and not user.last_name:
            name_parts = full_name.split(" ", 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        self._sync_customer(user, sociallogin)
        return user

    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        email = self._verified_email(sociallogin)
        if not email:
            return

        user = (
            User.objects.filter(email__iexact=email).first()
            or User.objects.filter(username__iexact=email).first()
        )
        if user is None or user.is_staff:
            return

        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])

        sociallogin.connect(request, user)
        self._sync_customer(user, sociallogin)

    def _verified_email(self, sociallogin):
        for email_address in sociallogin.email_addresses:
            if email_address.verified and email_address.email:
                return email_address.email.strip().lower()
        return ""

    def _sync_customer(self, user, sociallogin):
        email = (user.email or user.username or "").strip().lower()
        full_name = user.get_full_name().strip()
        if not full_name:
            full_name = (
                sociallogin.account.extra_data.get("name")
                or sociallogin.account.extra_data.get("full_name")
                or email
            )

        customer, _ = Customer.objects.update_or_create(
            email=email,
            defaults={
                "user": user,
                "full_name": full_name,
            },
        )
        if not customer.user_id:
            customer.user = user
            customer.save(update_fields=["user"])

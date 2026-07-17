from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .models import Customer

User = get_user_model()


class AccountFlowTests(TestCase):
    def test_register_verify_login_logout_dashboard_and_password_reset(self):
        register_response = self.client.post(
            reverse("customer_account:register"),
            {
                "email": "customer@example.com",
                "full_name": "Test Customer",
                "phone": "9999999999",
                "password1": "Str0ngPass!234",
                "password2": "Str0ngPass!234",
            },
            follow=True,
        )
        self.assertRedirects(register_response, reverse("customer_account:login"))

        user = User.objects.get(username="customer@example.com")
        customer = Customer.objects.get(user=user)
        self.assertFalse(user.is_active)
        self.assertEqual(customer.email, "customer@example.com")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/account/verify/", mail.outbox[0].body)

        blocked_login = self.client.post(
            reverse("customer_account:login"),
            {"username": "customer@example.com", "password": "Str0ngPass!234"},
        )
        self.assertContains(blocked_login, "Please verify your email before signing in.")

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_response = self.client.get(
            reverse("customer_account:verify_email", kwargs={"uidb64": uidb64, "token": token}),
            follow=True,
        )
        self.assertRedirects(verify_response, reverse("customer_account:dashboard"))
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        dashboard_response = self.client.get(reverse("customer_account:dashboard"))
        self.assertEqual(dashboard_response.status_code, 200)

        logout_response = self.client.get(reverse("customer_account:logout"), follow=True)
        self.assertRedirects(logout_response, reverse("customer_account:login"))

        password_reset_response = self.client.post(
            reverse("customer_account:password_reset"),
            {"email": "customer@example.com"},
            follow=True,
        )
        self.assertRedirects(password_reset_response, reverse("customer_account:password_reset_done"))
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("/account/reset/", mail.outbox[1].body)

        reset_token = default_token_generator.make_token(user)
        confirm_start = self.client.get(
            reverse("customer_account:password_reset_confirm", kwargs={"uidb64": uidb64, "token": reset_token}),
            follow=True,
        )
        self.assertEqual(confirm_start.status_code, 200)

        confirm_response = self.client.post(
            reverse("customer_account:password_reset_confirm", kwargs={"uidb64": uidb64, "token": "set-password"}),
            {"new_password1": "An0therStrong!456", "new_password2": "An0therStrong!456"},
            follow=True,
        )
        self.assertRedirects(confirm_response, reverse("customer_account:password_reset_complete"))

        final_login = self.client.post(
            reverse("customer_account:login"),
            {"username": "customer@example.com", "password": "An0therStrong!456"},
            follow=True,
        )
        self.assertRedirects(final_login, reverse("customer_account:dashboard"))


class PasswordResetSafetyTests(TestCase):
    def test_staff_user_does_not_receive_customer_reset_email(self):
        User.objects.create_user(
            username="staff@example.com",
            email="staff@example.com",
            password="Str0ngPass!234",
            is_staff=True,
            is_active=True,
        )

        response = self.client.post(
            reverse("customer_account:password_reset"),
            {"email": "staff@example.com"},
            follow=True,
        )

        self.assertRedirects(response, reverse("customer_account:password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)


class OAuthTemplateTests(TestCase):
    @override_settings(
        OAUTH_PROVIDER_STATUS={
            "apple": False,
            "facebook": False,
            "google": True,
        },
        SOCIALACCOUNT_PROVIDERS={
            "google": {
                "APPS": [
                    {
                        "client_id": "test-client-id",
                        "secret": "test-client-secret",
                        "key": "",
                    }
                ],
                "SCOPE": ["profile", "email"],
            }
        },
    )
    def test_configured_provider_button_posts_to_allauth(self):
        response = self.client.get(reverse("customer_account:login"))

        self.assertContains(response, 'action="/accounts/google/login/?process=login"')
        self.assertContains(response, 'data-oauth-provider="google"')
        self.assertContains(response, "Google OAuth is not configured yet", count=0)
        self.assertContains(response, "Apple OAuth is not configured yet")

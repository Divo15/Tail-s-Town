from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from ..forms import (
    CustomerAuthenticationForm,
    CustomerProfileForm,
    CustomerPasswordResetForm,
    CustomerRegistrationForm,
    CustomerSetPasswordForm,
)
from ..models import Order
from ..services.customers import get_customer

User = get_user_model()


class CustomerPasswordResetView(auth_views.PasswordResetView):
    form_class = CustomerPasswordResetForm
    template_name = "account/password_reset_form.html"
    email_template_name = "account/password_reset_email.txt"
    subject_template_name = "account/password_reset_subject.txt"
    success_url = "/account/password-reset/done/"


class CustomerPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "account/password_reset_done.html"


class CustomerPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = CustomerSetPasswordForm
    template_name = "account/password_reset_confirm.html"
    success_url = "/account/password-reset/complete/"


class CustomerPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "account/password_reset_complete.html"


def _send_verification_email(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = request.build_absolute_uri(
        reverse("customer_account:verify_email", kwargs={"uidb64": uidb64, "token": token})
    )
    subject = render_to_string("account/verification_email_subject.txt", {"user": user}).strip()
    message = render_to_string(
        "account/verification_email.txt",
        {
            "user": user,
            "verify_url": verify_url,
        },
    )
    send_mail(subject, message, None, [user.email], fail_silently=False)


def account_register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            _send_verification_email(request, user)
            messages.success(request, "Account created. Check your email to verify your account before signing in.")
            return redirect("customer_account:login")
    else:
        form = CustomerRegistrationForm()
    return render(request, "account/register.html", {"form": form})


def account_login(request):
    if request.method == "POST":
        form = CustomerAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Signed in.")
            return redirect("customer_account:dashboard")
    else:
        form = CustomerAuthenticationForm(request)
    return render(request, "account/login.html", {"form": form})


def account_logout(request):
    logout(request)
    return redirect("customer_account:login")


def verify_email(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=["is_active"])
        login(request, user)
        messages.success(request, "Email verified. You are signed in.")
        return redirect("customer_account:dashboard")

    messages.error(request, "This verification link is invalid or has expired.")
    return redirect("customer_account:login")


@login_required(login_url="customer_account:login")
def account_dashboard(request):
    customer = get_customer(request.user)
    recent_orders = Order.objects.filter(customer=customer).prefetch_related("items")[:5]
    saved_methods = customer.saved_payment_methods.all()
    return render(
        request,
        "account/dashboard.html",
        {
            "customer": customer,
            "recent_orders": recent_orders,
            "saved_methods": saved_methods,
        },
    )


@login_required(login_url="customer_account:login")
def profile_edit(request):
    customer = get_customer(request.user)
    if request.method == "POST":
        form = CustomerProfileForm(request.POST, instance=customer)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Profile updated.")
            return redirect("customer_account:dashboard")
    else:
        form = CustomerProfileForm(instance=customer)
    return render(request, "account/profile_form.html", {"form": form, "customer": customer})

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.password_validation import validate_password

from .models import Customer

User = get_user_model()


class CartAddForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)


class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200)
    email = forms.EmailField()
    phone = forms.CharField(max_length=30, required=False)
    line1 = forms.CharField(max_length=255, label="Address line 1")
    line2 = forms.CharField(max_length=255, required=False, label="Address line 2")
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100, initial="India")


class CustomerRegistrationForm(forms.Form):
    email = forms.EmailField()
    full_name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=30, required=False)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        if Customer.objects.filter(email=email).exists():
            raise forms.ValidationError("A customer profile with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        if password1:
            validate_password(password1)
        return cleaned_data

    def save(self):
        email = self.cleaned_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password1"],
        )
        user.is_active = False
        user.save(update_fields=["is_active"])
        Customer.objects.update_or_create(
            user=user,
            defaults={
                "full_name": self.cleaned_data["full_name"],
                "email": email,
                "phone": self.cleaned_data["phone"],
            },
        )
        return user


class CustomerAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            user = User.objects.filter(username=username.strip().lower()).first()
            if user and not user.is_active and user.check_password(password):
                raise forms.ValidationError(
                    "Please verify your email before signing in.",
                    code="email_not_verified",
                )
        return super().clean()

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.is_staff:
            raise forms.ValidationError("This login is for customers only.", code="staff_not_allowed")


class CustomerPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        users = super().get_users(email)
        return (user for user in users if not user.is_staff)


class CustomerSetPasswordForm(SetPasswordForm):
    pass


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["full_name", "email", "phone"]

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = Customer.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already used by another customer.")
        return email

    def save(self, user=None, commit=True):
        customer = super().save(commit=False)
        customer.email = self.cleaned_data["email"]
        if commit:
            customer.save()
            if user is not None:
                user.email = customer.email
                user.username = customer.email
                user.save(update_fields=["email", "username"])
        return customer

from django.urls import path
from django.views.generic import RedirectView

from . import views

account_patterns = [
    path("", views.account_dashboard, name="dashboard"),
    path("login/", views.account_login, name="login"),
    path("logout/", views.account_logout, name="logout"),
    path("register/", views.account_register, name="register"),
    path("verify/<str:uidb64>/<str:token>/", views.verify_email, name="verify_email"),
    path("password-reset/", views.CustomerPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", views.CustomerPasswordResetDoneView.as_view(), name="password_reset_done"),
    path(
        "reset/<uidb64>/<token>/",
        views.CustomerPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.CustomerPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
]

store_patterns = [
    path("", RedirectView.as_view(pattern_name="home", permanent=False), name="product_list"),
    path("faq/", views.faq_page, name="faq_page"),
    path("about/", views.about_page, name="about_page"),
    path("track-order/", views.track_order_page, name="track_order_page"),
    path("bundles/", views.bundle_page, name="bundle_page"),
    path("smart-feeder/", views.store_product_page, {"product_type": "smart-feeder"}, name="smart_feeder_page"),
    path("water-fountain/", views.store_product_page, {"product_type": "water-fountain"}, name="water_fountain_page"),
    path("litter-box/", views.store_product_page, {"product_type": "litter-box"}, name="litter_box_page"),
    path("products/<slug:slug>/", views.store_product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/items/<int:item_id>/update/", views.cart_update, name="cart_update"),
    path("cart/items/<int:item_id>/remove/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/<int:pk>/success/", views.order_success, name="order_success"),
]

urlpatterns = store_patterns

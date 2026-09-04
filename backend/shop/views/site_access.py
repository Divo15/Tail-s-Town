from django.conf import settings
from django.contrib.auth.hashers import constant_time_compare
from django.core import signing
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from shop.middleware import COOKIE_SALT, has_site_access


def _safe_destination(request):
    destination = request.POST.get("next") or request.GET.get("next") or "/"
    if url_has_allowed_host_and_scheme(
        destination,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destination
    return "/"


@never_cache
@require_http_methods(["GET", "POST"])
def site_access(request):
    destination = _safe_destination(request)

    if not settings.SITE_ACCESS_PASSWORD or has_site_access(request):
        return redirect(destination)

    error = ""
    if request.method == "POST":
        submitted_password = request.POST.get("password", "")
        if constant_time_compare(submitted_password, settings.SITE_ACCESS_PASSWORD):
            token = signing.dumps("granted", salt=COOKIE_SALT, compress=True)
            response = redirect(destination)
            response.set_cookie(
                settings.SITE_ACCESS_COOKIE_NAME,
                token,
                max_age=settings.SITE_ACCESS_COOKIE_AGE,
                secure=settings.SESSION_COOKIE_SECURE,
                httponly=True,
                samesite="Lax",
            )
            response["Cache-Control"] = "no-store"
            return response
        error = "That password is not correct. Please try again."

    response = render(
        request,
        "storefront/site_access.html",
        {"error": error, "next": destination},
        status=401 if error else 200,
    )
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response

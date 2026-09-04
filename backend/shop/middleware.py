from urllib.parse import urlencode

from django.conf import settings
from django.core import signing
from django.shortcuts import redirect
from django.urls import reverse


COOKIE_SALT = "tails-town.site-access"


def has_site_access(request):
    token = request.COOKIES.get(settings.SITE_ACCESS_COOKIE_NAME)
    if not token:
        return False

    try:
        value = signing.loads(
            token,
            salt=COOKIE_SALT,
            max_age=settings.SITE_ACCESS_COOKIE_AGE,
        )
    except signing.BadSignature:
        return False

    return value == "granted"


class SiteAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.SITE_ACCESS_PASSWORD or self._is_exempt(request.path):
            return self.get_response(request)

        if has_site_access(request):
            return self.get_response(request)

        access_url = reverse("site_access")
        query = urlencode({"next": request.get_full_path()})
        response = redirect(f"{access_url}?{query}")
        response["Cache-Control"] = "no-store"
        return response

    @staticmethod
    def _is_exempt(path):
        static_prefix = f"/{settings.STATIC_URL.lstrip('/')}"
        media_prefix = f"/{settings.MEDIA_URL.lstrip('/')}"
        exempt_prefixes = (
            reverse("site_access"),
            static_prefix,
            media_prefix,
            "/favicon.ico",
        )
        return any(path.startswith(prefix) for prefix in exempt_prefixes)

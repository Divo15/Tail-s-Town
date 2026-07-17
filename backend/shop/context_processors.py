from django.conf import settings


def oauth_providers(request):
    return {
        "oauth_provider_status": getattr(settings, "OAUTH_PROVIDER_STATUS", {}),
    }

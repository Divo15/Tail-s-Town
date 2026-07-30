import json
import logging
from types import SimpleNamespace
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


def send_bundle_enquiry_to_sheet(enquiry):
    webhook_url = getattr(settings, "BUNDLE_ENQUIRY_SHEET_WEBHOOK_URL", "")
    if not webhook_url:
        return

    submitted_at = timezone.localtime(enquiry.created_at)
    payload = {
        "submitted_at": submitted_at.isoformat(),
        "date": submitted_at.strftime("%Y-%m-%d"),
        "time": submitted_at.strftime("%H:%M:%S"),
        "bundle": enquiry.get_bundle_type_display(),
        "full_name": enquiry.full_name,
        "phone": enquiry.phone,
        "email": enquiry.email,
        "city": enquiry.city,
    }

    request = Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=4) as response:
            if response.status >= 400:
                logger.warning("Google Sheets webhook returned status %s", response.status)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        logger.warning("Could not send bundle enquiry %s to Google Sheets: %s", enquiry.pk, exc)


def send_bundle_enquiry_values_to_sheet(bundle_type, values):
    enquiry = SimpleNamespace(
        pk="no-db",
        created_at=timezone.now(),
        get_bundle_type_display=lambda: "Cat bundle" if bundle_type == "cat-bundle" else "Dog bundle",
        full_name=values.get("full_name", ""),
        phone=values.get("phone", ""),
        email=values.get("email", ""),
        city=values.get("city", ""),
    )
    send_bundle_enquiry_to_sheet(enquiry)

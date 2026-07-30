import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


def send_bundle_enquiry_to_sheet(enquiry, campaign_id=""):
    webhook_url = getattr(settings, "BUNDLE_ENQUIRY_SHEET_WEBHOOK_URL", "")
    if not webhook_url:
        return

    submitted_at = timezone.localtime(enquiry.created_at)
    payload = {
        "submitted_at": submitted_at.isoformat(),
        "date": submitted_at.strftime("%Y-%m-%d"),
        "time": submitted_at.strftime("%H:%M:%S"),
        "bundle": enquiry.get_bundle_type_display(),
        "bundle_type": enquiry.bundle_type,
        "campaign_id": campaign_id,
        "full_name": enquiry.full_name,
        "phone": enquiry.phone,
        "email": enquiry.email,
        "city": enquiry.city,
        "pet_type": enquiry.pet_type,
        "preferred_contact": enquiry.preferred_contact,
        "notes": enquiry.notes,
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

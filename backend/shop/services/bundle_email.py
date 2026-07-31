import logging

from django.conf import settings
from django.core.mail import send_mail


logger = logging.getLogger(__name__)


def _bundle_title(bundle_type):
    return "Cat care bundle" if bundle_type == "cat-bundle" else "Dog care bundle"


def send_bundle_enquiry_confirmation(bundle_type, values):
    recipient = values.get("email", "").strip()
    if not recipient:
        return

    subject = f"We received your { _bundle_title(bundle_type) } request"
    full_name = values.get("full_name", "").strip() or "there"
    city = values.get("city", "").strip()
    city_line = f"\nCity: {city}" if city else ""
    message = (
        f"Hi {full_name},\n\n"
        f"Thank you for your interest in the Tail's Town {_bundle_title(bundle_type)}.\n"
        "We received your submission and our team will reach out shortly with the next steps.\n\n"
        "Here are the details we received:\n"
        f"Name: {full_name}\n"
        f"Phone: {values.get('phone', '').strip()}\n"
        f"Email: {recipient}{city_line}\n\n"
        "If you need to update anything, reply to this email and we will help.\n\n"
        "Warmly,\n"
        "Tail's Town"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except Exception as exc:
        logger.warning("Could not send bundle confirmation email to %s: %s", recipient, exc)

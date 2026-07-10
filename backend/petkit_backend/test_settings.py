"""PostgreSQL-backed test settings used by the normal test suite."""

from .settings import *  # noqa: F401,F403


EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

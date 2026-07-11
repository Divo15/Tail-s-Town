# Production Deployment

The project can run on any Linux host that supports Python 3.12, PostgreSQL,
and a process command. The included `Procfile` is compatible with hosts such
as Render and Railway.

## Build and start commands

Use these values on the hosting platform:

```text
Build command: pip install -r requirements.txt && python backend/manage.py collectstatic --noinput && python backend/manage.py migrate --noinput
Start command: gunicorn --chdir backend petkit_backend.wsgi:application
```

`collectstatic` packages the images, CSS, JavaScript, and fonts for WhiteNoise.
Gunicorn serves Django through the production WSGI entry point.
The generated `backend/staticfiles/` folder is intentionally not committed.

## Required environment variables

Set these in the host's secret/environment settings. Do not commit a `.env`
file containing real values.

```text
DJANGO_SECRET_KEY=<long random secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com

POSTGRES_DB=<database name>
POSTGRES_USER=<database user>
POSTGRES_PASSWORD=<database password>
POSTGRES_HOST=<database host>
POSTGRES_PORT=5432
POSTGRES_CONN_MAX_AGE=60

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=<SMTP host>
EMAIL_PORT=587
EMAIL_HOST_USER=<SMTP user>
EMAIL_HOST_PASSWORD=<SMTP password>
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=PETKIT <no-reply@your-domain.com>

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

After the HTTPS domain is working, also set:

```text
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=False
```

Only enable HSTS once you are certain every relevant domain supports HTTPS.

## Media uploads

Static files are handled by WhiteNoise. Uploaded product images live under
`backend/media/`, which is local disk storage by default. That is fine only if
the host provides a persistent disk mounted to that path. For stateless hosts,
configure object storage (for example S3-compatible storage) before relying on
admin image uploads in production.

## Final checks

Run locally with production-style variables before deploying:

```powershell
cd C:\Users\HELLO!\project_petkit
$env:DJANGO_DEBUG = "False"
$env:DJANGO_SECRET_KEY = "replace-with-a-real-long-random-secret"
$env:DJANGO_ALLOWED_HOSTS = "example.com"
$env:DJANGO_CSRF_TRUSTED_ORIGINS = "https://example.com"
& .\.venv\Scripts\python.exe backend\manage.py check --deploy
```

On the host, create a staff account after migrations if no admin exists:

```text
python backend/manage.py createsuperuser
```

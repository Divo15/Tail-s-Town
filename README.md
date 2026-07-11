# Tail-s-Town

Tail-s-Town is a PETKIT-inspired smart pet care storefront built with Django, PostgreSQL, and a custom responsive frontend. The project includes product browsing, category-driven catalog management, cart and checkout flow, customer accounts, email verification, order tracking, and admin product/order management.

## Stack

- Backend: Django 6
- Database: PostgreSQL
- Images: Pillow
- PostgreSQL driver: psycopg
- Frontend: Django templates, plain HTML, CSS, and JavaScript

## Current Features

- Homepage served from Django at `/`
- Category-aware product catalog at `/shop/`
- Product detail pages at `/shop/products/<slug>/`
- Cart add, update, and remove flow
- Checkout and order creation
- Customer account dashboard
- Register, sign in, sign out
- Email verification flow
- Password reset flow
- Django admin for catalog and order management

## Project Layout

```text
project_petkit/
|-- assets/                      Shared images, fonts, and site assets used by the live Django frontend
|-- backend/
|   |-- manage.py
|   |-- petkit_backend/         Django project settings and root URLs
|   |-- postgres_test_access.sql
|   `-- shop/
|       |-- models.py           Catalog, customer, cart, address, order, and order item models
|       |-- forms.py
|       |-- urls.py
|       |-- services/           Cart, checkout, and customer helper logic
|       |-- views/
|       |   |-- account.py
|       |   |-- cart.py
|       |   |-- checkout.py
|       |   `-- storefront.py
|       `-- templates/
|           |-- account/
|           |-- store/
|           `-- storefront/
|-- frontend/                   Separate static/reference frontend snapshot
|-- .env.example
|-- .gitignore
|-- PRODUCT.md
|-- README.md
`-- requirements.txt
```

## Main Routes

- `/` - homepage
- `/shop/` - product listing
- `/shop/products/<slug>/` - product detail
- `/shop/cart/` - cart
- `/shop/checkout/` - checkout
- `/shop/orders/<id>/success/` - order success page
- `/account/` - customer dashboard
- `/account/login/` - sign in
- `/account/register/` - registration
- `/account/password-reset/` - password reset
- `/admin/` - Django admin

## Data Model

Main models in [models.py](</C:/Users/HELLO!/project_petkit/backend/shop/models.py>) include:

- `Category`
- `Product`
- `Customer`
- `Address`
- `SavedPaymentMethod`
- `Cart`
- `CartItem`
- `Order`
- `OrderItem`

## Local Setup

### 1. Create and activate a virtual environment

```powershell
cd C:\Users\HELLO!\project_petkit
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If `py` is unavailable, use your Python executable instead.

### 2. Install dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy values from `.env.example` into your local environment or `.env` workflow.

Important PostgreSQL defaults in the project settings are:

- `POSTGRES_DB=petkit_db`
- `POSTGRES_USER=petkit_admin`
- `POSTGRES_PASSWORD=petkit_admin_123!`
- `POSTGRES_HOST=127.0.0.1`
- `POSTGRES_PORT=5433`
- `POSTGRES_TEST_DB=test_petkit_db`

### 4. Run migrations

```powershell
cd backend
& "..\.venv\Scripts\python.exe" manage.py migrate
```

### 5. Start the development server

```powershell
cd backend
& "..\.venv\Scripts\python.exe" manage.py runserver
```

Open:

- [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Admin Access

The project uses Django's built-in admin panel at `/admin/`.

From there you can manage:

- categories
- products
- customers
- addresses
- carts and cart items
- orders and order items
- saved payment methods

## Email Behavior

Email settings are environment-driven. By default, the project uses the configured `EMAIL_BACKEND` value from settings and falls back to a local default sender:

- `DEFAULT_FROM_EMAIL=PETKIT <no-reply@petkit.local>`

For local development, console or local-memory backends are commonly used.

## Deployment

Production settings are environment-driven and include static-file handling,
HTTPS-aware cookies, CSRF origin configuration, PostgreSQL, and SMTP email
settings. See [DEPLOYMENT.md](DEPLOYMENT.md) for build/start commands, required
environment variables, and the media-upload persistence requirement.

## Tests

### Standard test run

```powershell
cd backend
& "..\.venv\Scripts\python.exe" manage.py test shop
```

### SQLite fallback test run

```powershell
cd backend
& "..\.venv\Scripts\python.exe" manage.py test shop --settings=petkit_backend.sqlite_test_settings
```

## PostgreSQL Test Database Permission

Django creates a separate temporary database during the normal PostgreSQL-backed test run. The application role needs permission to create that test database once.

Run this as a PostgreSQL administrator:

```powershell
cd C:\Users\HELLO!\project_petkit
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" `
  -h 127.0.0.1 -p 5433 -U postgres -d postgres `
  -f backend\postgres_test_access.sql
```

## Notes

- The live storefront is the Django-rendered experience under `backend/shop/templates/` plus shared assets in `assets/`.
- The `frontend/` folder is a separate static/reference frontend copy, not the main runtime entry point.
- Local-only folders such as `.venv`, PostgreSQL runtime bundles, agent metadata, logs, and database noise are ignored through `.gitignore`.

## Dependencies

Current Python dependencies from [requirements.txt](</C:/Users/HELLO!/project_petkit/requirements.txt>):

- `Django==6.0.6`
- `Pillow==12.3.0`
- `psycopg[binary]==3.3.4`

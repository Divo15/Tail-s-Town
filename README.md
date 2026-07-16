<<<<<<< HEAD
# PETKIT Website

PETKIT Website is a storefront-style pet care site with a Django backend for products, cart, checkout, orders, admin management, and customer accounts.

## Project Structure

```text
project_petkit/
├── index.html              # Static storefront homepage
├── styles.css              # Frontend styling
├── script.js               # Hero image slider
├── server.js               # Small local static file server
├── assets/                 # Images and media used by the frontend
└── backend/
    ├── manage.py
    ├── petkit_backend/     # Django project settings and root URLs
    └── shop/               # Django app for catalog, orders, admin, accounts
```
The map is clear now: the live Django app is under backend/ plus root assets/; frontend/ and static-site/ are duplicate/source-only material excluded from Vercel. I’m writing that distinction, the database flow, route ownership, package versions, and the test/main deployment picture into PROJECT_MAP.md.




The first file-write attempt was rejected by the patch formatter before changing anything. I’m retrying with the same content through a generated patch so every Markdown line is applied correctly; no repository files have been modified yet.

The folder also currently contains local runtime/vendor material such as `.venv`, `pyembed`, `Python312`, and `tools/postgresql18`. Those are useful locally, but they should normally be excluded from source control.

## Frontend

The public homepage is built with plain HTML, CSS, and JavaScript:

- `index.html` contains the landing page sections, header, hero, category area, support section, and footer.
- `styles.css` contains all visual styling and responsive behavior.
- `script.js` rotates the hero background slides.
- `server.js` can serve the static frontend locally.

Run the static site with:

```bash
node server.js
```

Then open:

```text
http://127.0.0.1:5173/
```

## Backend

The backend is a Django app in `backend/`.

Main models:

- `Product`: catalog items with name, description, price, stock, image, and active status.
- `Order`: customer order summary with customer name/email, shipping address, and status.
- `OrderItem`: line items attached to an order.
- `Customer`: customer profile linked one-to-one with Django's user model.
- `SavedPaymentMethod`: token reference placeholders for future payment integration.

Main routes:

- `/admin/`: Django admin for product, category, customer, cart, address, and order management.
- `/admin-panel/`: legacy redirect to `/admin/`.
- `/account/`: customer login, registration, dashboard, and profile editing.

Run Django checks with:

```bash
cd backend
..\.venv\Scripts\python.exe manage.py check
```

On Windows PowerShell, use:

```powershell
cd backend
& "..\.venv\Scripts\python.exe" manage.py check
```

## Database

Django is currently configured for PostgreSQL in `backend/petkit_backend/settings.py`.

Default environment values:

- `POSTGRES_DB=petkit_db`
- `POSTGRES_USER=petkit_admin`
- `POSTGRES_PASSWORD=petkit_admin_123!`
- `POSTGRES_HOST=127.0.0.1`
- `POSTGRES_PORT=5433`
- `POSTGRES_TEST_DB=test_petkit_db`

There is also a `backend/db.sqlite3` file in the project, but the current settings do not use SQLite.

### PostgreSQL-backed tests

Django creates an isolated database while running tests. Grant the application
role permission to create that database once, using a PostgreSQL administrator:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" `
  -h 127.0.0.1 -p 5433 -U postgres -d postgres `
  -f backend\postgres_test_access.sql
```

Then run the normal test suite:

```powershell
cd backend
& "..\.venv\Scripts\python.exe" manage.py test shop
```

The normal suite now uses PostgreSQL. For an explicit local fallback only:

```powershell
cd backend
& "..\.venv\Scripts\python.exe" manage.py test shop --settings=petkit_backend.sqlite_test_settings
```

## Known Issues

- The PostgreSQL application role needs `CREATEDB` once before it can run the
  PostgreSQL-backed Django test suite.
- Runtime/vendor folders are inside the project directory and should be ignored or moved out before committing.
- The frontend has placeholder links for search, cart, support, and several shop categories.
- Orders are associated with customers by matching `customer_email`, not by a database relationship to `Customer`.
- Admin management has been consolidated into Django's built-in `/admin/` panel.
- Payment methods are only token placeholders; there is no real payment provider flow yet.
- There is no public checkout/cart flow that creates `Order` and `OrderItem` records.

## Recommended Next Steps

1. Add `.gitignore` for `.venv`, `pyembed`, `Python312`, `tools/postgresql18/data`, `__pycache__`, database files, logs, and media uploads.
2. Add `requirements.txt` or `pyproject.toml`.
3. Fix or document the intended database path: PostgreSQL only, SQLite only, or separate dev/prod settings.
4. Add tests for registration, login, product CRUD, order status updates, and customer order visibility.
5. Decide whether the static homepage should become Django templates or remain a separate frontend.
6. Build the missing cart and checkout flow before treating this as a working ecommerce backend.
=======
# Tail-s-Town
Inspired smart pet care storefront built with Django, PostgreSQL, and a custom responsive frontend. Includes product browsing, category-based catalog management, cart, checkout, customer accounts, email verification, order tracking, and admin order/product management.
>>>>>>> b8b68421acde18cf4634545acd8317f66d423f81

# Tail's Town Repository Map

This is the working guide to the Tail's Town repository: what runs, where each component lives, how data moves, and how Git branches map to deployments.

## 1. Architecture

Tail's Town is a Django e-commerce storefront:

Browser -> Django URLs -> shop views -> services/models -> templates -> static assets

- Django owns routing, accounts, products, carts, checkout, orders, and admin.
- PostgreSQL stores production catalog, customer, cart, and order data.
- Django templates render the customer-facing pages.
- The repository assets/ directory contains the shared live CSS, JavaScript, images, fonts, and animation frames.

## 2. Live Application Paths

The live Django homepage is:

    backend/shop/templates/storefront/index.html

Live product-page template:

    backend/shop/templates/store/product_page.html

Live account templates:

    backend/shop/templates/account/

Live shop templates:

    backend/shop/templates/store/

Shared live assets:

    assets/site/
    assets/landing/
    assets/products/
    assets/product-pages/
    assets/hero/
    assets/sections/
    assets/brand/
    assets/fonts/

Important: frontend/ and static-site/ are alternate or source copies. The Django site is served from backend/ and assets/. The current .vercelignore excludes frontend/ and static-site/ from the Vercel bundle.

## 3. Repository Tree

    Tail-s-Town/
    |-- backend/
    |   |-- manage.py
    |   |-- petkit_backend/
    |   `-- shop/
    |-- assets/
    |   |-- site/
    |   |-- landing/
    |   |-- products/
    |   |-- product-pages/
    |   |-- hero/
    |   |-- sections/
    |   |-- brand/
    |   `-- fonts/
    |-- frontend/              alternate frontend copy
    |-- static-site/           alternate static site copy
    |-- requirements.txt
    |-- Procfile
    |-- railway.json
    |-- .env.example
    |-- .vercelignore
    |-- README.md
    |-- DEPLOYMENT.md
    `-- PRODUCT.md

## 4. Django Project

### backend/manage.py
Django command entry point for checks, tests, migrations, admin users, and static collection.

### backend/petkit_backend/settings.py
Production configuration. It reads DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_TRUSTED_ORIGINS, DATABASE_URL, and POSTGRES_* variables. WhiteNoise serves compressed static files. STATICFILES_DIRS points to assets/. STATIC_ROOT is backend/staticfiles/. MEDIA_ROOT is backend/media/.

### backend/petkit_backend/urls.py
Root routes:

- / -> homepage
- /shop/ -> compatibility redirect to the homepage; product pages, cart, checkout, and orders remain under /shop/
- /account/ -> account flow
- /admin/ -> Django built-in admin
- /admin-panel/ -> compatibility redirect to /admin/

### WSGI and ASGI
backend/petkit_backend/wsgi.py and asgi.py are the server entry points. The current Procfile uses WSGI with Gunicorn.

### Test settings
backend/petkit_backend/test_settings.py and sqlite_test_settings.py allow tests to run without the production PostgreSQL server.

## 5. Shop App

All Django business functionality is in backend/shop/.

### Models: backend/shop/models.py

- Category: product grouping with name and slug.
- Product: category, name, slug, SKU, brand, description, price, stock, image, and active flag.
- Customer: profile linked to a Django user.
- Address: saved shipping address.
- SavedPaymentMethod: provider token metadata; raw card data is not stored.
- Cart: one customer cart or anonymous session cart.
- CartItem: product and quantity.
- Order: customer details, shipping snapshot, status, and timestamps.
- OrderItem: product snapshot, name, quantity, unit price, and line total.

OrderItem.product and OrderItem.product_name are intentionally different: product links to the catalog when available; product_name preserves the name purchased if the catalog product is renamed or deleted.

### Views: backend/shop/views/

- storefront.py: homepage, product detail, and designed product-page data.
- cart.py: cart display, add, quantity update, remove, and stock checks.
- checkout.py: checkout, order creation, success page, and order ownership checks.
- account.py: registration, email verification, login, logout, dashboard, profile, and password reset.

### Services: backend/shop/services/

- carts.py: get/create the current customer or session cart and merge carts after login.
- customers.py: get or create customer profiles.
- checkout.py: prepare checkout data and create orders/order items.

Views handle HTTP requests; services hold reusable business rules; models hold database state.

Other app files:

- forms.py: account, profile, address, and checkout forms.
- admin.py: Django admin registrations and admin behavior.
- urls.py: account and shop route patterns.
- tests.py: automated app tests.
- migrations/: database schema history.

## 6. Route Map

### Catalog and product pages

- / -> homepage
- /shop/ -> compatibility redirect to the homepage
- /shop/products/<slug>/ -> database-backed product detail
- /shop/smart-feeder/ -> designed feeder page
- /shop/water-fountain/ -> designed fountain page
- /shop/litter-box/ -> designed litter-box page

The three designed product pages have separate presentation data and assets. They are not the same page with only a changed title.

### Cart and checkout

- /shop/cart/ -> cart detail
- /shop/cart/add/<product_id>/ -> add product
- /shop/cart/items/<item_id>/update/ -> update quantity
- /shop/cart/items/<item_id>/remove/ -> remove item
- /shop/checkout/ -> checkout and order creation
- /shop/orders/<id>/success/ -> authorized order-success page

Cart mutations use POST requests. Stock and ownership are checked server-side.

### Accounts

- /account/ -> customer dashboard
- /account/login/ -> sign in
- /account/logout/ -> sign out
- /account/register/ -> register
- /account/verify/<uidb64>/<token>/ -> email verification
- /account/password-reset/ -> request password reset
- /account/reset/<uidb64>/<token>/ -> choose a new password
- /account/profile/edit/ -> edit profile

Registration creates an inactive user and sends a verification link. Activation happens after the link is used.

## 7. Homepage Mental Map

backend/shop/templates/storefront/index.html contains the designed hero, navigation, category links, product section, smart pet ecosystem section, bundle section, support content, and footer.

Homepage content has two kinds:

- Editorial content: hero visuals, marketing copy, bundle composition, and some designed tiles are static template content.
- Catalog content: active categories and products can be queried from the database and shown in catalog/category sections.

Adding a product in Django admin updates database-backed catalog output when the product is active, assigned to the right category, and has a valid image. It does not automatically rewrite every editorial hero or marketing block.

## 8. Product Animation

The reusable product template is backend/shop/templates/store/product_page.html.

Animation ownership:

    assets/product-pages/script.js
    assets/product-pages/litter-animation.js
    assets/product-pages/litter-animation.css
    assets/product-pages/litter-sequence/desktop/
    assets/product-pages/litter-sequence/mobile/

The JavaScript maps scroll progress to frames. CSS controls the pinned stage, header offset, sizing, copy, and responsive behavior. When replacing frames, keep desktop/mobile paths, frame count, naming, loading behavior, and final-section release logic in sync.

## 9. Database Flow

Admin product -> Product and Category rows -> storefront view query -> template product card -> product detail -> cart item -> checkout -> Order and OrderItem rows.

Customer flow:

Register -> inactive Django user -> verification email -> active account -> customer profile -> personal cart -> checkout -> order history/dashboard.

Anonymous carts use a session. After login, the cart service can merge the session cart into the customer's cart.

## 10. Migrations

backend/shop/migrations/ currently contains:

- 0001_initial.py: initial schema.
- 0002_customer_savedpaymentmethod.py: saved payment metadata.
- 0003_category_product_brand_product_sku_product_slug_and_more.py: catalog/category fields.
- 0004_order_customer_order_shipping_address_snapshot_and_more.py: order/customer/shipping relationships and snapshots.

Do not edit an applied migration. Create a new one after model changes:

    python backend/manage.py makemigrations
    python backend/manage.py migrate

## 11. Dependency Versions

requirements.txt currently pins:

- Django 6.0.6
- gunicorn 23.0.0
- Pillow 12.3.0
- psycopg[binary] 3.3.4
- whitenoise 6.9.0

Python is not pinned in the repository. Local work used Python 3.12; some deployment builders selected Python 3.13. Pin a version only after choosing and testing one version consistently.

## 12. Deployment Files

- Procfile: gunicorn --chdir backend petkit_backend.wsgi:application
- railway.json: Railway configuration.
- .env.example: variable names and safe placeholders.
- .vercelignore: excludes duplicate frontend/source copies and generated/local files.
- README.md: setup and project overview.
- DEPLOYMENT.md: deployment notes.
- PRODUCT.md: product and storefront scope.

Production requires DJANGO_SECRET_KEY, DJANGO_DEBUG=False, DJANGO_ALLOWED_HOSTS, HTTPS CSRF trusted origins, DATABASE_URL or complete POSTGRES_* values, production email settings, PostgreSQL, and persistent media storage if admin uploads are used.

Run migrations after the deployment environment can reach PostgreSQL; do not depend on a build step that has no database network access.

## 13. Git And Deployment Map

| Branch | Purpose | Known repository state |
|---|---|---|
| test | Integration and deployment testing | Current working branch in the inspected checkout; tracks origin/test |
| main | Main/release history | Tracks origin/main |

Known external deployment configuration from the project work:

| Service | Branch/environment | Role |
|---|---|---|
| Vercel | Production was configured to track test during deployment work | Django/serverless deployment and preview domains |
| Railway PostgreSQL | Railway production environment | PostgreSQL database service |
| Railway app service | Separate Railway service used during deployment work | Gunicorn/Django deployment attempt |

External dashboard state can change. Verify the current branch tracking, domain, environment variables, and deployment status in Vercel and Railway before treating this table as current.

Domains used during setup included www.tails-town.com, tails-town.com, and Vercel-generated preview domains.

## 14. Where To Make Common Changes

| Goal | Main files |
|---|---|
| Homepage layout/copy | backend/shop/templates/storefront/index.html, assets/site/styles.css, assets/site/script.js |
| Product/catalog behavior | backend/shop/models.py, backend/shop/views/storefront.py, forms.py, templates/store/, admin.py, migrations/ |
| Cart behavior | backend/shop/views/cart.py, backend/shop/services/carts.py, templates/store/cart_detail.html |
| Checkout/orders | backend/shop/views/checkout.py, backend/shop/services/checkout.py, models.py, checkout.html, order_success.html |
| Login/register/verification | backend/shop/views/account.py, forms.py, templates/account/, urls.py |
| Litter animation | product_page.html, assets/product-pages/script.js, litter-animation.js/css, litter-sequence/ |
| Deployment | settings.py, requirements.txt, Procfile, railway.json, .env.example, .vercelignore |

## 15. Safe Workflow

1. Check the current branch before editing.
2. Edit the live Django path, not a duplicate file:// copy.
3. Run python backend/manage.py check.
4. Run focused tests with python backend/manage.py test shop --settings=petkit_backend.test_settings.
5. Test the affected URL through Django.
6. Check static paths, media paths, and responsive behavior.
7. Review git diff and git status.
8. Commit integration work to test.
9. Push test only after verification.
10. Promote to main deliberately.

Useful commands:

    python backend/manage.py check
    python backend/manage.py test shop --settings=petkit_backend.test_settings
    python backend/manage.py collectstatic --noinput
    git status
    git diff

## 16. Important Boundaries

- Opening a Django template with file:// shows raw template tags and does not run Django.
- The root static copies can differ from the live Django site.
- Homepage editorial sections are not fully database-driven.
- Admin-uploaded images require correctly configured production media storage.
- Vercel function size limits make large animation bundles risky.
- test and main can deploy different code.
- Never commit DATABASE_URL, secret keys, passwords, or SMTP credentials.

## 17. One-Sentence Mental Model

If the question is about what customers see, start in backend/shop/templates/; if it is about behavior, inspect backend/shop/views/ and services/; if it is about stored data, inspect models.py and migrations/; if it is about visuals, inspect assets/; and if it is about what is live, check the current Git branch plus the Vercel/Railway dashboards.

# Tail's Town Live Website Component Map

This document is the fast mental map for humans and coding agents working on the live Tail's Town website. It maps visible components and URLs to the exact repository files that own their markup, styling, behavior, data, and assets.

All paths are relative to the repository root: `Tail-s-Town/`.

## Source-of-truth rule

The deployed website is the Django application built from:

- Templates: `backend/shop/templates/`
- Views and page data: `backend/shop/views/`
- Shared live static files: `assets/`
- URL routing: `backend/petkit_backend/urls.py` and `backend/shop/urls.py`
- Database entities: `backend/shop/models.py`

Do not make live-site changes in `frontend/`. That folder is a reference/alternate copy and is excluded from the Vercel bundle by `.vercelignore`.

## Runtime mental model

```text
Browser URL
  -> backend/petkit_backend/urls.py
  -> backend/shop/urls.py
  -> backend/shop/views/*.py
  -> backend/shop/templates/**/*.html
  -> assets/**/*.css, assets/**/*.js, images, video, and fonts
  -> backend/shop/models.py / PostgreSQL when the component is data-driven
```

## Route-to-page map

| Live URL | Visible page | View/controller | Main template | Primary styles and scripts |
|---|---|---|---|---|
| `/` | Homepage/storefront | `backend/shop/views/storefront.py` → `home` | `backend/shop/templates/storefront/index.html` | `assets/site/styles.css`, `assets/site/script.js` |
| `/shop/` | Redirect to homepage | `backend/shop/urls.py` | None | None |
| `/shop/smart-feeder/` | Designed Smart Feeder page | `backend/shop/views/storefront.py` → `store_product_page` | `backend/shop/templates/store/product_page.html` | `assets/product-pages/styles.css`, `assets/product-pages/script.js` |
| `/shop/water-fountain/` | Designed Water Fountain page | `backend/shop/views/storefront.py` → `store_product_page` | `backend/shop/templates/store/product_page.html` | `assets/product-pages/styles.css`, `assets/product-pages/script.js` |
| `/shop/litter-box/` | Designed Litter Box page | `backend/shop/views/storefront.py` → `store_product_page` | `backend/shop/templates/store/product_page.html` | Product-page files plus `assets/product-pages/litter-animation.css` and `assets/product-pages/litter-animation.js` |
| `/shop/products/<slug>/` | Database-backed product details | `backend/shop/views/storefront.py` → `store_product_detail` | `backend/shop/templates/store/product_detail.html` | Inline design system in `backend/shop/templates/store/base.html` |
| `/shop/cart/` | Cart | `backend/shop/views/cart.py` → `cart_detail` | `backend/shop/templates/store/cart_detail.html` | Inline design system in `backend/shop/templates/store/base.html` |
| `/shop/checkout/` | Checkout | `backend/shop/views/checkout.py` → `checkout` | `backend/shop/templates/store/checkout.html` | Inline design system in `backend/shop/templates/store/base.html` |
| `/shop/orders/<id>/success/` | Order confirmation | `backend/shop/views/checkout.py` → `order_success` | `backend/shop/templates/store/order_success.html` | Inline design system in `backend/shop/templates/store/base.html` |
| `/account/` | Customer dashboard | `backend/shop/views/account.py` → `account_dashboard` | `backend/shop/templates/account/dashboard.html` | Inline account design system in `backend/shop/templates/account/base.html` |
| `/account/login/` | Sign in | `backend/shop/views/account.py` → `account_login` | `backend/shop/templates/account/login.html` | `backend/shop/templates/account/base.html` |
| `/account/register/` | Registration | `backend/shop/views/account.py` → `account_register` | `backend/shop/templates/account/register.html` | `backend/shop/templates/account/base.html` |
| `/account/password-reset/` | Password-reset request | `backend/shop/views/account.py` → `CustomerPasswordResetView` | `backend/shop/templates/account/password_reset_form.html` | `backend/shop/templates/account/base.html` |
| `/account/password-reset/done/` | Reset-email confirmation | Django class-based view in `backend/shop/views/account.py` | `backend/shop/templates/account/password_reset_done.html` | `backend/shop/templates/account/base.html` |
| `/account/reset/<uid>/<token>/` | Choose new password | Django class-based view in `backend/shop/views/account.py` | `backend/shop/templates/account/password_reset_confirm.html` | `backend/shop/templates/account/base.html` |
| `/account/password-reset/complete/` | Password changed | Django class-based view in `backend/shop/views/account.py` | `backend/shop/templates/account/password_reset_complete.html` | `backend/shop/templates/account/base.html` |
| `/account/profile/edit/` | Edit customer profile | `backend/shop/views/account.py` → `profile_edit` | `backend/shop/templates/account/profile_form.html` | `backend/shop/templates/account/base.html` |
| `/admin/` | Django administration | Django admin | Django admin templates | `backend/shop/admin.py` controls registered models |

## Homepage component map

Main markup: `backend/shop/templates/storefront/index.html`

Main styles: `assets/site/styles.css`

Main behavior: `assets/site/script.js`

| Visible component | Template location / selector | Behavior owner | Content or asset owner |
|---|---|---|---|
| Fixed main navigation | `.site-header`, `.brand`, `.nav-links`, `.header-actions` | Header solid-state behavior in `assets/site/script.js` | Logo/favicon files under `assets/brand/`; product links in the template |
| Account prompt and Sign Up button | `.auth-prompt`, `.auth-link-secondary` | Authentication state comes from Django `request.user` | Markup in `backend/shop/templates/storefront/index.html` |
| Cart icon | `.icon-button[aria-label="Open cart"]` | Link route in template | Cart state is handled by `backend/shop/views/cart.py` and `backend/shop/services/carts.py` |
| Rotating hero photography | `.hero`, `.hero-media`, `.hero-photo` | Slide timing/text swapping in `assets/site/script.js` | Hero images under `assets/hero/` |
| Hero headline | `#hero-title`, `.hero-content`, `.hero-accent` | Text variants in the `slides` array in `assets/site/script.js` | Initial copy in the homepage template |
| Collection introduction | `.collection-intro`, `#collection-title` | None | Static template copy |
| Product/category tiles | `#products`, `.product-band`, `.product-tile` | Hover state in `assets/site/script.js` | Data from `home()` in `backend/shop/views/storefront.py`; product/category data from `backend/shop/models.py`; imagery under `assets/landing/` and `assets/products/` |
| Feeder tile | `#feeders` | Links to designed feeder page | Product selection logic in `backend/shop/views/storefront.py` |
| Water tile | `#hydration` | Links to designed water page | Product selection logic in `backend/shop/views/storefront.py` |
| Litter tile | `#litter` | Links to designed litter page | Product selection logic in `backend/shop/views/storefront.py` |
| Bundle scene | `#bundles`, `.bundle-section`, `.bundle-living-scene` | CSS presentation | Images under `assets/landing/`; fallback markup in the homepage template |
| Bundle pet/product markers | `.pet-window`, `.bundle-product-dot` | CSS presentation | Generated by homepage template loops or fallback markup |
| Toast/status overlay | `.cart-toast` | `showToast()` in `assets/site/script.js` | Markup in homepage template |

Homepage database flow:

```text
Category + Product rows
  -> home() in backend/shop/views/storefront.py
  -> homepage_sections
  -> product/category tiles in storefront/index.html
```

## Designed product-page component map

The feeder, water, and litter routes share one template and are customized by `PRODUCT_PAGE_DATA`.

- Shared template: `backend/shop/templates/store/product_page.html`
- Per-product content/configuration: `backend/shop/views/storefront.py` → `PRODUCT_PAGE_DATA`
- Shared styling: `assets/product-pages/styles.css`
- Shared behavior: `assets/product-pages/script.js`
- Product assets: `assets/product-pages/assets/`

### Shared components

| Visible component | Template selector | Style owner | Behavior/data owner |
|---|---|---|---|
| Product navigation header | `.site-header`, `.brand`, `.nav-links`, `.header-actions` | `assets/product-pages/styles.css` | Solid/rolled-up state in `assets/product-pages/script.js`; links in `product_page.html` |
| Product page anchor rail | `.product-rail` | `assets/product-pages/styles.css` | Conditional links in `product_page.html` based on page flags |
| Product hero copy | `.detail-hero`, `.detail-copy`, `#product-title` | `assets/product-pages/styles.css` | Text in `PRODUCT_PAGE_DATA` |
| Product hero model | `.detail-stage`, `.model-card`, `.model-glass` | `assets/product-pages/styles.css` | `model_image` and `model_alt` in `PRODUCT_PAGE_DATA` |
| Floating hero labels | `.floating-chip`, `.chip-a`, `.chip-b`, `.chip-c` | `assets/product-pages/styles.css` | `chips` tuple in `PRODUCT_PAGE_DATA` |
| Add-to-cart action | `.detail-cart-form`, `.primary-action` | `assets/product-pages/styles.css` | `backend/shop/views/cart.py`, `backend/shop/forms.py`, `backend/shop/services/carts.py` |
| Live-use video | `#live-use`, `.live-product-scene`, `[data-live-video]` | `assets/product-pages/styles.css` | Lazy load/play logic in `assets/product-pages/script.js`; video/poster paths in `PRODUCT_PAGE_DATA` |
| Inside-view section | `#inside-view`, `.exploded-product` | `assets/product-pages/styles.css` | Generated from `inside_heading`, `inside_label`, and `layers` in `PRODUCT_PAGE_DATA` |
| Exploding product image | `.explode-core` | `assets/product-pages/styles.css` | One-time trigger in `assets/product-pages/script.js` for feeder and water |
| Exploding component labels | `.explode-layer`, `.layer-one` through `.layer-four` | Distances/keyframes in `assets/product-pages/styles.css` | Label text in `PRODUCT_PAGE_DATA` |
| Orbit/ring graphic | `.explode-orbit` and pseudo-elements | `assets/product-pages/styles.css` | CSS-only |
| Cart toast | `.cart-toast` | `assets/product-pages/styles.css` | `showToast()` in `assets/product-pages/script.js` |

### Smart Feeder page

Route: `/shop/smart-feeder/`

Body scope: `.detail-feeder`

| Component/asset | Source path |
|---|---|
| Copy, chips, inside labels, and page flags | `backend/shop/views/storefront.py` → `PRODUCT_PAGE_DATA["smart-feeder"]` |
| Product image | `assets/product-pages/assets/tailstown-feeder-product-transparent.webp` |
| Live-use video | `assets/product-pages/assets/feeder-dogs-eating-tailstown.mp4` |
| One-time explosion and observer | `assets/product-pages/script.js` → `singleCycleExplodedSections` |
| Explosion distance and final hold | `.detail-feeder` rules in `assets/product-pages/styles.css` |
| Short final page/scroll boundary | `.detail-feeder .exploded-product` desktop rule in `assets/product-pages/styles.css` |
| Header roll-up at bottom | `.detail-feeder .site-header.is-rolled-up` plus `setHeaderState()` |

### Water Fountain page

Route: `/shop/water-fountain/`

Body scope: `.detail-water`

| Component/asset | Source path |
|---|---|
| Copy, chips, inside labels, and page flags | `backend/shop/views/storefront.py` → `PRODUCT_PAGE_DATA["water-fountain"]` |
| Product image | `assets/product-pages/assets/tailstown-water-product-transparent.webp` |
| Live-use poster | `assets/product-pages/assets/hero-cats-water-winter-branded.webp` |
| Live-use video | `assets/product-pages/assets/water-live-tailstown.mp4` |
| One-time explosion and observer | `assets/product-pages/script.js` → `singleCycleExplodedSections` |
| Explosion distance and final hold | `.detail-water` rules in `assets/product-pages/styles.css` |
| Short final page/scroll boundary | `.detail-water .exploded-product` desktop rule in `assets/product-pages/styles.css` |
| Header roll-up at bottom | `.detail-water .site-header.is-rolled-up` plus `setHeaderState()` |

Note: `PRODUCT_PAGE_DATA["water-fountain"]["explode_class"]` still emits the historical class `water-explode-pinned`, but the old water-only scroll-scrubbing controller has been removed. Current water behavior is owned by the shared feeder/water rules above.

### Litter Box page

Route: `/shop/litter-box/`

Body scope: `.detail-litter`

| Component/asset | Source path |
|---|---|
| Copy, page flags, frame counts | `backend/shop/views/storefront.py` → `PRODUCT_PAGE_DATA["litter-box"]` |
| Hero product image | `assets/product-pages/assets/tailstown-litter-product-floating.webp` |
| Scroll animation markup/canvas/stories | `backend/shop/templates/store/product_page.html` → `.litter-animation` |
| Scroll animation styling | `assets/product-pages/litter-animation.css` |
| Canvas/frame loading and story transitions | `assets/product-pages/litter-animation.js` |
| Desktop frames | `assets/product-pages/litter-sequence/desktop/` |
| Mobile frames | `assets/product-pages/litter-sequence/mobile/` |
| Final fallback frames | `assets/product-pages/litter-sequence/final/` |

The litter page intentionally hides the normal live-use and inside-view sections through `hide_live_use` and `hide_inside_view` in `PRODUCT_PAGE_DATA`.

## Database-backed store component map

These pages extend `backend/shop/templates/store/base.html`. This base template contains the shared store shell and its CSS directly inside a `<style>` block.

| Component/page | Markup owner | Logic/data owner |
|---|---|---|
| Shared store top strip/header/nav/cart icon | `backend/shop/templates/store/base.html` | Authentication state from Django request; routes from `backend/shop/urls.py` |
| Shared messages | `backend/shop/templates/store/base.html` | Django messages emitted by views |
| Generic product hero/details | `backend/shop/templates/store/product_detail.html` | `store_product_detail()` in `backend/shop/views/storefront.py`; `Product` model |
| Product add form | `backend/shop/templates/store/product_detail.html` | `CartAddForm` in `backend/shop/forms.py`; `cart_add()` in `backend/shop/views/cart.py` |
| Related-product cards | `backend/shop/templates/store/product_detail.html` | Related-product query in `store_product_detail()` |
| Cart progress/header | `backend/shop/templates/store/cart_detail.html` → `.cart-hero`, `.cart-steps` | `cart_detail()` in `backend/shop/views/cart.py` |
| Cart item card | `.cart-item`, `.cart-controls`, `.cart-item-total` | `Cart`, `CartItem`, cart views, and `backend/shop/services/carts.py` |
| Empty cart | `.empty-cart` | Conditional markup in `cart_detail.html` |
| Cart summary | `.cart-summary` | Cart totals supplied by cart service/view |
| Cart recommendations | `.cart-recommendations` | `cart_detail()` product query |
| Checkout contact/shipping form | `backend/shop/templates/store/checkout.html` → `.checkout-form` | Checkout form in `backend/shop/forms.py`; `checkout()` view; `backend/shop/services/checkout.py` |
| Checkout item summary | `.checkout-summary`, `.checkout-items` | Current cart and calculated totals |
| Order confirmation | `backend/shop/templates/store/order_success.html` | `order_success()` and `Order`/`OrderItem` models |

## Account component map

All account pages extend `backend/shop/templates/account/base.html`. That file owns the account header, top strip, navigation, responsive layout, form/button styling, auth-page background, and password visibility JavaScript.

| Component/page | Markup owner | Logic/data owner |
|---|---|---|
| Shared account shell/header | `backend/shop/templates/account/base.html` | Login state from Django request |
| Password show/hide control | Inline script at bottom of `backend/shop/templates/account/base.html` | `[data-password-toggle]` buttons in login/register templates |
| Sign-in form | `backend/shop/templates/account/login.html` | `account_login()` in `backend/shop/views/account.py`; form in `backend/shop/forms.py` |
| Registration form | `backend/shop/templates/account/register.html` | `account_register()` in `backend/shop/views/account.py`; form in `backend/shop/forms.py` |
| OAuth buttons | `backend/shop/templates/account/_oauth_options.html` | Forms post to `django-allauth` provider URLs under `/accounts/`; provider buttons are enabled by OAuth env vars in `backend/petkit_backend/settings.py` |
| Auth photo panel | `.account-hero` in login/register templates | Background styling/asset in `backend/shop/templates/account/base.html` |
| Auth switch link | `.auth-switch` in login/register templates | Django account routes |
| Customer dashboard profile | `backend/shop/templates/account/dashboard.html` | `account_dashboard()`; `Customer` model |
| Recent orders | `backend/shop/templates/account/dashboard.html` | `Order` model/query in account view |
| Profile edit form | `backend/shop/templates/account/profile_form.html` | `profile_edit()` and profile form |
| Password-reset request | `backend/shop/templates/account/password_reset_form.html` | Django password-reset class in `backend/shop/views/account.py` |
| Password-reset sent state | `backend/shop/templates/account/password_reset_done.html` | Django password-reset workflow |
| New-password form | `backend/shop/templates/account/password_reset_confirm.html` | Django token validation/password reset |
| Password-reset completion | `backend/shop/templates/account/password_reset_complete.html` | Django password-reset workflow |
| Verification email body/subject | `backend/shop/templates/account/verification_email.txt`, `verification_email_subject.txt` | Registration/verification functions in `backend/shop/views/account.py` |

## Business-logic ownership

| Concern | Primary files |
|---|---|
| URL routing | `backend/petkit_backend/urls.py`, `backend/shop/urls.py` |
| Homepage/product queries and designed-page content | `backend/shop/views/storefront.py` |
| Account, verification, login, profile, password reset | `backend/shop/views/account.py`, `backend/shop/forms.py` |
| Cart mutations and validation | `backend/shop/views/cart.py`, `backend/shop/services/carts.py` |
| Checkout and order creation | `backend/shop/views/checkout.py`, `backend/shop/services/checkout.py` |
| Customer creation/profile helpers | `backend/shop/services/customers.py` |
| Catalog/customer/cart/order database schema | `backend/shop/models.py` |
| Admin management | `backend/shop/admin.py` |
| Database schema history | `backend/shop/migrations/` |
| Automated tests | `backend/shop/tests.py` |

## Static asset ownership

| Asset directory | Used by |
|---|---|
| `assets/site/` | Homepage CSS, JavaScript, background textures, and homepage fonts |
| `assets/brand/` | Global logo/favicon/app icons |
| `assets/hero/` | Homepage/store-base hero imagery |
| `assets/landing/` | Homepage product tiles, bundles, and lifestyle scenes |
| `assets/products/` | General product imagery |
| `assets/sections/` | Store/order-success supporting imagery |
| `assets/product-pages/` | Designed product-page CSS, JavaScript, videos, product renders, and animation frames |
| `assets/fonts/` | Shared font files |

## Fast change lookup

| Requested change | Start here |
|---|---|
| Homepage navigation, hero, product tiles, bundles | `backend/shop/templates/storefront/index.html`, then `assets/site/styles.css` and `assets/site/script.js` |
| Feeder/water/litter page copy or component labels | `PRODUCT_PAGE_DATA` in `backend/shop/views/storefront.py` |
| Feeder/water product-page layout or animation | `assets/product-pages/styles.css`, `assets/product-pages/script.js`, `backend/shop/templates/store/product_page.html` |
| Litter frame animation | `assets/product-pages/litter-animation.js`, `litter-animation.css`, and `litter-sequence/` |
| Login/register UI | `backend/shop/templates/account/login.html`, `register.html`, and `account/base.html` |
| OAuth2 buttons | `backend/shop/templates/account/_oauth_options.html`, `backend/shop/adapters.py`, `backend/shop/context_processors.py`, and `backend/petkit_backend/settings.py` |
| Generic product detail UI | `backend/shop/templates/store/product_detail.html`, `store/base.html` |
| Cart UI or behavior | `cart_detail.html`, `backend/shop/views/cart.py`, `backend/shop/services/carts.py` |
| Checkout UI or order creation | `checkout.html`, `backend/shop/views/checkout.py`, `backend/shop/services/checkout.py` |
| Product fields/admin/catalog behavior | `backend/shop/models.py`, `admin.py`, `views/storefront.py` |
| Deployment/runtime configuration | `backend/petkit_backend/settings.py`, `Procfile`, `railway.json`, `.vercelignore`, `DEPLOYMENT.md` |

## Agent handoff checklist

1. Confirm the branch with `git status --short --branch`. Vercel and Railway have been configured to deploy `test` during current development.
2. Identify the live URL in the route table above.
3. Edit the live Django template or root `assets/` file, not the `frontend/` copy.
4. If content is product-specific, check `PRODUCT_PAGE_DATA` before duplicating markup.
5. If the component is data-driven, trace the corresponding view, service, form, and model.
6. Validate JavaScript with `node --check <file>` when applicable.
7. Run `git diff --check` and inspect the complete diff.
8. Run Django checks/tests when dependencies are installed.
9. Commit and push deliberately to `test` only after validation.

## One-sentence orientation

Start with the route, find its template, follow its CSS/JavaScript references into `assets/`, then follow template variables back to the view and models; ignore `frontend/` unless the task explicitly targets the inactive reference copy.

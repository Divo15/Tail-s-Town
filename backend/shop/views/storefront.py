from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CartAddForm
from ..models import BundleEnquiry, Category, Product


PRODUCT_PAGE_DATA = {
    "smart-feeder": {
        "category_terms": ("feed", "feeder"),
        "body_class": "detail-feeder",
        "explode_class": "",
        "category": "Feeders",
        "nav_label": "Feeders",
        "eyebrow": "Smart feeding",
        "title_lines": ("Smart", "Feeder"),
        "description": "Quiet portioning for early mornings, late meetings, and cozy routines without making the kitchen feel busy.",
        "model_image": "product-pages/assets/tailstown-feeder-product-transparent.webp",
        "model_alt": "Tail's Town smart automatic pet feeder",
        "live_poster": "product-pages/assets/tailstown-feeder-product-transparent.webp",
        "live_video": "product-pages/assets/feeder-dogs-eating-tailstown.mp4",
        "live_label": "Cat and dog using the smart feeder in live motion",
        "inside_heading": "Soft mornings, built layer by layer.",
        "inside_label": "Scroll animation showing feeder components opening apart",
        "chips": (
            ("chip-a", "timed breakfast"),
            ("chip-b", "quiet motor"),
            ("chip-c", "easy bowl lift"),
        ),
        "layers": (
            ("layer-one", "sealed hopper"),
            ("layer-two", "quiet motor"),
            ("layer-three", "portion sensor"),
            ("layer-four", "lift-out bowl"),
        ),
    },
    "water-fountain": {
        "category_terms": ("water", "fountain", "hydration"),
        "body_class": "detail-water",
        "explode_class": "water-explode-pinned",
        "category": "Water",
        "nav_label": "Water",
        "eyebrow": "Fresh hydration",
        "title_lines": ("Water", "Fountain"),
        "description": "Hydrate the loved little ones with clean hydration",
        "model_image": "product-pages/assets/tailstown-water-product-transparent.webp",
        "model_alt": "Tail's Town water fountain",
        "live_poster": "product-pages/assets/hero-cats-water-winter-branded.webp",
        "live_video": "product-pages/assets/water-live-tailstown.mp4",
        "live_label": "Cats drinking from the water fountain in live motion",
        "hide_unavailable_note": True,
        "inside_heading": "Fresh water, built layer by layer.",
        "inside_label": "Scroll animation showing water fountain components opening apart",
        "chips": (
            ("chip-a", "fresh filtered flow"),
            ("chip-b", "low splash edge"),
            ("chip-c", "visible water level"),
        ),
        "layers": (
            ("layer-one", "flow arch"),
            ("layer-two", "filter core"),
            ("layer-three", "water window"),
            ("layer-four", "low-splash basin"),
        ),
    },
    "litter-box": {
        "category_terms": ("litter", "clean"),
        "body_class": "detail-litter",
        "explode_class": "litter-explode",
        "category": "Litter",
        "nav_label": "Litter",
        "eyebrow": "Clean corner",
        "title_lines": ("Litter", "Box"),
        "description": "A rounded enclosed design with a friendly front window, built for calmer indoor cat routines.",
        "model_image": "product-pages/assets/tailstown-litter-product-floating.webp",
        "model_alt": "Tail's Town rounded enclosed litter box",
        "live_poster": "product-pages/assets/tailstown-litter-product-floating.webp",
        "live_video": "product-pages/assets/shared-live.mp4",
        "live_label": "Cat using the litter box in live motion",
        "hide_live_use": True,
        "frame_sequence": True,
        "frame_count": 120,
        "available_frame_count": 75,
        "source_frame_count": 300,
        "frame_label": "Scroll-controlled smart litter box engineering reveal",
        "hide_inside_view": True,
        "inside_heading": "Private comfort, opened beautifully.",
        "inside_label": "Scroll animation showing litter box components opening apart",
        "chips": (
            ("chip-a", "smooth front entry"),
            ("chip-b", "odour-conscious shell"),
            ("chip-c", "easy daily service"),
        ),
        "layers": (
            ("layer-one", "rounded shell"),
            ("layer-two", "front entry"),
            ("layer-three", "service pod"),
            ("layer-four", "tucked tray"),
        ),
    },
}

AD_BUNDLE_DATA = {
    "cat-bundle": {
        "kind": "cat",
        "title": "Cat care bundle",
        "subtitle": "Fresh water, calmer feeding, and a cleaner litter corner in one focused routine.",
        "meta_description": "A focused Tail's Town cat bundle landing page for smart feeding, fresh hydration, and cleaner litter care.",
        "hero_image": "landing/cat-living-room-bundle.webp",
        "hero_alt": "Cat care bundle products in a warm living room with two cats",
        "detail_image": "landing/cat-bundle-litter-box.webp",
        "detail_alt": "Tail's Town litter box for calmer cat routines",
        "slides": (
            {
                "scene_src": "landing/cat-living-room-bundle.webp",
                "scene_alt": "Cat care bundle products in a warm living room with two cats",
                "product_src": "product-pages/assets/tailstown-water-product-transparent.webp",
                "product_alt": "Tail's Town water fountain product closeup",
            },
            {
                "scene_src": "landing/feeder-dispenser-living-room.webp",
                "scene_alt": "Tail's Town smart feeder styled for daily cat feeding",
                "product_src": "product-pages/assets/tailstown-feeder-product-transparent.webp",
                "product_alt": "Tail's Town smart feeder product closeup",
            },
            {
                "scene_src": "landing/cat-bundle-litter-box.webp",
                "scene_alt": "Tail's Town litter box for calmer cat routines",
                "scene_position": "78% center",
                "scene_position_mobile": "72% center",
                "product_src": "product-pages/assets/tailstown-litter-product-floating.webp",
                "product_alt": "Tail's Town litter box product closeup",
            },
        ),
        "lhs_slides": (
            {
                "src": "landing/cat-living-room-bundle.webp",
                "alt": "Cat care bundle products in a warm living room with two cats",
                "position": "center",
                "position_mobile": "52% center",
            },
        ),
        "image_quote": {
            "lead": "Because comfort has a rhythm.",
            "lead_parts": ("Because comfort", "has a rhythm."),
            "support": "Fresh water, calm meals, and a cleaner corner for the little rituals they count on.",
        },
        "rhs_video": {
            "src": "landing/cat-litter-box-use-bundle.mp4",
            "alt": "Cat using the Tail's Town automatic litter box",
            "position": "58% center",
            "position_mobile": "58% 48%",
        },
        "rhs_quote": "A quieter corner for the rituals they keep private.",
        "rhs_quote_parts": ("A quieter corner", "for private rituals."),
        "accent": "cat",
        "includes": (
            {
                "name": "Water Fountain",
                "copy": "Clean daily hydration for curious cats.",
                "url": "/shop/water-fountain/",
                "image": "landing/cat-bundle-water-fountain-sticker.webp",
                "image_alt": "Tail's Town water fountain",
            },
            {
                "name": "Litter Box",
                "copy": "A calmer enclosed corner for shared homes.",
                "url": "/shop/litter-box/",
                "image": "landing/cat-bundle-litter-box-sticker.webp",
                "image_alt": "Tail's Town litter box",
            },
            {
                "name": "Smart Feeder",
                "copy": "Quiet portions when the day gets busy.",
                "url": "/shop/smart-feeder/",
                "image": "product-pages/assets/tailstown-feeder-product-transparent.webp",
                "image_alt": "Tail's Town smart feeder",
            },
        ),
        "price_offer": {
            "label": "Bundle-only price",
            "headline": "All 3 essentials for less.",
            "items": ("$500", "$400", "$200"),
            "separate_total": "$1,100",
            "bundle_price": "$900",
            "saving": "Get the full cat care set for $900 instead of $1,100.",
            "badge": "Save $200",
        },
        "details": (
            "Built around cat routines: drinking, eating, and litter care.",
            "Uses the existing Tail's Town smart-care collection.",
            "Best for apartments, family rooms, and multi-cat corners.",
        ),
    },
    "dog-bundle": {
        "kind": "dog",
        "title": "Dog care bundle",
        "subtitle": "Meal timing and cleaner hydration for everyday dog routines.",
        "meta_description": "A focused Tail's Town dog bundle landing page for smart feeding and fresh hydration.",
        "hero_image": "landing/dog-living-room-main.webp",
        "hero_alt": "Dog care bundle feeder and water fountain in a sunlit living room",
        "detail_image": "landing/dog-water-rhs-first.webp",
        "detail_alt": "A dog drinking from the Tail's Town water fountain",
        "slides": (
            {
                "scene_src": "landing/dog-living-room-main.webp",
                "scene_alt": "Dog care bundle feeder and water fountain in a sunlit living room",
                "scene_position": "78% center",
                "scene_position_mobile": "82% center",
                "product_src": "product-pages/assets/tailstown-feeder-product-transparent.webp",
                "product_alt": "Tail's Town smart feeder product closeup",
            },
            {
                "scene_src": "landing/dog-water-rhs-first.webp",
                "scene_alt": "A dog drinking from the Tail's Town water fountain",
                "scene_position": "64% center",
                "scene_position_mobile": "70% center",
                "product_src": "product-pages/assets/tailstown-water-product-transparent.webp",
                "product_alt": "Tail's Town water fountain product closeup",
            },
        ),
        "lhs_slides": (
            {
                "src": "landing/dog-living-room-main.webp",
                "alt": "Dog care bundle feeder and water fountain in a sunlit living room",
                "position": "center",
                "position_mobile": "48% center",
            },
        ),
        "image_quote": {
            "lead": "Care that keeps pace with devotion.",
            "lead_parts": ("Care that keeps pace", "with devotion."),
            "support": "Steady meals and fresh water, ready before they need to ask.",
        },
        "rhs_quote": "Fresh water. Warm mornings. No missed moments.",
        "rhs_quote_parts": ("Fresh water.", "Warm mornings.", "No missed moments."),
        "dog_rhs_slides": (
            {
                "src": "landing/dog-water-rhs-first.webp",
                "alt": "Dog drinking from the Tail's Town water fountain in a warm living room",
                "position": "center",
                "position_mobile": "50% center",
            },
            {
                "src": "landing/dog-water-use-bundle.webp",
                "alt": "Golden retriever drinking from the Tail's Town water fountain in a warm living room",
                "position": "center",
                "position_mobile": "50% center",
            },
        ),
        "accent": "dog",
        "includes": (
            {
                "name": "Smart Feeder",
                "copy": "Timed portions for early starts and late meetings.",
                "url": "/shop/smart-feeder/",
                "image": "product-pages/assets/tailstown-feeder-product-transparent.webp",
                "image_alt": "Tail's Town smart feeder",
            },
            {
                "name": "Water Fountain",
                "copy": "Fresh water kept ready through the day.",
                "url": "/shop/water-fountain/",
                "image": "product-pages/assets/tailstown-water-product-transparent.webp",
                "image_alt": "Tail's Town water fountain",
            },
        ),
        "price_offer": {
            "label": "Bundle-only price",
            "headline": "Both dog essentials for less.",
            "items": ("$500", "$400"),
            "separate_total": "$900",
            "bundle_price": "$630",
            "saving": "Get the dog care pair for $630 instead of $900.",
            "badge": "Save $270",
        },
        "details": (
            "Built around daily dog care: feeding and hydration.",
            "Keeps the kitchen routine calmer without extra visual clutter.",
            "A focused route for dog-owner ad traffic.",
        ),
    },
}


def home(request):
    categories = list(Category.objects.filter(products__is_active=True).distinct().order_by("name")[:8])
    homepage_sections = []
    preferred_categories = (
        ("feeders", ("feed", "feeder")),
        ("hydration", ("water", "fountain", "hydration")),
        ("litter", ("litter", "clean")),
    )

    for anchor_id, matches in preferred_categories:
        category = next(
            (
                category
                for category in categories
                if any(match in category.slug.lower() or match in category.name.lower() for match in matches)
            ),
            None,
        )
        if not category:
            continue
        product = (
            Product.objects.filter(is_active=True, category=category)
            .select_related("category")
            .order_by("-created_at")
            .first()
        )
        if not product:
            continue
        homepage_sections.append(
            {
                "category": category,
                "product": product,
                "anchor_id": anchor_id,
            }
        )

    featured_categories = [section["category"] for section in homepage_sections]

    return render(
        request,
        "storefront/index.html",
        {
            "homepage_sections": homepage_sections,
            "categories": categories,
            "featured_categories": featured_categories,
            "active_product_count": Product.objects.filter(is_active=True).count(),
        },
    )


def bundle_page(request):
    return render(request, "storefront/bundles.html")


def ad_bundle_page(request, bundle_type):
    bundle = AD_BUNDLE_DATA.get(bundle_type)
    if not bundle:
        raise Http404("Ad bundle page not found")

    lead_values = {
        "full_name": "",
        "phone": "",
        "email": "",
        "city": "",
        "pet_type": bundle["kind"],
        "preferred_contact": "phone",
        "notes": "",
    }
    lead_errors = {}
    lead_submitted = request.GET.get("submitted") == "1"

    if request.method == "POST":
        lead_values = {
            "full_name": request.POST.get("full_name", "").strip(),
            "phone": request.POST.get("phone", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "city": request.POST.get("city", "").strip(),
            "pet_type": bundle["kind"],
            "preferred_contact": "phone",
            "notes": "",
        }

        if not lead_values["full_name"]:
            lead_errors["full_name"] = "Enter your name."
        if not lead_values["phone"]:
            lead_errors["phone"] = "Enter your phone number."
        if not lead_values["email"]:
            lead_errors["email"] = "Enter your email ID."
        else:
            try:
                validate_email(lead_values["email"])
            except ValidationError:
                lead_errors["email"] = "Enter a valid email ID."
        if not lead_errors:
            BundleEnquiry.objects.create(
                bundle_type=bundle_type,
                full_name=lead_values["full_name"],
                phone=lead_values["phone"],
                email=lead_values["email"],
                city=lead_values["city"],
                pet_type=lead_values["pet_type"],
                preferred_contact=lead_values["preferred_contact"],
                notes=lead_values["notes"],
            )
            return redirect(f"{request.path}?submitted=1")

    return render(
        request,
        "storefront/ad_bundle.html",
        {
            "bundle": bundle,
            "lead_errors": lead_errors,
            "lead_submitted": lead_submitted,
            "lead_values": lead_values,
        },
    )


def store_product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category"), slug=slug, is_active=True)
    related_products = Product.objects.filter(is_active=True).select_related("category").exclude(pk=product.pk)
    if product.category_id:
        related_products = related_products.filter(category=product.category)
    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "form": CartAddForm(),
            "related_products": related_products[:3],
        },
    )


def store_product_page(request, product_type):
    page = PRODUCT_PAGE_DATA.get(product_type)
    if not page:
        raise Http404("Product page not found")

    categories = Category.objects.filter(
        products__is_active=True,
    ).distinct()

    category = next(
        (
            category
            for category in categories
            if any(term in category.slug.lower() or term in category.name.lower() for term in page["category_terms"])
        ),
        None,
    )

    product = None
    if category:
        product = (
            Product.objects.filter(is_active=True, category=category)
            .select_related("category")
            .order_by("-created_at")
            .first()
        )

    return render(
        request,
        "store/product_page.html",
        {
            "page": page,
            "product": product,
            "form": CartAddForm(),
        },
    )

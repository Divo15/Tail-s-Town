from django.http import Http404
from django.shortcuts import get_object_or_404, render

from ..forms import CartAddForm
from ..models import Category, Product


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
        "explode_class": "",
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
        "frame_count": 150,
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

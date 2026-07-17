from django.shortcuts import get_object_or_404, render

from ..forms import CartAddForm
from ..models import Category, Product


def home(request):
    categories = list(Category.objects.filter(products__is_active=True).distinct().order_by("name")[:8])
    homepage_sections = []

    for index, category in enumerate(categories[:3], start=1):
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
                "anchor_id": f"category-{index}",
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


def store_product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.filter(products__is_active=True).distinct()
    category_slug = request.GET.get("category")

    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    return render(
        request,
        "store/product_list.html",
        {
            "products": products,
            "categories": categories,
            "active_category": active_category,
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

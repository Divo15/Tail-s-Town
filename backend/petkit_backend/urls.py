"""
URL configuration for petkit_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from shop import views as shop_views
from shop import urls as shop_urls

urlpatterns = [
    path('', shop_views.home, name='home'),
    path('ads', RedirectView.as_view(url='/ads/cat-bundle/', permanent=False), name='ads_landing_no_slash'),
    path('ads/', RedirectView.as_view(url='/ads/cat-bundle/', permanent=False), name='ads_landing'),
    path('ads/cat-bundle/', shop_views.ad_bundle_page, {'bundle_type': 'cat-bundle'}, name='cat_ads_bundle'),
    path('ads/dog-bundle/', shop_views.ad_bundle_page, {'bundle_type': 'dog-bundle'}, name='dog_ads_bundle'),
    path('favicon.ico', RedirectView.as_view(url='/static/brand/favicon.ico', permanent=True)),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('about/', shop_views.about_page, name='about_page_root'),
    path('about-us/', shop_views.about_page, name='about_us_page'),
    path('shop/', include((shop_urls.store_patterns, 'store'), namespace='store')),
    path('admin-panel/', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin-panel/<path:unused>', RedirectView.as_view(url='/admin/', permanent=False)),
    path('account/', include((shop_urls.account_patterns, 'customer_account'), namespace='customer_account')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
URL configuration for shop_api project.

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

from django.contrib import admin
from django.urls import include, path

from product import views as product_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/v1/categories/with_count/',
        product_views.CategoryWithCountListView.as_view(),
        name='category-with-count',
    ),
    path(
        'api/v1/categories/<int:id>/',
        product_views.CategoryRetrieveUpdateDestroyView.as_view(),
        name='category-detail',
    ),
    path(
        'api/v1/categories/',
        product_views.CategoryListCreateView.as_view(),
        name='category-list',
    ),
    path(
        'api/v1/products/with_reviews/',
        product_views.ProductWithReviewsListView.as_view(),
        name='product-with-reviews',
    ),
    path(
        'api/v1/products/<int:id>/',
        product_views.ProductRetrieveUpdateDestroyView.as_view(),
        name='product-detail',
    ),
    path(
        'api/v1/products/',
        product_views.ProductListCreateView.as_view(),
        name='product-list',
    ),
    path(
        'api/v1/reviews/<int:id>/',
        product_views.ReviewRetrieveUpdateDestroyView.as_view(),
        name='review-detail',
    ),
    path(
        'api/v1/reviews/',
        product_views.ReviewListCreateView.as_view(),
        name='review-list',
    ),
    path('api/v1/users/', include('users.urls')),
]

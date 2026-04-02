from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models import Product, Category, Review


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_per_page = 20


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ("title", "category", "price", "created", "updated")
    list_filter = ("category",)
    search_fields = ("title", "description")
    list_per_page = 20
    ordering = ("-created",)


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ("product", "stars", "display_stars")
    list_filter = ("stars",)
    search_fields = ("product__title", "text")
    list_per_page = 20

    @display(description="Оценка", label=True)
    def display_stars(self, obj):
        if obj.stars >= 4:
            return "⭐ Отлично", "success"
        elif obj.stars == 3:
            return "👍 Нормально", "warning"
        else:
            return "👎 Плохо", "danger"
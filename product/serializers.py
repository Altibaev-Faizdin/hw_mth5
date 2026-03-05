from rest_framework import serializers
from .models import Category, Product, Review
from django.db.models import Avg


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ReviewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewDetailSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = 'id', 'title', 'price', 'reviews', 'rating'

    def get_rating(self, obj):
        return obj.reviews.aggregate(avg=Avg('stars'))['avg']


class CategoryWithCountSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = 'id', 'name', 'products_count'

    def get_products_count(self, obj):
        return obj.products.count()


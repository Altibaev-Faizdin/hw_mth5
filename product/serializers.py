from rest_framework import serializers
from .models import Category, Product, Review
from django.db.models import Avg
from common.validators import validate_age_for_product_creation


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    owner_email = serializers.CharField(source='owner.email', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category', 'owner', 'owner_email', 'created', 'updated']
        read_only_fields = ['owner', 'owner_email', 'created', 'updated']


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





class CategoryValidateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, max_length=100, min_length=1)

    def create(self, validated_data):
        return Category.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class ProductValidateSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=150, min_length=1)
    description = serializers.CharField(required=True)
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2, min_value=0)
    category_id = serializers.IntegerField(required=True)

    def validate_category_id(self, category_id):
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise serializers.ValidationError('Категория с таким идентификатором не существует.')
        return category_id

    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method == 'POST':
            validate_age_for_product_creation(request)
        return attrs

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.save()
        return instance


class ReviewValidateSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)
    stars = serializers.IntegerField(required=True, min_value=1, max_value=5)
    product_id = serializers.IntegerField(required=True)

    def validate_product_id(self, product_id):
        try:
            Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Товар с таким идентификатором не существует!')
        return product_id

    def create(self, validated_data):
        return Review.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.stars = validated_data.get('stars', instance.stars)
        instance.product_id = validated_data.get('product_id', instance.product_id)
        instance.save()
        return instance
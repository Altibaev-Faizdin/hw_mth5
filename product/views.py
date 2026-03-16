from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer, CategoryDetailSerializer,
    ProductSerializer, ProductDetailSerializer,
    ReviewSerializer, ReviewDetailSerializer,
    ProductWithReviewsSerializer, CategoryWithCountSerializer,
    CategoryValidateSerializer, ProductValidateSerializer, ReviewValidateSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryValidateSerializer
        return CategorySerializer
    
    @action(detail=False, methods=['get'])
    def with_count(self, request):
        categories = Category.objects.all()
        serializer = CategoryWithCountSerializer(categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductValidateSerializer
        return ProductSerializer
    
    @action(detail=False, methods=['get'])
    def with_reviews(self, request):
        products = Product.objects.all()
        serializer = ProductWithReviewsSerializer(products, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewValidateSerializer
        return ReviewSerializer
from rest_framework import generics, permissions

from common.permissions import IsModerator
from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    CategoryValidateSerializer,
    CategoryWithCountSerializer,
    ProductSerializer,
    ProductValidateSerializer,
    ProductWithReviewsSerializer,
    ReviewSerializer,
    ReviewValidateSerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CategoryValidateSerializer
        return CategorySerializer


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return CategoryValidateSerializer
        return CategorySerializer


class CategoryWithCountListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryWithCountSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [IsModerator()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductValidateSerializer
        return ProductSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    lookup_field = 'id'
    permission_classes = [IsModerator]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProductValidateSerializer
        return ProductSerializer


class ProductWithReviewsListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductWithReviewsSerializer
    permission_classes = [IsModerator]


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewValidateSerializer
        return ReviewSerializer


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ReviewValidateSerializer
        return ReviewSerializer

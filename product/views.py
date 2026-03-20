from rest_framework.response import Response
from rest_framework import status, viewsets, generics
from rest_framework.decorators import action, api_view
from .models import Category, Product, Review, ConfirmationCode
from .serializers import (
    CategorySerializer, CategoryDetailSerializer,
    ProductSerializer, ProductDetailSerializer,
    ReviewSerializer, ReviewDetailSerializer,
    ProductWithReviewsSerializer, CategoryWithCountSerializer,
    CategoryValidateSerializer, ProductValidateSerializer, ReviewValidateSerializer,
    UserRegistrationSerializer, UserLoginSerializer, ConfirmationCodeSerializer, UserSerializer
)
from django.contrib.auth.models import User


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

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = ConfirmationCode.objects.get(user=user)
        return Response({
            'message': 'Пользователь успешно зарегистрирован. Пожалуйста, проверьте свою электронную почту для получения кода подтверждения.',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'confirmation_code': confirmation_code.code 
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Вход успешен',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)


class UserConfirmView(generics.CreateAPIView):
    serializer_class = ConfirmationCodeSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        confirmation = serializer.validated_data['confirmation']
        
        user.is_active = True
        user.save()
        
        confirmation.delete()
        
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Адрес электронной почты успешно подтвержден. Ваш аккаунт теперь активен..',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
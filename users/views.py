from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, ConfirmationCode
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ConfirmationCodeSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        confirmation_code = ConfirmationCode.objects.get(user=user)
        
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Пользователь успешно зарегистрирован. Подтвердите email-адрес.',
            'user': user_serializer.data,
            'confirmation_code': confirmation_code.code  
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.CreateAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        refresh['birthdate'] = user.birthdate.isoformat() if user.birthdate else None
        
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Вход успешен!',
            'user': user_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class UserConfirmView(generics.CreateAPIView):
    serializer_class = ConfirmationCodeSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        user.is_active = True
        user.save()
        
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Email-адрес успешно подтверждён. Аккаунт активирован.',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)
    
    def get_permissions(self):
        return [permission() for permission in self.permission_classes]
    
    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Только сотрудники могут просматривать список пользователей.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

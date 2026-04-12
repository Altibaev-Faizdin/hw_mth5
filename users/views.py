from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .google_oauth import GoogleOAuthError, exchange_authorization_code, fetch_userinfo
from .models import CustomUser, ConfirmationCode
from .serializers import (
    ConfirmationCodeSerializer,
    GoogleOAuthSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
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
        return Response(
            {
                'message': 'Пользователь успешно зарегистрирован. Подтвердите email-адрес.',
                'user': user_serializer.data,
                'confirmation_code': confirmation_code.code,
            },
            status=status.HTTP_201_CREATED,
        )


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
        return Response(
            {
                'message': 'Вход успешен!',
                'user': user_serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class GoogleOAuthView(generics.GenericAPIView):
    """POST: code + redirect_uri с фронта → JWT (обмен кода на токены — вручную, см. google_oauth)."""

    permission_classes = [AllowAny]
    serializer_class = GoogleOAuthSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']
        redirect_uri = serializer.validated_data['redirect_uri']

        client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '') or ''
        client_secret = getattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET', '') or ''
        if not client_id or not client_secret:
            return Response(
                {'detail': 'Google OAuth не настроен (GOOGLE_OAUTH_CLIENT_ID / SECRET).'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            tokens = exchange_authorization_code(code, redirect_uri, client_id, client_secret)
        except GoogleOAuthError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

        access_token = tokens.get('access_token')
        if not access_token:
            return Response(
                {'detail': 'Ответ Google не содержит access_token.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            profile = fetch_userinfo(access_token)
        except GoogleOAuthError as e:
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

        email_raw = (profile.get('email') or '').strip()
        if not email_raw:
            return Response(
                {'detail': 'В профиле Google нет email; выберите аккаунт с почтой.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = CustomUser.objects.normalize_email(email_raw)
        given = (profile.get('given_name') or '')[:150]
        family = (profile.get('family_name') or '')[:150]
        sub = (profile.get('sub') or '')[:255]

        now = timezone.now()
        user = CustomUser.objects.filter(email__iexact=email).first()

        if user is None:
            user = CustomUser(
                email=email,
                registration_source=CustomUser.RegistrationSource.GOOGLE,
            )
            user.set_unusable_password()

        user.first_name = given or user.first_name
        user.last_name = family or user.last_name
        user.is_active = True
        user.last_login = now
        if sub:
            sub_qs = CustomUser.objects.filter(google_sub=sub)
            if user.pk:
                sub_qs = sub_qs.exclude(pk=user.pk)
            if sub_qs.exists():
                return Response(
                    {'detail': 'Этот Google-аккаунт уже привязан к другому пользователю.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.google_sub = sub
        user.save()

        refresh = RefreshToken.for_user(user)
        refresh['birthdate'] = user.birthdate.isoformat() if user.birthdate else None

        user_serializer = UserSerializer(user)
        return Response(
            {
                'message': 'Вход через Google выполнен.',
                'user': user_serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


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
        return Response(
            {
                'message': 'Email-адрес успешно подтверждён. Аккаунт активирован.',
                'user': user_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()

    def list(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {'detail': 'Только сотрудники могут просматривать список пользователей.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)


class UserRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

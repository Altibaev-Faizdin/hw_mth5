from rest_framework import serializers
from .models import CustomUser, ConfirmationCode


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'},
        label='Confirm Password'
    )
    phone_number = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Phone number is optional for regular users'
    )
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password2', 'phone_number']
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email уже зарегистрирован!')
        return value
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Пароли не совпадают!'
            })
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        ConfirmationCode.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Неверные учетные данные!')
        
        if not user.check_password(password):
            raise serializers.ValidationError('Неверные учетные данные!')
        
        if not user.is_active:
            raise serializers.ValidationError(
                'Учетная запись не активирована. Пожалуйста, подтвердите свою электронную почту.'
            )
        
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'phone_number', 'is_active', 'is_staff', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phone_number']


class ConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text='6-digit confirmation code'
    )
    
    def validate(self, data):
        email = data.get('email')
        code = data.get('code')
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError('Пользователь с таким email не найден!')
        
        try:
            confirmation = ConfirmationCode.objects.get(user=user)
        except ConfirmationCode.DoesNotExist:
            raise serializers.ValidationError('Код подтверждения не найден для этого пользователя!')
        
        if confirmation.code != code:
            raise serializers.ValidationError('Неверный код подтверждения!')
        
        data['user'] = user
        data['confirmation'] = confirmation
        return data

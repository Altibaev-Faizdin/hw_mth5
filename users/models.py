from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
import random


def generate_confirmation_code():
    return str(random.randint(100000, 999999))


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class RegistrationSource(models.TextChoices):
        LOCAL = 'local', 'Local'
        GOOGLE = 'google', 'Google'
        FACEBOOK = 'facebook', 'Facebook'

    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        help_text='Phone number. Required for superusers.'
    )
    birthdate = models.DateField(blank=True, null=True)
    registration_source = models.CharField(
        max_length=32,
        choices=RegistrationSource.choices,
        default=RegistrationSource.LOCAL,
    )
    google_sub = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text='OpenID subject из Google (sub), для привязки аккаунта.',
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        name = ' '.join(p for p in (self.first_name, self.last_name) if p).strip()
        return name or self.email
    
    def get_short_name(self):
        return self.first_name or self.email


class ConfirmationCode(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='confirmation_code')
    code = models.CharField(max_length=6, default=generate_confirmation_code)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Confirmation Code'
        verbose_name_plural = 'Confirmation Codes'
    
    def __str__(self):
        return f"Код подтверждения для {self.user.email}"


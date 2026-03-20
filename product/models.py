from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
import random



def generate_confirmation_code():
    return str(random.randint(100000, 999999))


class ConfirmationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='confirmation_code')
    code = models.CharField(max_length=6, default=generate_confirmation_code)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Код подтверждения для {self.user.username}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Review(models.Model):
    text = models.TextField()
    stars = models.IntegerField(
    default=1,
    validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ]
)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
 
    def __str__(self):
        return f"Обзор для {self.product.title}"

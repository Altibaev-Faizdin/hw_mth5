from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

router = DefaultRouter()
router.register(r'', views.UserViewSet, basename='user')

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('confirm/', views.UserConfirmView.as_view(), name='confirm'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]

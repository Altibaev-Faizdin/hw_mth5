from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('oauth/google/', views.GoogleOAuthView.as_view(), name='google-oauth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('confirm/', views.UserConfirmView.as_view(), name='confirm'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('me/', views.CurrentUserView.as_view(), name='user-me'),
    path('<int:pk>/', views.UserRetrieveView.as_view(), name='user-detail'),
    path('', views.UserListView.as_view(), name='user-list'),
]

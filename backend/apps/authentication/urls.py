from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('social-accounts/', views.SocialAccountListView.as_view(), name='social-accounts'),
    path('social/connect/', views.connect_social_account, name='connect-social'),
    path('social/disconnect/<str:provider>/', views.disconnect_social_account, name='disconnect-social'),
]

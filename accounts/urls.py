from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # User management
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('users/', views.users_list, name='users'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    
    # Organization management
    path('organization/', views.organization_settings, name='organization'),
    path('subscription/', views.subscription_info, name='subscription'),
    path('upgrade/', views.upgrade_plan, name='upgrade'),
    
    # Password management
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='auth/password_change.html',
        success_url='/accounts/profile/'
    ), name='password_change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html'
    ), name='password_reset'),
]
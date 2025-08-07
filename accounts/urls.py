from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_lang

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
    path('users/export/', views.export_users, name='export_users'),
    path('users/bulk-actions/', views.bulk_user_actions, name='bulk_user_actions'),
    
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
    
    # Language switching
    path('set-language/', views_lang.set_language, name='set_language'),
    path('set-language-ajax/', views_lang.set_language_ajax, name='set_language_ajax'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/create-samples/', views.create_sample_notifications, name='create_sample_notifications'),
]
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('quick-stats/', views.quick_stats, name='quick_stats'),
    path('refresh/', views.dashboard_refresh, name='refresh'),
]
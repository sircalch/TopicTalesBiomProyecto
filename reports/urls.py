from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.index, name='index'),
    path('patients/', views.patients_report, name='patients'),
    path('appointments/', views.appointments_report, name='appointments'),
    path('financial/', views.financial_report, name='financial'),
    path('analytics/', views.analytics_report, name='analytics'),
]
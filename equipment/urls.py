from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    path('', views.equipment_list, name='list'),
    path('create/', views.equipment_create, name='create'),
    path('<int:equipment_id>/', views.equipment_detail, name='detail'),
    path('<int:equipment_id>/maintenance/', views.maintenance_schedule, name='maintenance'),
]
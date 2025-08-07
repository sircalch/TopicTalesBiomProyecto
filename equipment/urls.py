from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # Dashboard principal
    path('', views.equipment_list, name='list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Gestión de equipos
    path('create/', views.equipment_create, name='create'),
    path('<int:pk>/', views.equipment_detail, name='detail'),
    path('<int:pk>/edit/', views.equipment_edit, name='edit'),
    
    # Mantenimiento
    path('<int:pk>/maintenance/', views.maintenance_schedule, name='maintenance'),
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    
    # Registro de uso
    path('<int:pk>/usage/', views.usage_log_create, name='usage_log'),
    
    # Gestión de categorías, ubicaciones y proveedores
    path('categories/', views.categories_list, name='categories'),
    path('locations/', views.locations_list, name='locations'),
    path('suppliers/', views.suppliers_list, name='suppliers'),
    
    # Exportación y acciones en lote
    path('export/', views.equipment_export, name='export'),
    path('bulk-actions/', views.bulk_actions, name='bulk_actions'),
    
    # API endpoints
    path('api/<int:pk>/alerts/', views.api_equipment_alerts, name='api_alerts'),
]
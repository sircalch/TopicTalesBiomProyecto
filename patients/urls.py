from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='list'),
    path('search/', views.patient_search, name='search'),
    path('create/', views.patient_create, name='create'),
    path('<int:patient_id>/', views.patient_detail, name='detail'),
    path('<int:patient_id>/edit/', views.patient_edit, name='edit'),
    path('<int:patient_id>/medical-history/', views.medical_history, name='medical_history'),
    path('<int:patient_id>/vital-signs/', views.vital_signs, name='vital_signs'),
    path('<int:patient_id>/documents/', views.documents, name='documents'),
    
    # Export functionality
    path('export/excel/', views.export_patients_excel, name='export_excel'),
    path('export/pdf/', views.export_patients_pdf, name='export_pdf'),
    path('export/csv/', views.export_patients_csv, name='export_csv'),
    
    # AJAX endpoints
    path('api/quick-actions/', views.patient_quick_actions, name='quick_actions'),
]
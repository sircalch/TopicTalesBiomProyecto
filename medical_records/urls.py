from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_records, name='search'),
    
    # Patient Medical Records
    path('patient/<int:patient_id>/', views.patient_records, name='patient_records'),
    path('patient/<int:patient_id>/edit/', views.edit_medical_record, name='edit_record'),
    
    # Consultations
    path('patient/<int:patient_id>/consultations/', views.consultations_list, name='consultations_list'),
    path('patient/<int:patient_id>/consultation/create/', views.create_consultation, name='create_consultation'),
    path('consultation/<int:consultation_id>/', views.consultation_detail, name='consultation_detail'),
    path('consultation/<int:consultation_id>/edit/', views.edit_consultation, name='edit_consultation'),
    
    # Vital Signs, Lab Results, Prescriptions
    path('consultation/<int:consultation_id>/vital-signs/add/', views.add_vital_signs, name='add_vital_signs'),
    path('consultation/<int:consultation_id>/lab-result/add/', views.add_lab_result, name='add_lab_result'),
    path('consultation/<int:consultation_id>/prescription/add/', views.add_prescription, name='add_prescription'),
    
    # Documents and Alerts
    path('patient/<int:patient_id>/document/upload/', views.upload_document, name='upload_document'),
    path('patient/<int:patient_id>/alert/create/', views.create_alert, name='create_alert'),
]
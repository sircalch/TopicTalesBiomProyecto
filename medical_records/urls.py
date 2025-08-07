from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_records, name='search'),
    path('consultations/', views.all_consultations, name='all_consultations'),
    path('create/', views.create_medical_record, name='create_record'),
    path('templates/', views.record_templates, name='templates'),
    path('clinical-history/', views.clinical_history, name='clinical_history'),
    
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
    
    # Template Management
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/<int:template_id>/', views.template_detail, name='template_detail'),
    path('templates/<int:template_id>/edit/', views.edit_template, name='edit_template'),
    path('templates/<int:template_id>/duplicate/', views.duplicate_template, name='duplicate_template'),
    path('templates/<int:template_id>/delete/', views.delete_template, name='delete_template'),
    path('templates/<int:template_id>/use/', views.use_template, name='use_template'),
]
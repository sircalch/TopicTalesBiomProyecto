from django.urls import path
from . import views
from .views_new import specialties_dashboard

app_name = 'specialties'

urlpatterns = [
    # Dashboard principal - NUEVA VERSION LIMPIA
    path('', specialties_dashboard, name='index'),
    # Dashboard original (backup)
    path('old/', views.index, name='index_old'),
    
    # Especialidades
    path('list/', views.specialty_list, name='specialty_list'),
    path('specialty/<int:pk>/', views.specialty_detail, name='specialty_detail'),
    
    # Doctores
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctor/<int:pk>/', views.doctor_detail, name='doctor_detail'),
    
    # Consultas
    path('consultations/', views.consultation_list, name='consultation_list'),
    path('consultation/<int:pk>/', views.consultation_detail, name='consultation_detail'),
    path('consultation/create/', views.create_consultation, name='create_consultation'),
    
    # Tratamientos
    path('treatments/', views.treatment_list, name='treatment_list'),
    path('treatment/<int:pk>/', views.treatment_detail, name='treatment_detail'),
    
    # Referencias
    path('referrals/', views.referral_list, name='referral_list'),
    path('referral/<int:pk>/', views.referral_detail, name='referral_detail'),
    path('referral/create/', views.create_referral, name='create_referral'),
    
    # Procedimientos
    path('procedures/', views.procedures_list, name='procedures_list'),
    
    # Vistas específicas por especialidad (compatibilidad)
    path('nutrition/', views.nutrition, name='nutrition'),
    path('psychology/', views.psychology, name='psychology'),
    
    # Pediatría - Submenu
    path('pediatrics/', views.pediatrics, name='pediatrics'),
    path('pediatrics/consultations/', views.pediatric_consultations, name='pediatric_consultations'),
    path('pediatrics/growth-charts/', views.growth_charts, name='growth_charts'),
    path('pediatrics/vaccines/', views.vaccine_control, name='vaccines'),
    path('pediatrics/development/', views.child_development, name='development'),
    
    # Cardiología - Submenu
    path('cardiology/', views.cardiology, name='cardiology'),
    path('cardiology/ecg/', views.ecg_management, name='ecg'),
    path('cardiology/echo/', views.echocardiogram, name='echo'),
    path('cardiology/stress-test/', views.stress_test, name='stress_test'),
    path('cardiology/rehabilitation/', views.cardiac_rehabilitation, name='cardiac_rehabilitation'),
    
    # Oftalmología - Submenu
    path('ophthalmology/', views.ophthalmology, name='ophthalmology'),
    path('ophthalmology/eye-exams/', views.eye_exams, name='eye_exams'),
    path('ophthalmology/vision-tests/', views.vision_tests, name='vision_tests'),
    path('ophthalmology/prescriptions/', views.optical_prescriptions, name='prescriptions'),
    path('ophthalmology/surgeries/', views.eye_surgeries, name='surgeries'),
    
    # Odontología - Submenu
    path('dentistry/', views.dentistry, name='dentistry'),
    path('dentistry/dental-exams/', views.dental_exams, name='dental_exams'),
    path('dentistry/treatments/', views.dental_treatments, name='treatments'),
    path('dentistry/orthodontics/', views.orthodontics, name='orthodontics'),
    path('dentistry/oral-surgery/', views.oral_surgery, name='oral_surgery'),
    
    # Dermatología - Submenu
    path('dermatology/', views.dermatology, name='dermatology'),
    path('dermatology/skin-exams/', views.skin_exams, name='skin_exams'),
    path('dermatology/dermatoscopy/', views.dermatoscopy, name='dermatoscopy'),
    path('dermatology/treatments/', views.dermatology_treatments, name='dermatology_treatments'),
    path('dermatology/cosmetic/', views.cosmetic_dermatology, name='cosmetic'),
    
    # Ginecología - Submenu
    path('gynecology/', views.gynecology, name='gynecology'),
    path('gynecology/gynecologic-exams/', views.gynecologic_exams, name='gynecologic_exams'),
    path('gynecology/pregnancy/', views.prenatal_control, name='pregnancy'),
    path('gynecology/pap-smear/', views.pap_smear, name='pap_smear'),
    path('gynecology/contraception/', views.contraception, name='contraception'),
    
    # Traumatología - Submenu
    path('traumatology/', views.traumatology, name='traumatology'),
    path('traumatology/xrays/', views.xray_management, name='xrays'),
    path('traumatology/fractures/', views.fracture_management, name='fractures'),
    path('traumatology/therapy/', views.physiotherapy, name='therapy'),
    path('traumatology/surgeries/', views.orthopedic_surgeries, name='orthopedic_surgeries'),
    
    # API endpoints
    path('api/specialty/<int:specialty_id>/doctors/', views.api_specialty_doctors, name='api_specialty_doctors'),
    path('api/specialty/<int:specialty_id>/procedures/', views.api_specialty_procedures, name='api_specialty_procedures'),
    
    # AJAX endpoints for dashboard functionality - TEMPORARILY DISABLED
    # path('ajax/dashboard-stats/', views.ajax_dashboard_stats, name='ajax_dashboard_stats'),
    path('ajax/complete-consultation/<int:consultation_id>/', views.ajax_complete_consultation, name='ajax_complete_consultation'),
    path('ajax/process-referral/<int:referral_id>/', views.ajax_process_referral, name='ajax_process_referral'),
    path('ajax/specialty-activity/<int:specialty_id>/', views.ajax_specialty_activity, name='ajax_specialty_activity'),
    path('ajax/search-specialties/', views.ajax_search_specialties, name='ajax_search_specialties'),
    path('ajax/doctor-availability/<int:doctor_id>/', views.ajax_doctor_availability, name='ajax_doctor_availability'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'api'

# Router para ViewSets
router = DefaultRouter()
router.register(r'patients', views.PatientViewSet)
router.register(r'appointments', views.AppointmentViewSet)
router.register(r'medical-records', views.MedicalRecordViewSet)
router.register(r'specialties', views.SpecialtyViewSet)
router.register(r'doctors', views.DoctorViewSet)
router.register(r'consultations', views.SpecialtyConsultationViewSet)
router.register(r'reports', views.ReportViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    # Autenticación
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/user/', views.current_user, name='current_user'),
    
    # Dashboard y estadísticas
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/recent-activity/', views.recent_activity, name='recent_activity'),
    
    # Búsqueda global
    path('search/', views.global_search, name='global_search'),
    
    # Endpoints específicos
    path('patients/<int:patient_id>/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patients/<int:patient_id>/medical-records/', views.patient_medical_records, name='patient_medical_records'),
    path('appointments/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointments/calendar/', views.appointments_calendar, name='appointments_calendar'),
    
    # Especialidades
    path('specialties/<int:specialty_id>/doctors/', views.specialty_doctors, name='specialty_doctors'),
    path('specialties/<int:specialty_id>/procedures/', views.specialty_procedures, name='specialty_procedures'),
    
    # Reportes
    path('reports/<int:report_id>/generate/', views.generate_report, name='generate_report'),
    path('reports/<int:report_id>/download/', views.download_report_api, name='download_report_api'),
    
    # Facturación
    path('invoices/<int:invoice_id>/send/', views.send_invoice, name='send_invoice'),
    path('invoices/<int:invoice_id>/mark-paid/', views.mark_invoice_paid, name='mark_invoice_paid'),
    
    # Subir archivos
    path('upload/document/', views.upload_document, name='upload_document'),
    path('upload/profile-image/', views.upload_profile_image, name='upload_profile_image'),
    
    # Configuración del sistema
    path('system/modules/', views.system_modules, name='system_modules'),
    path('system/settings/', views.system_settings, name='system_settings'),
    
    # Incluir las rutas del router
    path('', include(router.urls)),
]
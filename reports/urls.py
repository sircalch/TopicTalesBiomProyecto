from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard principal
    path('', views.index, name='index'),
    
    # Gestión de reportes
    path('list/', views.report_list, name='list'),
    path('create/', views.create_report, name='create'),
    path('<int:pk>/', views.report_detail, name='detail'),
    path('<int:pk>/download/', views.download_report, name='download'),
    path('<int:pk>/share/', views.share_report, name='share'),
    
    # Tipos de reportes específicos
    path('patients/', views.patients_report, name='patients'),
    path('patients/export/excel/', views.export_patients_excel, name='export_patients_excel'),
    path('patients/export/pdf/', views.export_patients_pdf, name='export_patients_pdf'),
    path('appointments/', views.appointments_report, name='appointments'),
    path('financial/', views.financial_report, name='financial'),
    path('analytics/', views.analytics_report, name='analytics'),
    path('custom/', views.custom_report, name='custom'),
    
    # Plantillas
    path('templates/', views.templates_list, name='templates'),
    path('templates/create/', views.create_template, name='create_template'),
    
    # API endpoints
    path('api/<int:pk>/status/', views.api_report_status, name='api_status'),
    path('api/<int:pk>/delete/', views.api_delete_report, name='api_delete'),
]
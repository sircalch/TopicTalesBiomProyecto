from django.urls import path
from . import views

app_name = 'psychology'

urlpatterns = [
    # Dashboard
    path('', views.psychology_dashboard, name='dashboard'),
    
    # Evaluaciones Psicológicas
    path('evaluaciones/', views.evaluation_list, name='evaluation_list'),
    path('evaluaciones/nueva/', views.evaluation_create, name='evaluation_create'),
    path('evaluaciones/<int:pk>/', views.evaluation_detail, name='evaluation_detail'),
    path('evaluaciones/<int:pk>/editar/', views.evaluation_edit, name='evaluation_edit'),
    
    # Tests Psicológicos
    path('tests/', views.test_list, name='test_list'),
    path('tests/nuevo/', views.test_create, name='test_create'),
    
    # Sesiones de Terapia
    path('sesiones/', views.session_list, name='session_list'),
    path('sesiones/nueva/', views.session_create, name='session_create'),
    path('sesiones/<int:pk>/', views.session_detail, name='session_detail'),
    
    # Planes de Tratamiento
    path('planes/', views.treatment_plan_list, name='treatment_plan_list'),
    path('planes/nuevo/', views.treatment_plan_create, name='treatment_plan_create'),
    path('planes/<int:pk>/', views.treatment_plan_detail, name='treatment_plan_detail'),
    
    # Objetivos Psicológicos
    path('objetivos/', views.goal_list, name='goal_list'),
    path('objetivos/nuevo/', views.goal_create, name='goal_create'),
    path('objetivos/<int:pk>/', views.goal_detail, name='goal_detail'),
    
    # APIs
    path('api/paciente/<int:patient_id>/evaluaciones/', views.patient_evaluations_api, name='patient_evaluations_api'),
    path('api/evaluacion/<int:evaluation_id>/resumen/', views.evaluation_summary_api, name='evaluation_summary_api'),
]
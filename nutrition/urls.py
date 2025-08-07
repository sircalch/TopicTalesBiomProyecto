from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    # Dashboard
    path('', views.nutrition_dashboard, name='dashboard'),
    
    # Evaluaciones Nutricionales
    path('assessments/', views.assessment_list, name='assessment_list'),
    path('assessments/create/', views.assessment_create, name='assessment_create'),
    path('assessments/<int:pk>/', views.assessment_detail, name='assessment_detail'),
    path('assessments/<int:pk>/edit/', views.assessment_edit, name='assessment_edit'),
    
    # Planes Dietéticos
    path('diet-plans/', views.diet_plan_list, name='diet_plan_list'),
    path('diet-plans/create/', views.diet_plan_create, name='diet_plan_create'),
    path('diet-plans/<int:pk>/', views.diet_plan_detail, name='diet_plan_detail'),
    
    # Menús de Comida
    path('diet-plans/<int:diet_plan_id>/meals/create/', views.meal_plan_create, name='meal_plan_create'),
    
    # Consultas Nutricionales
    path('consultations/', views.consultation_list, name='consultation_list'),
    path('consultations/create/', views.consultation_create, name='consultation_create'),
    path('consultations/<int:pk>/', views.consultation_detail, name='consultation_detail'),
    
    # Metas Nutricionales
    path('goals/', views.nutrition_goals_list, name='goals_list'),
    path('goals/create/', views.nutrition_goal_create, name='goal_create'),
    
    # API Endpoints
    path('api/patient/<int:patient_id>/assessments/', views.api_patient_assessments, name='api_patient_assessments'),
    path('api/bmi-calculator/', views.api_bmi_calculator, name='api_bmi_calculator'),
    path('api/calorie-calculator/', views.api_calorie_calculator, name='api_calorie_calculator'),
]
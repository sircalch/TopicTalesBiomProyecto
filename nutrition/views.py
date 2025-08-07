from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import (
    NutritionalAssessment, 
    DietPlan, 
    MealPlan, 
    FoodItem, 
    NutritionConsultation, 
    NutritionGoal
)
from .forms import (
    NutritionalAssessmentForm, 
    DietPlanForm, 
    MealPlanForm, 
    NutritionConsultationForm, 
    NutritionGoalForm,
    PatientSearchForm
)
from patients.models import Patient


@login_required
def nutrition_dashboard(request):
    """Dashboard principal del módulo de nutrición"""
    
    # Obtener estadísticas generales
    total_assessments = NutritionalAssessment.objects.filter(
        patient__organization=request.user.profile.organization
    ).count()
    
    total_diet_plans = DietPlan.objects.filter(
        assessment__patient__organization=request.user.profile.organization
    ).count()
    
    active_plans = DietPlan.objects.filter(
        assessment__patient__organization=request.user.profile.organization,
        is_active=True
    ).count()
    
    recent_consultations = NutritionConsultation.objects.filter(
        patient__organization=request.user.profile.organization
    ).count()
    
    # Evaluaciones recientes
    recent_assessments = NutritionalAssessment.objects.filter(
        patient__organization=request.user.profile.organization
    ).order_by('-created_at')[:5]
    
    # Consultas próximas
    upcoming_consultations = NutritionConsultation.objects.filter(
        patient__organization=request.user.profile.organization,
        next_appointment__gte=timezone.now()
    ).order_by('next_appointment')[:5]
    
    # Estadísticas de IMC por categorías
    bmi_stats = {}
    assessments = NutritionalAssessment.objects.filter(
        patient__organization=request.user.profile.organization
    )
    
    for assessment in assessments:
        category = assessment.get_bmi_category()
        bmi_stats[category] = bmi_stats.get(category, 0) + 1
    
    # Metas activas por prioridad
    active_goals = NutritionGoal.objects.filter(
        patient__organization=request.user.profile.organization,
        status='active'
    ).values('priority').annotate(count=Count('id'))
    
    context = {
        'total_assessments': total_assessments,
        'total_diet_plans': total_diet_plans,
        'active_plans': active_plans,
        'recent_consultations': recent_consultations,
        'recent_assessments': recent_assessments,
        'upcoming_consultations': upcoming_consultations,
        'bmi_stats': bmi_stats,
        'active_goals': active_goals,
    }
    
    return render(request, 'nutrition/dashboard.html', context)


@login_required
def assessment_list(request):
    """Lista de evaluaciones nutricionales"""
    
    assessments = NutritionalAssessment.objects.filter(
        patient__organization=request.user.profile.organization
    ).order_by('-created_at')
    
    # Aplicar búsqueda si existe
    search_query = request.GET.get('search')
    search_form = PatientSearchForm(request.GET or None)
    
    if search_query:
        assessments = assessments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__identification_number__icontains=search_query)
        )
    elif search_form.is_valid() and search_form.cleaned_data.get('patient_search'):
        search_term = search_form.cleaned_data['patient_search']
        assessments = assessments.filter(
            Q(patient__first_name__icontains=search_term) |
            Q(patient__last_name__icontains=search_term) |
            Q(patient__identification_number__icontains=search_term)
        )
    
    # Paginación
    paginator = Paginator(assessments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'search_query': search_query,
    }
    
    return render(request, 'nutrition/assessment_list.html', context)


@login_required
def assessment_create(request):
    """Crear nueva evaluación nutricional"""
    
    if request.method == 'POST':
        form = NutritionalAssessmentForm(request.POST, user=request.user)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.nutritionist = request.user
            assessment.save()
            messages.success(request, 'Evaluación nutricional creada exitosamente.')
            return redirect('nutrition:assessment_detail', pk=assessment.pk)
    else:
        form = NutritionalAssessmentForm(user=request.user)
    
    return render(request, 'nutrition/assessment_form.html', {'form': form, 'title': 'Nueva Evaluación Nutricional'})


@login_required
def assessment_detail(request, pk):
    """Detalle de evaluación nutricional"""
    
    assessment = get_object_or_404(
        NutritionalAssessment,
        pk=pk,
        patient__organization=request.user.profile.organization
    )
    
    # Obtener planes dietéticos relacionados
    diet_plans = assessment.diet_plans.all().order_by('-created_at')
    
    # Obtener consultas relacionadas
    consultations = assessment.consultations.all().order_by('-consultation_date')
    
    context = {
        'assessment': assessment,
        'diet_plans': diet_plans,
        'consultations': consultations,
    }
    
    return render(request, 'nutrition/assessment_detail.html', context)


@login_required
def assessment_edit(request, pk):
    """Editar evaluación nutricional"""
    
    assessment = get_object_or_404(
        NutritionalAssessment,
        pk=pk,
        patient__organization=request.user.profile.organization
    )
    
    if request.method == 'POST':
        form = NutritionalAssessmentForm(request.POST, instance=assessment, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evaluación nutricional actualizada exitosamente.')
            return redirect('nutrition:assessment_detail', pk=assessment.pk)
    else:
        form = NutritionalAssessmentForm(instance=assessment, user=request.user)
    
    return render(request, 'nutrition/assessment_form.html', {
        'form': form, 
        'title': 'Editar Evaluación Nutricional',
        'assessment': assessment
    })


@login_required
def diet_plan_list(request):
    """Lista de planes dietéticos"""
    
    diet_plans = DietPlan.objects.filter(
        assessment__patient__organization=request.user.profile.organization
    ).order_by('-created_at')
    
    # Aplicar filtros
    search_query = request.GET.get('search')
    if search_query:
        diet_plans = diet_plans.filter(
            Q(assessment__patient__first_name__icontains=search_query) |
            Q(assessment__patient__last_name__icontains=search_query) |
            Q(assessment__patient__identification_number__icontains=search_query) |
            Q(plan_name__icontains=search_query)
        )
    
    plan_type = request.GET.get('plan_type')
    if plan_type:
        diet_plans = diet_plans.filter(plan_type=plan_type)
    
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        diet_plans = diet_plans.filter(is_active=True)
    elif is_active == 'false':
        diet_plans = diet_plans.filter(is_active=False)
    
    # Paginación
    paginator = Paginator(diet_plans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'plan_types': DietPlan.PLAN_TYPE_CHOICES,
        'search_query': search_query,
        'plan_type': plan_type,
        'is_active': is_active,
    }
    
    return render(request, 'nutrition/diet_plan_list.html', context)


@login_required
def diet_plan_create(request):
    """Crear nuevo plan dietético"""
    
    if request.method == 'POST':
        form = DietPlanForm(request.POST, user=request.user)
        if form.is_valid():
            diet_plan = form.save()
            messages.success(request, 'Plan dietético creado exitosamente.')
            return redirect('nutrition:diet_plan_detail', pk=diet_plan.pk)
    else:
        form = DietPlanForm(user=request.user)
    
    return render(request, 'nutrition/diet_plan_form.html', {'form': form, 'title': 'Nuevo Plan Dietético'})


@login_required
def diet_plan_detail(request, pk):
    """Detalle de plan dietético"""
    
    diet_plan = get_object_or_404(
        DietPlan,
        pk=pk,
        assessment__patient__organization=request.user.profile.organization
    )
    
    # Obtener menús organizados por día y comida
    meal_plans = diet_plan.meal_plans.all().order_by('day_number', 'meal_type')
    
    # Organizar menús por día
    meals_by_day = {}
    for meal in meal_plans:
        if meal.day_number not in meals_by_day:
            meals_by_day[meal.day_number] = {}
        meals_by_day[meal.day_number][meal.meal_type] = meal
    
    context = {
        'diet_plan': diet_plan,
        'meals_by_day': meals_by_day,
        'meal_types': MealPlan.MEAL_CHOICES,
    }
    
    return render(request, 'nutrition/diet_plan_detail.html', context)


@login_required
def consultation_list(request):
    """Lista de consultas nutricionales"""
    
    consultations = NutritionConsultation.objects.filter(
        patient__organization=request.user.profile.organization
    ).order_by('-consultation_date')
    
    # Aplicar búsqueda si existe
    search_query = request.GET.get('search')
    search_form = PatientSearchForm(request.GET or None)
    
    if search_query:
        consultations = consultations.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__identification_number__icontains=search_query)
        )
    elif search_form.is_valid() and search_form.cleaned_data.get('patient_search'):
        search_term = search_form.cleaned_data['patient_search']
        consultations = consultations.filter(
            Q(patient__first_name__icontains=search_term) |
            Q(patient__last_name__icontains=search_term) |
            Q(patient__identification_number__icontains=search_term)
        )
    
    # Paginación
    paginator = Paginator(consultations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'search_query': search_query,
    }
    
    return render(request, 'nutrition/consultation_list.html', context)


@login_required
def consultation_create(request):
    """Crear nueva consulta nutricional"""
    
    if request.method == 'POST':
        form = NutritionConsultationForm(request.POST, user=request.user)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.nutritionist = request.user
            consultation.save()
            messages.success(request, 'Consulta nutricional registrada exitosamente.')
            return redirect('nutrition:consultation_detail', pk=consultation.pk)
    else:
        form = NutritionConsultationForm(user=request.user)
    
    return render(request, 'nutrition/consultation_form.html', {'form': form, 'title': 'Nueva Consulta Nutricional'})


@login_required
def consultation_detail(request, pk):
    """Detalle de consulta nutricional"""
    
    consultation = get_object_or_404(
        NutritionConsultation,
        pk=pk,
        patient__organization=request.user.profile.organization
    )
    
    context = {
        'consultation': consultation,
    }
    
    return render(request, 'nutrition/consultation_detail.html', context)


@login_required
def nutrition_goals_list(request):
    """Lista de metas nutricionales"""
    
    goals = NutritionGoal.objects.filter(
        patient__organization=request.user.profile.organization
    ).order_by('-priority', 'target_date')
    
    # Aplicar filtros
    status = request.GET.get('status')
    if status:
        goals = goals.filter(status=status)
    
    goal_type = request.GET.get('goal_type')
    if goal_type:
        goals = goals.filter(goal_type=goal_type)
    
    # Paginación
    paginator = Paginator(goals, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'goal_types': NutritionGoal.GOAL_TYPE_CHOICES,
        'status_choices': NutritionGoal.STATUS_CHOICES,
    }
    
    return render(request, 'nutrition/goals_list.html', context)


@login_required
def nutrition_goal_create(request):
    """Crear nueva meta nutricional"""
    
    if request.method == 'POST':
        form = NutritionGoalForm(request.POST, user=request.user)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.nutritionist = request.user
            goal.save()
            messages.success(request, 'Meta nutricional creada exitosamente.')
            return redirect('nutrition:goals_list')
    else:
        form = NutritionGoalForm(user=request.user)
    
    return render(request, 'nutrition/goal_form.html', {'form': form, 'title': 'Nueva Meta Nutricional'})


@login_required
def meal_plan_create(request, diet_plan_id):
    """Crear nuevo menú para un plan dietético"""
    
    diet_plan = get_object_or_404(
        DietPlan,
        pk=diet_plan_id,
        assessment__patient__organization=request.user.profile.organization
    )
    
    if request.method == 'POST':
        form = MealPlanForm(request.POST, user=request.user)
        if form.is_valid():
            meal_plan = form.save()
            messages.success(request, 'Menú creado exitosamente.')
            return redirect('nutrition:diet_plan_detail', pk=diet_plan.pk)
    else:
        form = MealPlanForm(user=request.user, initial={'diet_plan': diet_plan})
    
    return render(request, 'nutrition/meal_plan_form.html', {
        'form': form, 
        'title': f'Nuevo Menú para {diet_plan.name}',
        'diet_plan': diet_plan
    })


# API Views para AJAX
@login_required
def api_patient_assessments(request, patient_id):
    """API para obtener evaluaciones de un paciente específico"""
    
    try:
        patient = Patient.objects.get(
            pk=patient_id,
            organization=request.user.profile.organization
        )
        
        assessments = NutritionalAssessment.objects.filter(
            patient=patient
        ).order_by('-created_at').values(
            'id', 'created_at', 'weight', 'height', 'bmi', 'objective'
        )
        
        return JsonResponse({
            'success': True,
            'assessments': list(assessments)
        })
    
    except Patient.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Paciente no encontrado'
        })


@login_required
def api_bmi_calculator(request):
    """API para calcular IMC"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            weight = float(data.get('weight', 0))
            height = float(data.get('height', 0))
            
            if weight > 0 and height > 0:
                height_m = height / 100
                bmi = round(weight / (height_m ** 2), 2)
                
                # Determinar categoría
                if bmi < 18.5:
                    category = 'Bajo peso'
                elif 18.5 <= bmi < 25:
                    category = 'Peso normal'
                elif 25 <= bmi < 30:
                    category = 'Sobrepeso'
                elif 30 <= bmi < 35:
                    category = 'Obesidad grado I'
                elif 35 <= bmi < 40:
                    category = 'Obesidad grado II'
                else:
                    category = 'Obesidad grado III'
                
                return JsonResponse({
                    'success': True,
                    'bmi': bmi,
                    'category': category
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Valores inválidos'
                })
        
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Datos inválidos'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_calorie_calculator(request):
    """API para calcular calorías recomendadas"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            weight = float(data.get('weight', 0))
            height = float(data.get('height', 0))
            age = int(data.get('age', 0))
            gender = data.get('gender', 'M')
            activity_level = data.get('activity_level', 'sedentary')
            
            if weight > 0 and height > 0 and age > 0:
                # Calcular BMR usando fórmula de Harris-Benedict
                if gender == 'M':
                    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
                else:
                    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
                
                # Multiplicadores de actividad
                activity_multipliers = {
                    'sedentary': 1.2,
                    'light': 1.375,
                    'moderate': 1.55,
                    'active': 1.725,
                    'very_active': 1.9,
                }
                
                multiplier = activity_multipliers.get(activity_level, 1.2)
                daily_calories = round(bmr * multiplier, 2)
                
                return JsonResponse({
                    'success': True,
                    'bmr': round(bmr, 2),
                    'daily_calories': daily_calories
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Valores inválidos'
                })
        
        except (json.JSONDecodeError, ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': 'Datos inválidos'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

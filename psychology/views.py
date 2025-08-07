from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    PsychologicalEvaluation, PsychologicalTest, TestResult,
    TherapySession, TreatmentPlan, PsychologicalGoal
)
from .forms import (
    PsychologicalEvaluationForm, PsychologicalTestForm, TestResultForm,
    TherapySessionForm, TreatmentPlanForm, PsychologicalGoalForm
)
from patients.models import Patient


@login_required
def psychology_dashboard(request):
    """Dashboard principal del módulo de psicología"""
    # Estadísticas generales
    total_evaluations = PsychologicalEvaluation.objects.filter(psychologist=request.user).count()
    completed_evaluations = PsychologicalEvaluation.objects.filter(
        psychologist=request.user, is_completed=True
    ).count()
    active_treatments = TreatmentPlan.objects.filter(
        created_by=request.user, is_active=True
    ).count()
    total_sessions = TherapySession.objects.filter(psychologist=request.user).count()
    
    # Evaluaciones recientes
    recent_evaluations = PsychologicalEvaluation.objects.filter(
        psychologist=request.user
    ).order_by('-evaluation_date')[:5]
    
    # Próximas sesiones
    upcoming_sessions = TherapySession.objects.filter(
        psychologist=request.user,
        session_date__gte=timezone.now(),
        status__in=['scheduled', 'rescheduled']
    ).order_by('session_date')[:5]
    
    # Objetivos próximos a vencer
    upcoming_goals = PsychologicalGoal.objects.filter(
        treatment_plan__created_by=request.user,
        status='active',
        target_date__lte=timezone.now() + timedelta(days=7)
    ).order_by('target_date')[:5]
    
    # Gráfico de evaluaciones por tipo
    evaluations_by_type = PsychologicalEvaluation.objects.filter(
        psychologist=request.user
    ).values('evaluation_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_evaluations': total_evaluations,
        'completed_evaluations': completed_evaluations,
        'active_treatments': active_treatments,
        'total_sessions': total_sessions,
        'recent_evaluations': recent_evaluations,
        'upcoming_sessions': upcoming_sessions,
        'upcoming_goals': upcoming_goals,
        'evaluations_by_type': evaluations_by_type,
        'completion_rate': round((completed_evaluations / total_evaluations * 100) if total_evaluations > 0 else 0, 1),
    }
    
    return render(request, 'psychology/dashboard.html', context)


# === EVALUACIONES PSICOLÓGICAS ===

@login_required
def evaluation_list(request):
    """Lista de evaluaciones psicológicas"""
    evaluations = PsychologicalEvaluation.objects.filter(
        psychologist=request.user
    ).select_related('patient').order_by('-evaluation_date')
    
    # Filtros
    search = request.GET.get('search')
    evaluation_type = request.GET.get('evaluation_type')
    completed = request.GET.get('completed')
    
    if search:
        evaluations = evaluations.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(patient__identification_number__icontains=search) |
            Q(chief_complaint__icontains=search)
        )
    
    if evaluation_type:
        evaluations = evaluations.filter(evaluation_type=evaluation_type)
    
    if completed == 'true':
        evaluations = evaluations.filter(is_completed=True)
    elif completed == 'false':
        evaluations = evaluations.filter(is_completed=False)
    
    # Paginación
    paginator = Paginator(evaluations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'evaluation_types': PsychologicalEvaluation.EVALUATION_TYPE_CHOICES,
        'title': 'Evaluaciones Psicológicas',
        'search_query': search,
        'evaluation_type': evaluation_type,
        'completed': completed
    }
    
    return render(request, 'psychology/evaluation_list.html', context)


@login_required
def evaluation_create(request):
    """Crear nueva evaluación psicológica"""
    if request.method == 'POST':
        form = PsychologicalEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.psychologist = request.user
            evaluation.save()
            messages.success(request, 'Evaluación psicológica creada exitosamente.')
            return redirect('psychology:evaluation_detail', pk=evaluation.pk)
    else:
        form = PsychologicalEvaluationForm()
    
    context = {
        'form': form,
        'title': 'Nueva Evaluación Psicológica'
    }
    
    return render(request, 'psychology/evaluation_form.html', context)


@login_required
def evaluation_detail(request, pk):
    """Detalle de evaluación psicológica"""
    evaluation = get_object_or_404(
        PsychologicalEvaluation, 
        pk=pk, 
        psychologist=request.user
    )
    
    # Resultados de tests relacionados
    test_results = TestResult.objects.filter(evaluation=evaluation).select_related('test')
    
    # Plan de tratamiento si existe
    treatment_plan = getattr(evaluation, 'psychological_treatment_plan', None)
    
    # Sesiones de terapia
    therapy_sessions = TherapySession.objects.filter(
        evaluation=evaluation
    ).order_by('-session_date')[:10]
    
    context = {
        'evaluation': evaluation,
        'test_results': test_results,
        'treatment_plan': treatment_plan,
        'therapy_sessions': therapy_sessions,
        'title': f'Evaluación de {evaluation.patient.get_full_name()}'
    }
    
    return render(request, 'psychology/evaluation_detail.html', context)


@login_required
def evaluation_edit(request, pk):
    """Editar evaluación psicológica"""
    evaluation = get_object_or_404(
        PsychologicalEvaluation, 
        pk=pk, 
        psychologist=request.user
    )
    
    if request.method == 'POST':
        form = PsychologicalEvaluationForm(request.POST, instance=evaluation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evaluación actualizada exitosamente.')
            return redirect('psychology:evaluation_detail', pk=evaluation.pk)
    else:
        form = PsychologicalEvaluationForm(instance=evaluation)
    
    context = {
        'form': form,
        'evaluation': evaluation,
        'title': 'Editar Evaluación'
    }
    
    return render(request, 'psychology/evaluation_form.html', context)


# === TESTS PSICOLÓGICOS ===

@login_required
def test_list(request):
    """Lista de tests psicológicos"""
    tests = PsychologicalTest.objects.filter(is_active=True).order_by('category', 'name')
    
    # Filtros
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if category:
        tests = tests.filter(category=category)
    
    if search:
        tests = tests.filter(
            Q(name__icontains=search) |
            Q(abbreviation__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(tests, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'test_categories': PsychologicalTest.TEST_CATEGORY_CHOICES,
        'title': 'Catálogo de Tests Psicológicos'
    }
    
    return render(request, 'psychology/test_list.html', context)


@login_required
def test_create(request):
    """Crear nuevo test psicológico"""
    if request.method == 'POST':
        form = PsychologicalTestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test psicológico creado exitosamente.')
            return redirect('psychology:test_list')
    else:
        form = PsychologicalTestForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Test Psicológico'
    }
    
    return render(request, 'psychology/test_form.html', context)


# === SESIONES DE TERAPIA ===

@login_required
def session_list(request):
    """Lista de sesiones de terapia"""
    sessions = TherapySession.objects.filter(
        psychologist=request.user
    ).select_related('patient', 'evaluation').order_by('-session_date')
    
    # Filtros
    search_query = request.GET.get('search')
    patient_id = request.GET.get('patient')
    session_type = request.GET.get('session_type')
    status = request.GET.get('status')
    
    if search_query:
        sessions = sessions.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(patient__identification_number__icontains=search_query) |
            Q(session_notes__icontains=search_query)
        )
    
    if patient_id:
        sessions = sessions.filter(patient_id=patient_id)
    
    if session_type:
        sessions = sessions.filter(session_type=session_type)
    
    if status:
        sessions = sessions.filter(status=status)
    
    # Paginación
    paginator = Paginator(sessions, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'session_types': TherapySession.SESSION_TYPE_CHOICES,
        'session_statuses': TherapySession.SESSION_STATUS_CHOICES,
        'title': 'Sesiones de Terapia',
        'search_query': search_query,
        'patient_id': patient_id,
        'session_type': session_type,
        'status': status
    }
    
    return render(request, 'psychology/session_list.html', context)


@login_required
def session_create(request):
    """Crear nueva sesión de terapia"""
    if request.method == 'POST':
        form = TherapySessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.psychologist = request.user
            session.save()
            messages.success(request, 'Sesión de terapia creada exitosamente.')
            return redirect('psychology:session_detail', pk=session.pk)
    else:
        form = TherapySessionForm()
    
    context = {
        'form': form,
        'title': 'Nueva Sesión de Terapia'
    }
    
    return render(request, 'psychology/session_form.html', context)


@login_required
def session_detail(request, pk):
    """Detalle de sesión de terapia"""
    session = get_object_or_404(
        TherapySession,
        pk=pk,
        psychologist=request.user
    )
    
    # Sesiones anteriores del mismo paciente
    previous_sessions = TherapySession.objects.filter(
        patient=session.patient,
        psychologist=request.user,
        session_date__lt=session.session_date
    ).order_by('-session_date')[:5]
    
    context = {
        'session': session,
        'previous_sessions': previous_sessions,
        'title': f'Sesión {session.session_number} - {session.patient.get_full_name()}'
    }
    
    return render(request, 'psychology/session_detail.html', context)


# === PLANES DE TRATAMIENTO ===

@login_required
def treatment_plan_list(request):
    """Lista de planes de tratamiento"""
    plans = TreatmentPlan.objects.filter(
        created_by=request.user
    ).select_related('evaluation__patient').order_by('-created_at')
    
    # Filtros
    is_active = request.GET.get('is_active')
    approach = request.GET.get('approach')
    
    if is_active == 'true':
        plans = plans.filter(is_active=True)
    elif is_active == 'false':
        plans = plans.filter(is_active=False)
    
    if approach:
        plans = plans.filter(treatment_approach=approach)
    
    # Paginación
    paginator = Paginator(plans, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'treatment_approaches': TreatmentPlan.TREATMENT_APPROACH_CHOICES,
        'title': 'Planes de Tratamiento'
    }
    
    return render(request, 'psychology/treatment_plan_list.html', context)


@login_required
def treatment_plan_create(request):
    """Crear nuevo plan de tratamiento"""
    if request.method == 'POST':
        form = TreatmentPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()
            messages.success(request, 'Plan de tratamiento creado exitosamente.')
            return redirect('psychology:treatment_plan_detail', pk=plan.pk)
    else:
        form = TreatmentPlanForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Plan de Tratamiento'
    }
    
    return render(request, 'psychology/treatment_plan_form.html', context)


@login_required
def treatment_plan_detail(request, pk):
    """Detalle de plan de tratamiento"""
    plan = get_object_or_404(
        TreatmentPlan,
        pk=pk,
        created_by=request.user
    )
    
    # Objetivos del plan
    goals = PsychologicalGoal.objects.filter(treatment_plan=plan).order_by('-priority', 'target_date')
    
    # Sesiones relacionadas
    sessions = TherapySession.objects.filter(
        evaluation=plan.evaluation,
        psychologist=request.user
    ).order_by('-session_date')[:10]
    
    context = {
        'plan': plan,
        'goals': goals,
        'sessions': sessions,
        'title': f'Plan de Tratamiento - {plan.evaluation.patient.get_full_name()}'
    }
    
    return render(request, 'psychology/treatment_plan_detail.html', context)


# === OBJETIVOS PSICOLÓGICOS ===

@login_required
def goal_list(request):
    """Lista de objetivos psicológicos"""
    goals = PsychologicalGoal.objects.filter(
        treatment_plan__created_by=request.user
    ).select_related('treatment_plan__evaluation__patient').order_by('-priority', 'target_date')
    
    # Filtros
    status = request.GET.get('status')
    goal_type = request.GET.get('goal_type')
    priority = request.GET.get('priority')
    
    if status:
        goals = goals.filter(status=status)
    
    if goal_type:
        goals = goals.filter(goal_type=goal_type)
    
    if priority:
        goals = goals.filter(priority=priority)
    
    # Paginación
    paginator = Paginator(goals, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'goal_types': PsychologicalGoal.GOAL_TYPE_CHOICES,
        'goal_statuses': PsychologicalGoal.STATUS_CHOICES,
        'priorities': [(1, 'Baja'), (2, 'Media'), (3, 'Alta'), (4, 'Crítica')],
        'title': 'Objetivos Psicológicos'
    }
    
    return render(request, 'psychology/goal_list.html', context)


@login_required
def goal_create(request):
    """Crear nuevo objetivo psicológico"""
    if request.method == 'POST':
        form = PsychologicalGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.created_by = request.user
            goal.save()
            messages.success(request, 'Objetivo psicológico creado exitosamente.')
            return redirect('psychology:goal_detail', pk=goal.pk)
    else:
        form = PsychologicalGoalForm()
    
    context = {
        'form': form,
        'title': 'Nuevo Objetivo Psicológico'
    }
    
    return render(request, 'psychology/goal_form.html', context)


@login_required
def goal_detail(request, pk):
    """Detalle de objetivo psicológico"""
    goal = get_object_or_404(
        PsychologicalGoal,
        pk=pk,
        treatment_plan__created_by=request.user
    )
    
    context = {
        'goal': goal,
        'title': f'Objetivo: {goal.title}'
    }
    
    return render(request, 'psychology/goal_detail.html', context)


# === APIs Y UTILIDADES ===

@login_required
def patient_evaluations_api(request, patient_id):
    """API para obtener evaluaciones de un paciente"""
    evaluations = PsychologicalEvaluation.objects.filter(
        patient_id=patient_id,
        psychologist=request.user
    ).values('id', 'evaluation_type', 'evaluation_date', 'is_completed')
    
    return JsonResponse({
        'evaluations': list(evaluations)
    })


@login_required
def evaluation_summary_api(request, evaluation_id):
    """API para obtener resumen de una evaluación"""
    evaluation = get_object_or_404(
        PsychologicalEvaluation,
        pk=evaluation_id,
        psychologist=request.user
    )
    
    data = {
        'patient': evaluation.patient.get_full_name(),
        'evaluation_type': evaluation.get_evaluation_type_display(),
        'evaluation_date': evaluation.evaluation_date.strftime('%d/%m/%Y %H:%M'),
        'chief_complaint': evaluation.chief_complaint,
        'provisional_diagnosis': evaluation.provisional_diagnosis,
        'is_completed': evaluation.is_completed,
    }
    
    return JsonResponse(data)

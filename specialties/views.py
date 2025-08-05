from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Count, Q, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    Specialty, Doctor, SpecialtyProcedure, SpecialtyConsultation,
    SpecialtyTreatment, SpecialtyReferral
)
from .forms import (
    SpecialtyForm, DoctorForm, SpecialtyProcedureForm, SpecialtyConsultationForm,
    SpecialtyTreatmentForm, SpecialtyReferralForm, SpecialtyFilterForm
)
from patients.models import Patient

@login_required  
def index(request):
    """Dashboard principal de especialidades"""
    from datetime import datetime, timedelta
    from django.db.models import Q
    
    # Fechas para filtros temporales
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Estadísticas generales
    total_consultations = SpecialtyConsultation.objects.count()
    consultations_this_week = SpecialtyConsultation.objects.filter(date__gte=week_ago).count()
    consultations_this_month = SpecialtyConsultation.objects.filter(date__gte=month_ago).count()
    
    # Calcular porcentajes de cambio
    prev_week_consultations = SpecialtyConsultation.objects.filter(
        date__gte=week_ago - timedelta(days=7), 
        date__lt=week_ago
    ).count()
    week_change = ((consultations_this_week - prev_week_consultations) / max(prev_week_consultations, 1)) * 100
    
    stats = {
        'total_specialties': Specialty.objects.filter(is_active=True).count(),
        'total_doctors': Doctor.objects.filter(is_active=True).count(),
        'total_consultations': total_consultations,
        'consultations_this_week': consultations_this_week,
        'consultations_this_month': consultations_this_month,
        'week_change': round(week_change, 1),
        'pending_referrals': SpecialtyReferral.objects.filter(status='pending').count(),
        'active_treatments': SpecialtyTreatment.objects.filter(status='in_progress').count(),
        'completed_consultations': SpecialtyConsultation.objects.filter(is_completed=True).count(),
        'urgent_referrals': SpecialtyReferral.objects.filter(
            status='pending', urgency__in=['urgent', 'emergency']
        ).count(),
        'consultations_today': SpecialtyConsultation.objects.filter(date__date=today).count(),
        'upcoming_consultations': SpecialtyConsultation.objects.filter(
            date__gt=timezone.now(),
            date__date__lte=today + timedelta(days=7)
        ).count(),
    }
    
    # Especialidades con estadísticas detalladas
    specialties = Specialty.objects.filter(is_active=True).annotate(
        doctors_count=Count('doctor', distinct=True),
        consultations_count=Count('specialtyconsultation', distinct=True),
        active_treatments_count=Count('specialtytreatment', filter=Q(specialtytreatment__status='in_progress'), distinct=True),
        this_month_consultations=Count('specialtyconsultation', filter=Q(specialtyconsultation__date__gte=month_ago), distinct=True)
    ).order_by('-consultations_count')
    
    # Consultas recientes con más detalles
    recent_consultations = SpecialtyConsultation.objects.select_related(
        'patient', 'doctor__user', 'specialty'
    ).order_by('-date')[:10]
    
    # Referencias pendientes ordenadas por urgencia
    pending_referrals = SpecialtyReferral.objects.filter(
        status='pending'
    ).select_related(
        'patient', 'from_specialty', 'to_specialty', 'referring_doctor__user'
    ).order_by('-urgency', '-referral_date')[:5]
    
    # Top especialidades por consultas
    top_specialties = list(specialties.filter(consultations_count__gt=0)[:5])
    
    # Doctores más activos
    active_doctors = Doctor.objects.filter(is_active=True).annotate(
        consultations_count=Count('specialtyconsultation', distinct=True),
        this_month_consultations=Count('specialtyconsultation', filter=Q(specialtyconsultation__date__gte=month_ago), distinct=True)
    ).filter(consultations_count__gt=0).select_related('user').order_by('-this_month_consultations')[:5]
    
    # Distribución de consultas por tipo
    consultation_types = SpecialtyConsultation.objects.filter(
        date__gte=month_ago
    ).values('consultation_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Tratamientos por estado
    treatment_status_distribution = SpecialtyTreatment.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'title': 'Dashboard de Especialidades Médicas',
        'stats': stats,
        'specialties': specialties,
        'recent_consultations': recent_consultations,
        'pending_referrals': pending_referrals,
        'top_specialties': top_specialties,
        'active_doctors': active_doctors,
        'consultation_types': consultation_types,
        'treatment_status_distribution': treatment_status_distribution,
        'today': today,
    }
    
    return render(request, 'specialties/dashboard.html', context)

@login_required
def specialty_list(request):
    """Lista de todas las especialidades"""
    specialties_list = Specialty.objects.annotate(
        doctors_count=Count('doctor', distinct=True),
        consultations_count=Count('specialtyconsultation', distinct=True),
        procedures_count=Count('procedures', distinct=True)
    ).order_by('name')
    
    # Filtros
    active_filter = request.GET.get('active')
    if active_filter == 'true':
        specialties_list = specialties_list.filter(is_active=True)
    elif active_filter == 'false':
        specialties_list = specialties_list.filter(is_active=False)
    
    # Paginación
    paginator = Paginator(specialties_list, 20)
    page_number = request.GET.get('page')
    specialties = paginator.get_page(page_number)
    
    context = {
        'title': 'Especialidades',
        'specialties': specialties,
        'active_filter': active_filter,
    }
    
    return render(request, 'specialties/specialty_list.html', context)

@login_required
def specialty_detail(request, pk):
    """Detalle de una especialidad específica"""
    specialty = get_object_or_404(Specialty, pk=pk)
    
    # Doctores de esta especialidad
    doctors = Doctor.objects.filter(
        specialties=specialty, is_active=True
    ).select_related('user')
    
    # Procedimientos de esta especialidad
    procedures = SpecialtyProcedure.objects.filter(
        specialty=specialty, is_active=True
    ).order_by('name')
    
    # Consultas recientes
    recent_consultations = SpecialtyConsultation.objects.filter(
        specialty=specialty
    ).select_related('patient', 'doctor').order_by('-date')[:10]
    
    # Estadísticas
    stats = {
        'total_consultations': specialty.specialtyconsultation_set.count(),
        'total_treatments': specialty.specialtytreatment_set.count(),
        'completed_consultations': specialty.specialtyconsultation_set.filter(is_completed=True).count(),
        'active_treatments': specialty.specialtytreatment_set.filter(status='in_progress').count(),
    }
    
    context = {
        'title': f'Especialidad: {specialty.name}',
        'specialty': specialty,
        'doctors': doctors,
        'procedures': procedures,
        'recent_consultations': recent_consultations,
        'stats': stats,
    }
    
    return render(request, 'specialties/specialty_detail.html', context)

@login_required
def doctor_list(request):
    """Lista de doctores por especialidad"""
    doctors_list = Doctor.objects.filter(is_active=True).select_related('user').prefetch_related('specialties')
    
    # Filtro por especialidad
    specialty_filter = request.GET.get('specialty')
    if specialty_filter:
        doctors_list = doctors_list.filter(specialties__id=specialty_filter)
    
    # Filtro por disponibilidad
    availability_filter = request.GET.get('availability')
    if availability_filter == 'accepting':
        doctors_list = doctors_list.filter(accepts_new_patients=True)
    
    # Paginación
    paginator = Paginator(doctors_list, 20)
    page_number = request.GET.get('page')
    doctors = paginator.get_page(page_number)
    
    # Especialidades para el filtro
    specialties = Specialty.objects.filter(is_active=True).order_by('name')
    
    context = {
        'title': 'Doctores Especialistas',
        'doctors': doctors,
        'specialties': specialties,
        'specialty_filter': specialty_filter,
        'availability_filter': availability_filter,
    }
    
    return render(request, 'specialties/doctor_list.html', context)

@login_required
def doctor_detail(request, pk):
    """Detalle de un doctor específico"""
    doctor = get_object_or_404(Doctor, pk=pk)
    
    # Consultas del doctor
    consultations = SpecialtyConsultation.objects.filter(
        doctor=doctor
    ).select_related('patient', 'specialty').order_by('-date')[:20]
    
    # Tratamientos activos
    active_treatments = SpecialtyTreatment.objects.filter(
        doctor=doctor, status='in_progress'
    ).select_related('patient', 'specialty')
    
    # Estadísticas
    stats = {
        'total_consultations': doctor.specialtyconsultation_set.count(),
        'completed_consultations': doctor.specialtyconsultation_set.filter(is_completed=True).count(),
        'total_treatments': doctor.specialtytreatment_set.count(),
        'active_treatments': doctor.specialtytreatment_set.filter(status='in_progress').count(),
    }
    
    context = {
        'title': f'Dr. {doctor.user.get_full_name()}',
        'doctor': doctor,
        'consultations': consultations,
        'active_treatments': active_treatments,
        'stats': stats,
    }
    
    return render(request, 'specialties/doctor_detail.html', context)

@login_required
def consultation_list(request):
    """Lista de consultas de especialidades"""
    consultations_list = SpecialtyConsultation.objects.select_related(
        'patient', 'doctor', 'specialty'
    ).order_by('-date')
    
    # Filtros básicos
    specialty_filter = request.GET.get('specialty')
    status_filter = request.GET.get('status')
    doctor_filter = request.GET.get('doctor')
    
    if specialty_filter:
        consultations_list = consultations_list.filter(specialty__id=specialty_filter)
    if status_filter == 'completed':
        consultations_list = consultations_list.filter(is_completed=True)
    elif status_filter == 'pending':
        consultations_list = consultations_list.filter(is_completed=False)
    if doctor_filter:
        consultations_list = consultations_list.filter(doctor__id=doctor_filter)
    
    # Paginación
    paginator = Paginator(consultations_list, 20)
    page_number = request.GET.get('page')
    consultations = paginator.get_page(page_number)
    
    # Para filtros
    specialties = Specialty.objects.filter(is_active=True).order_by('name')
    doctors = Doctor.objects.filter(is_active=True).select_related('user').order_by('user__first_name')
    
    context = {
        'title': 'Consultas de Especialidades',
        'consultations': consultations,
        'specialties': specialties,
        'doctors': doctors,
        'specialty_filter': specialty_filter,
        'status_filter': status_filter,
        'doctor_filter': doctor_filter,
    }
    
    return render(request, 'specialties/consultation_list.html', context)

@login_required
def consultation_detail(request, pk):
    """Detalle de una consulta específica"""
    consultation = get_object_or_404(SpecialtyConsultation, pk=pk)
    
    # Tratamientos relacionados
    treatments = SpecialtyTreatment.objects.filter(
        consultation=consultation
    ).order_by('-start_date')
    
    context = {
        'title': f'Consulta {consultation.specialty.name} - {consultation.patient.get_full_name()}',
        'consultation': consultation,
        'treatments': treatments,
    }
    
    return render(request, 'specialties/consultation_detail.html', context)

@login_required
def create_consultation(request):
    """Crear nueva consulta de especialidad"""
    if request.method == 'POST':
        form = SpecialtyConsultationForm(request.POST, user=request.user)
        if form.is_valid():
            consultation = form.save()
            messages.success(request, 'Consulta de especialidad creada exitosamente.')
            return redirect('specialties:consultation_detail', pk=consultation.pk)
    else:
        form = SpecialtyConsultationForm(user=request.user)
    
    context = {
        'title': 'Nueva Consulta de Especialidad',
        'form': form,
    }
    
    return render(request, 'specialties/create_consultation.html', context)

@login_required
def create_referral(request):
    """Crear nueva referencia"""
    if request.method == 'POST':
        form = SpecialtyReferralForm(request.POST, user=request.user)
        if form.is_valid():
            referral = form.save()
            messages.success(request, 'Referencia creada exitosamente.')
            return redirect('specialties:referral_detail', pk=referral.pk)
    else:
        form = SpecialtyReferralForm(user=request.user)
    
    context = {
        'title': 'Nueva Referencia',
        'form': form,
    }
    
    return render(request, 'specialties/create_referral.html', context)

@login_required
def treatment_list(request):
    """Lista de tratamientos de especialidades"""
    treatments_list = SpecialtyTreatment.objects.select_related(
        'patient', 'doctor', 'specialty'
    ).order_by('-start_date')
    
    # Filtros
    specialty_filter = request.GET.get('specialty')
    status_filter = request.GET.get('status')
    
    if specialty_filter:
        treatments_list = treatments_list.filter(specialty__id=specialty_filter)
    if status_filter:
        treatments_list = treatments_list.filter(status=status_filter)
    
    # Paginación
    paginator = Paginator(treatments_list, 20)
    page_number = request.GET.get('page')
    treatments = paginator.get_page(page_number)
    
    # Para filtros
    specialties = Specialty.objects.filter(is_active=True).order_by('name')
    
    context = {
        'title': 'Tratamientos de Especialidades',
        'treatments': treatments,
        'specialties': specialties,
        'specialty_filter': specialty_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'specialties/treatment_list.html', context)

@login_required
def treatment_detail(request, pk):
    """Detalle de un tratamiento específico"""
    treatment = get_object_or_404(SpecialtyTreatment, pk=pk)
    
    context = {
        'title': f'Tratamiento: {treatment.name}',
        'treatment': treatment,
    }
    
    return render(request, 'specialties/treatment_detail.html', context)

@login_required
def referral_list(request):
    """Lista de referencias entre especialidades"""
    referrals_list = SpecialtyReferral.objects.select_related(
        'patient', 'referring_doctor', 'from_specialty', 'to_specialty'
    ).order_by('-referral_date')
    
    # Filtros  
    status_filter = request.GET.get('status')
    urgency_filter = request.GET.get('urgency')
    
    if status_filter:
        referrals_list = referrals_list.filter(status=status_filter)
    if urgency_filter:
        referrals_list = referrals_list.filter(urgency=urgency_filter)
    
    # Paginación
    paginator = Paginator(referrals_list, 20)
    page_number = request.GET.get('page')
    referrals = paginator.get_page(page_number)
    
    context = {
        'title': 'Referencias entre Especialidades',
        'referrals': referrals,
        'status_filter': status_filter,
        'urgency_filter': urgency_filter,
    }
    
    return render(request, 'specialties/referral_list.html', context)

@login_required
def referral_detail(request, pk):
    """Detalle de una referencia específica"""
    referral = get_object_or_404(SpecialtyReferral, pk=pk)
    
    context = {
        'title': f'Referencia: {referral.from_specialty.name} → {referral.to_specialty.name}',
        'referral': referral,
    }
    
    return render(request, 'specialties/referral_detail.html', context)

@login_required  
def procedures_list(request):
    """Lista de procedimientos por especialidad"""
    procedures_list = SpecialtyProcedure.objects.select_related('specialty').filter(is_active=True)
    
    # Filtro por especialidad
    specialty_filter = request.GET.get('specialty')
    if specialty_filter:
        procedures_list = procedures_list.filter(specialty__id=specialty_filter)
    
    # Paginación
    paginator = Paginator(procedures_list, 20)
    page_number = request.GET.get('page')
    procedures = paginator.get_page(page_number)
    
    # Para filtros
    specialties = Specialty.objects.filter(is_active=True).order_by('name')
    
    context = {
        'title': 'Procedimientos de Especialidades',
        'procedures': procedures,
        'specialties': specialties,
        'specialty_filter': specialty_filter,
    }
    
    return render(request, 'specialties/procedures_list.html', context)

# Vistas específicas por especialidad (redirigen al detalle correspondiente)
@login_required
def nutrition(request):
    """Vista específica para Nutrición"""
    try:
        specialty = Specialty.objects.get(code='NUTR')
        return redirect('specialties:specialty_detail', pk=specialty.pk)
    except Specialty.DoesNotExist:
        messages.error(request, 'La especialidad de Nutrición no está configurada.')
        return redirect('specialties:index')

@login_required
def psychology(request):
    """Vista específica para Psicología"""
    try:
        specialty = Specialty.objects.get(code='PSYC')
        return redirect('specialties:specialty_detail', pk=specialty.pk)
    except Specialty.DoesNotExist:
        messages.error(request, 'La especialidad de Psicología no está configurada.')
        return redirect('specialties:index')

@login_required
def pediatrics(request):
    """Vista específica para Pediatría"""
    context = {
        'title': 'Pediatría - Atención Infantil',
        'specialty_name': 'Pediatría',
        'specialty_code': 'PEDI',
    }
    return render(request, 'specialties/pediatrics.html', context)

@login_required
def ophthalmology(request):
    """Vista específica para Oftalmología"""
    context = {
        'title': 'Oftalmología - Cuidado Ocular',
        'specialty_name': 'Oftalmología', 
        'specialty_code': 'OPHT',
    }
    return render(request, 'specialties/oftalmologia.html', context)

@login_required
def dentistry(request):
    """Vista específica para Odontología"""
    context = {
        'title': 'Odontología - Salud Bucal',
        'specialty_name': 'Odontología',
        'specialty_code': 'DENT',
    }
    return render(request, 'specialties/odontologia.html', context)

@login_required
def traumatology(request):
    """Vista específica para Traumatología"""
    context = {
        'title': 'Traumatología - Medicina Ortopédica',
        'specialty_name': 'Traumatología',
        'specialty_code': 'TRAU',
    }
    return render(request, 'specialties/traumatologia.html', context)

@login_required
def dermatology(request):
    """Vista específica para Dermatología"""
    context = {
        'title': 'Dermatología - Cuidado de la Piel',
        'specialty_name': 'Dermatología',
        'specialty_code': 'DERM',
    }
    return render(request, 'specialties/dermatologia.html', context)

@login_required
def gynecology(request):
    """Vista específica para Ginecología"""
    context = {
        'title': 'Ginecología - Salud Femenina',
        'specialty_name': 'Ginecología',
        'specialty_code': 'GINE',
    }
    return render(request, 'specialties/ginecologia.html', context)

@login_required
def cardiology(request):
    """Vista específica para Cardiología"""
    context = {
        'title': 'Cardiología - Salud Cardiovascular',
        'specialty_name': 'Cardiología',
        'specialty_code': 'CARD',
    }
    return render(request, 'specialties/cardiologia.html', context)

# ==================== PEDIATRÍA SUBMENU ====================
@login_required
def pediatric_consultations(request):
    """Consultas Pediátricas"""
    context = {
        'title': 'Consultas Pediátricas',
        'specialty_name': 'Pediatría',
        'page_title': 'Consultas Pediátricas',
        'description': 'Gestión de consultas médicas especializadas en pediatría'
    }
    return render(request, 'specialties/pediatrics/consultations.html', context)

@login_required
def growth_charts(request):
    """Tablas de Crecimiento"""
    context = {
        'title': 'Tablas de Crecimiento',
        'specialty_name': 'Pediatría',
        'page_title': 'Tablas de Crecimiento',
        'description': 'Seguimiento del crecimiento y desarrollo infantil'
    }
    return render(request, 'specialties/pediatrics/growth_charts.html', context)

@login_required
def vaccine_control(request):
    """Control de Vacunas"""
    context = {
        'title': 'Control de Vacunas',
        'specialty_name': 'Pediatría',
        'page_title': 'Control de Vacunas',
        'description': 'Gestión del esquema de vacunación infantil'
    }
    return render(request, 'specialties/pediatrics/vaccines.html', context)

@login_required
def child_development(request):
    """Desarrollo Infantil"""
    context = {
        'title': 'Desarrollo Infantil',
        'specialty_name': 'Pediatría',
        'page_title': 'Desarrollo Infantil',
        'description': 'Evaluación del desarrollo psicomotor y cognitivo'
    }
    return render(request, 'specialties/pediatrics/development.html', context)

# ==================== CARDIOLOGÍA SUBMENU ====================
@login_required
def ecg_management(request):
    """Electrocardiogramas"""
    context = {
        'title': 'Electrocardiogramas',
        'specialty_name': 'Cardiología',
        'page_title': 'Electrocardiogramas',
        'description': 'Gestión de estudios electrocardiográficos'
    }
    return render(request, 'specialties/cardiology/ecg.html', context)

@login_required
def echocardiogram(request):
    """Ecocardiogramas"""
    context = {
        'title': 'Ecocardiogramas',
        'specialty_name': 'Cardiología',
        'page_title': 'Ecocardiogramas',
        'description': 'Estudios de ecocardiografía'
    }
    return render(request, 'specialties/cardiology/echo.html', context)

@login_required
def stress_test(request):
    """Pruebas de Esfuerzo"""
    context = {
        'title': 'Pruebas de Esfuerzo',
        'specialty_name': 'Cardiología',
        'page_title': 'Pruebas de Esfuerzo',
        'description': 'Evaluación cardiovascular mediante pruebas de esfuerzo'
    }
    return render(request, 'specialties/cardiology/stress_test.html', context)

@login_required
def cardiac_rehabilitation(request):
    """Rehabilitación Cardíaca"""
    context = {
        'title': 'Rehabilitación Cardíaca',
        'specialty_name': 'Cardiología',
        'page_title': 'Rehabilitación Cardíaca',
        'description': 'Programas de rehabilitación cardiovascular'
    }
    return render(request, 'specialties/cardiology/rehabilitation.html', context)

# ==================== OFTALMOLOGÍA SUBMENU ====================
@login_required
def eye_exams(request):
    """Exámenes Oculares"""
    context = {
        'title': 'Exámenes Oculares',
        'specialty_name': 'Oftalmología',
        'page_title': 'Exámenes Oculares',
        'description': 'Evaluaciones oftalmológicas completas'
    }
    return render(request, 'specialties/ophthalmology/eye_exams.html', context)

@login_required
def vision_tests(request):
    """Pruebas de Visión"""
    context = {
        'title': 'Pruebas de Visión',
        'specialty_name': 'Oftalmología',
        'page_title': 'Pruebas de Visión',
        'description': 'Evaluaciones de agudeza visual y refracción'
    }
    return render(request, 'specialties/ophthalmology/vision_tests.html', context)

@login_required
def optical_prescriptions(request):
    """Recetas Ópticas"""
    context = {
        'title': 'Recetas Ópticas',
        'specialty_name': 'Oftalmología',
        'page_title': 'Recetas Ópticas',
        'description': 'Gestión de prescripciones ópticas'
    }
    return render(request, 'specialties/ophthalmology/prescriptions.html', context)

@login_required
def eye_surgeries(request):
    """Cirugías Oculares"""
    context = {
        'title': 'Cirugías Oculares',
        'specialty_name': 'Oftalmología',
        'page_title': 'Cirugías Oculares',
        'description': 'Gestión de procedimientos quirúrgicos oftalmológicos'
    }
    return render(request, 'specialties/ophthalmology/surgeries.html', context)

# ==================== ODONTOLOGÍA SUBMENU ====================
@login_required
def dental_exams(request):
    """Exámenes Dentales"""
    context = {
        'title': 'Exámenes Dentales',
        'specialty_name': 'Odontología',
        'page_title': 'Exámenes Dentales',
        'description': 'Evaluaciones odontológicas y diagnósticos'
    }
    return render(request, 'specialties/dentistry/dental_exams.html', context)

@login_required
def dental_treatments(request):
    """Tratamientos Dentales"""
    context = {
        'title': 'Tratamientos Dentales',
        'specialty_name': 'Odontología',
        'page_title': 'Tratamientos Dentales',
        'description': 'Gestión de tratamientos odontológicos'
    }
    return render(request, 'specialties/dentistry/treatments.html', context)

@login_required
def orthodontics(request):
    """Ortodoncia"""
    context = {
        'title': 'Ortodoncia',
        'specialty_name': 'Odontología',
        'page_title': 'Ortodoncia',
        'description': 'Tratamientos de ortodoncia y alineación dental'
    }
    return render(request, 'specialties/dentistry/orthodontics.html', context)

@login_required
def oral_surgery(request):
    """Cirugía Oral"""
    context = {
        'title': 'Cirugía Oral',
        'specialty_name': 'Odontología',
        'page_title': 'Cirugía Oral',
        'description': 'Procedimientos de cirugía oral y maxilofacial'
    }
    return render(request, 'specialties/dentistry/oral_surgery.html', context)

# ==================== DERMATOLOGÍA SUBMENU ====================
@login_required
def skin_exams(request):
    """Exámenes de Piel"""
    context = {
        'title': 'Exámenes de Piel',
        'specialty_name': 'Dermatología',
        'page_title': 'Exámenes de Piel',
        'description': 'Evaluaciones dermatológicas y diagnósticos'
    }
    return render(request, 'specialties/dermatology/skin_exams.html', context)

@login_required
def dermatoscopy(request):
    """Dermatoscopia"""
    context = {
        'title': 'Dermatoscopia',
        'specialty_name': 'Dermatología',
        'page_title': 'Dermatoscopia',
        'description': 'Estudios dermatoscópicos especializados'
    }
    return render(request, 'specialties/dermatology/dermatoscopy.html', context)

@login_required
def dermatology_treatments(request):
    """Tratamientos Dermatológicos"""
    context = {
        'title': 'Tratamientos Dermatológicos',
        'specialty_name': 'Dermatología',
        'page_title': 'Tratamientos',
        'description': 'Tratamientos médicos dermatológicos'
    }
    return render(request, 'specialties/dermatology/treatments.html', context)

@login_required
def cosmetic_dermatology(request):
    """Dermatología Cosmética"""
    context = {
        'title': 'Dermatología Cosmética',
        'specialty_name': 'Dermatología',
        'page_title': 'Cosmética',
        'description': 'Tratamientos dermatológicos estéticos'
    }
    return render(request, 'specialties/dermatology/cosmetic.html', context)

# ==================== GINECOLOGÍA SUBMENU ====================
@login_required
def gynecologic_exams(request):
    """Exámenes Ginecológicos"""
    context = {
        'title': 'Exámenes Ginecológicos',
        'specialty_name': 'Ginecología',
        'page_title': 'Exámenes Ginecológicos',
        'description': 'Evaluaciones ginecológicas completas'
    }
    return render(request, 'specialties/gynecology/gynecologic_exams.html', context)

@login_required
def prenatal_control(request):
    """Control Prenatal"""
    context = {
        'title': 'Control Prenatal',
        'specialty_name': 'Ginecología',
        'page_title': 'Control Prenatal',
        'description': 'Seguimiento médico durante el embarazo'
    }
    return render(request, 'specialties/gynecology/pregnancy.html', context)

@login_required
def pap_smear(request):
    """Citología"""
    context = {
        'title': 'Citología',
        'specialty_name': 'Ginecología',
        'page_title': 'Citología',
        'description': 'Estudios citológicos y Papanicolaou'
    }
    return render(request, 'specialties/gynecology/pap_smear.html', context)

@login_required
def contraception(request):
    """Anticonceptivos"""
    context = {
        'title': 'Anticonceptivos',
        'specialty_name': 'Ginecología',
        'page_title': 'Anticonceptivos',
        'description': 'Asesoría en métodos anticonceptivos'
    }
    return render(request, 'specialties/gynecology/contraception.html', context)

# ==================== TRAUMATOLOGÍA SUBMENU ====================
@login_required
def xray_management(request):
    """Radiografías"""
    context = {
        'title': 'Radiografías',
        'specialty_name': 'Traumatología',
        'page_title': 'Radiografías',
        'description': 'Gestión de estudios radiológicos'
    }
    return render(request, 'specialties/traumatology/xrays.html', context)

@login_required
def fracture_management(request):
    """Fracturas"""
    context = {
        'title': 'Fracturas',
        'specialty_name': 'Traumatología',
        'page_title': 'Fracturas',
        'description': 'Tratamiento de fracturas y lesiones óseas'
    }
    return render(request, 'specialties/traumatology/fractures.html', context)

@login_required
def physiotherapy(request):
    """Fisioterapia"""
    context = {
        'title': 'Fisioterapia',
        'specialty_name': 'Traumatología',
        'page_title': 'Fisioterapia',
        'description': 'Programas de rehabilitación física'
    }
    return render(request, 'specialties/traumatology/therapy.html', context)

@login_required
def orthopedic_surgeries(request):
    """Cirugías Ortopédicas"""
    context = {
        'title': 'Cirugías Ortopédicas',
        'specialty_name': 'Traumatología',
        'page_title': 'Cirugías',
        'description': 'Procedimientos quirúrgicos ortopédicos'
    }
    return render(request, 'specialties/traumatology/surgeries.html', context)

# API Views
@login_required
def api_specialty_doctors(request, specialty_id):
    """API para obtener doctores de una especialidad"""
    try:
        specialty = Specialty.objects.get(pk=specialty_id)
        doctors = Doctor.objects.filter(
            specialties=specialty, 
            is_active=True, 
            accepts_new_patients=True
        ).select_related('user')
        
        doctors_data = [
            {
                'id': doctor.id,
                'name': doctor.full_name,
                'experience': doctor.years_experience,
                'license': doctor.license_number
            }
            for doctor in doctors
        ]
        
        return JsonResponse({'doctors': doctors_data})
    except Specialty.DoesNotExist:
        return JsonResponse({'error': 'Especialidad no encontrada'}, status=404)

@login_required
def api_specialty_procedures(request, specialty_id):
    """API para obtener procedimientos de una especialidad"""
    try:
        specialty = Specialty.objects.get(pk=specialty_id)
        procedures = SpecialtyProcedure.objects.filter(
            specialty=specialty, is_active=True
        )
        
        procedures_data = [
            {
                'id': procedure.id,
                'name': procedure.name,
                'duration': procedure.duration_minutes,
                'price': float(procedure.price),
                'requires_anesthesia': procedure.requires_anesthesia,
                'requires_fasting': procedure.requires_fasting
            }
            for procedure in procedures
        ]
        
        return JsonResponse({'procedures': procedures_data})
    except Specialty.DoesNotExist:
        return JsonResponse({'error': 'Especialidad no encontrada'}, status=404)

# AJAX Views for Dashboard Functionality
@login_required
def ajax_dashboard_stats(request):
    """API para obtener estadísticas del dashboard en tiempo real"""
    from datetime import datetime, timedelta
    from django.db.models import Q
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'consultations_today': SpecialtyConsultation.objects.filter(date__date=today).count(),
        'consultations_this_week': SpecialtyConsultation.objects.filter(date__gte=week_ago).count(),
        'pending_referrals': SpecialtyReferral.objects.filter(status='pending').count(),
        'urgent_referrals': SpecialtyReferral.objects.filter(
            status='pending', urgency__in=['urgent', 'emergency']
        ).count(),
        'active_treatments': SpecialtyTreatment.objects.filter(status='in_progress').count(),
        'completed_consultations': SpecialtyConsultation.objects.filter(is_completed=True).count(),
        'upcoming_consultations': SpecialtyConsultation.objects.filter(
            date__gt=timezone.now(),
            date__date__lte=today + timedelta(days=7)
        ).count(),
    }
    
    return JsonResponse({'success': True, 'stats': stats})

@login_required
def ajax_complete_consultation(request, consultation_id):
    """AJAX para completar una consulta"""
    if request.method == 'POST':
        try:
            consultation = get_object_or_404(SpecialtyConsultation, pk=consultation_id)
            consultation.is_completed = True
            consultation.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Consulta marcada como completada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def ajax_process_referral(request, referral_id):
    """AJAX para procesar una referencia"""
    if request.method == 'POST':
        try:
            referral = get_object_or_404(SpecialtyReferral, pk=referral_id)
            referral.status = 'processed'
            referral.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Referencia procesada exitosamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def ajax_specialty_activity(request, specialty_id):
    """API para obtener actividad reciente de una especialidad"""
    try:
        specialty = get_object_or_404(Specialty, pk=specialty_id)
        
        # Consultas recientes
        recent_consultations = SpecialtyConsultation.objects.filter(
            specialty=specialty
        ).select_related('patient', 'doctor__user').order_by('-date')[:5]
        
        consultations_data = [
            {
                'id': consultation.id,
                'patient_name': consultation.patient.get_full_name(),
                'doctor_name': consultation.doctor.user.get_full_name(),
                'date': consultation.date.strftime('%d/%m/%Y %H:%M'),
                'type': consultation.get_consultation_type_display(),
                'is_completed': consultation.is_completed
            }
            for consultation in recent_consultations
        ]
        
        return JsonResponse({
            'success': True,
            'specialty': specialty.name,
            'consultations': consultations_data
        })
    except Specialty.DoesNotExist:
        return JsonResponse({'error': 'Especialidad no encontrada'}, status=404)

@login_required
def ajax_search_specialties(request):
    """AJAX para búsqueda de especialidades"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'success': False, 'error': 'Término de búsqueda requerido'})
    
    specialties = Specialty.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).annotate(
        doctors_count=Count('doctor', distinct=True),
        consultations_count=Count('specialtyconsultation', distinct=True)
    )[:10]
    
    specialties_data = [
        {
            'id': specialty.id,
            'name': specialty.name,
            'description': specialty.description,
            'code': specialty.code,
            'doctors_count': specialty.doctors_count,
            'consultations_count': specialty.consultations_count
        }
        for specialty in specialties
    ]
    
    return JsonResponse({'success': True, 'specialties': specialties_data})

@login_required
def ajax_doctor_availability(request, doctor_id):
    """API para verificar disponibilidad de doctor"""
    try:
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        
        # Próximas citas del doctor
        today = timezone.now().date()
        upcoming_consultations = SpecialtyConsultation.objects.filter(
            doctor=doctor,
            date__date__gte=today
        ).order_by('date')[:5]
        
        consultations_data = [
            {
                'date': consultation.date.strftime('%d/%m/%Y %H:%M'),
                'patient': consultation.patient.get_full_name(),
                'specialty': consultation.specialty.name
            }
            for consultation in upcoming_consultations
        ]
        
        return JsonResponse({
            'success': True,
            'doctor': {
                'name': doctor.user.get_full_name(),
                'specialties': [s.name for s in doctor.specialties.all()],
                'is_available': doctor.accepts_new_patients,
                'upcoming_consultations': consultations_data
            }
        })
    except Doctor.DoesNotExist:
        return JsonResponse({'error': 'Doctor no encontrado'}, status=404)
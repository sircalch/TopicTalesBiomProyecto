from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import Patient
from appointments.models import Appointment

@login_required
def patient_list(request):
    """
    List all patients with search and filtering capabilities
    """
    organization = request.user.profile.organization
    
    # Get all patients for this organization
    patients = Patient.objects.filter(organization=organization).order_by('-registration_date')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(mother_last_name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    # Gender filter
    gender_filter = request.GET.get('gender')
    if gender_filter:
        patients = patients.filter(gender=gender_filter)
    
    # Age range filter
    age_range = request.GET.get('age_range')
    if age_range:
        today = timezone.now().date()
        if age_range == '0-17':
            birth_date_start = today - timedelta(days=17*365)
            patients = patients.filter(birth_date__gte=birth_date_start)
        elif age_range == '18-35':
            birth_date_start = today - timedelta(days=35*365)
            birth_date_end = today - timedelta(days=18*365)
            patients = patients.filter(birth_date__lte=birth_date_end, birth_date__gte=birth_date_start)
        elif age_range == '36-60':
            birth_date_start = today - timedelta(days=60*365)
            birth_date_end = today - timedelta(days=36*365)
            patients = patients.filter(birth_date__lte=birth_date_end, birth_date__gte=birth_date_start)
        elif age_range == '60+':
            birth_date_end = today - timedelta(days=60*365)
            patients = patients.filter(birth_date__lte=birth_date_end)
    
    # Blood type filter
    blood_type_filter = request.GET.get('blood_type')
    if blood_type_filter:
        patients = patients.filter(blood_type=blood_type_filter)
    
    # Statistics
    total_patients = Patient.objects.filter(organization=organization).count()
    active_patients = Patient.objects.filter(organization=organization, is_active=True).count()
    
    # New patients this month
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = Patient.objects.filter(
        organization=organization,
        registration_date__gte=this_month_start
    ).count()
    
    # Patients with appointments today
    today = timezone.now().date()
    with_appointments_today = Patient.objects.filter(
        organization=organization,
        appointments__start_datetime__date=today
    ).distinct().count()
    
    # Pagination
    per_page = request.GET.get('per_page', 25)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 25
    
    paginator = Paginator(patients, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Gestión de Pacientes',
        'patients': page_obj,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'new_this_month': new_this_month,
        'with_appointments_today': with_appointments_today,
        'paginator': paginator,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
    }
    
    return render(request, 'patients/list.html', context)

@login_required
def patient_create(request):
    """
    Create a new patient
    """
    from .forms import PatientForm
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.organization = request.user.profile.organization
            patient.created_by = request.user
            
            # Auto-generate patient_id if not provided
            if not patient.patient_id:
                organization = request.user.profile.organization
                last_patient = Patient.objects.filter(organization=organization).order_by('id').last()
                if last_patient:
                    try:
                        last_id = int(last_patient.patient_id.replace('PAC', ''))
                        patient.patient_id = f'PAC{str(last_id + 1).zfill(3)}'
                    except:
                        patient.patient_id = f'PAC{Patient.objects.filter(organization=organization).count() + 1:03d}'
                else:
                    patient.patient_id = 'PAC001'
            
            patient.save()
            messages.success(request, f'Paciente {patient.get_full_name()} creado exitosamente.')
            return redirect('patients:detail', patient_id=patient.id)
    else:
        form = PatientForm()
    
    return render(request, 'patients/create.html', {
        'title': 'Nuevo Paciente',
        'form': form
    })

@login_required
def patient_detail(request, patient_id):
    """
    Show patient details
    """
    patient = get_object_or_404(Patient, id=patient_id, organization=request.user.profile.organization)
    
    # Get recent appointments
    recent_appointments = patient.appointments.order_by('-start_datetime')[:5]
    
    # Get recent vital signs
    recent_vitals = patient.vital_signs.order_by('-recorded_at')[:5]
    
    # Get medical history
    try:
        medical_history = patient.medical_history
    except:
        medical_history = None
    
    # Get documents
    documents = patient.documents.order_by('-uploaded_at')[:10]
    
    context = {
        'title': f'Paciente: {patient.get_full_name()}',
        'patient': patient,
        'recent_appointments': recent_appointments,
        'recent_vitals': recent_vitals,
        'medical_history': medical_history,
        'documents': documents
    }
    
    return render(request, 'patients/detail.html', context)

@login_required
def patient_edit(request, patient_id):
    """
    Edit patient information
    """
    from .forms import PatientForm
    
    patient = get_object_or_404(Patient, id=patient_id, organization=request.user.profile.organization)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Información de {patient.get_full_name()} actualizada exitosamente.')
            return redirect('patients:detail', patient_id=patient.id)
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'patients/edit.html', {
        'title': f'Editar: {patient.get_full_name()}',
        'form': form,
        'patient': patient
    })

@login_required
def medical_history(request, patient_id):
    """
    Manage patient medical history
    """
    from .forms import MedicalHistoryForm
    from .models import MedicalHistory
    
    patient = get_object_or_404(Patient, id=patient_id, organization=request.user.profile.organization)
    
    try:
        history = patient.medical_history
    except MedicalHistory.DoesNotExist:
        history = None
    
    if request.method == 'POST':
        if history:
            form = MedicalHistoryForm(request.POST, instance=history)
        else:
            form = MedicalHistoryForm(request.POST)
        
        if form.is_valid():
            medical_history = form.save(commit=False)
            medical_history.patient = patient
            medical_history.updated_by = request.user
            medical_history.save()
            messages.success(request, 'Historia médica actualizada exitosamente.')
            return redirect('patients:medical_history', patient_id=patient.id)
    else:
        form = MedicalHistoryForm(instance=history)
    
    return render(request, 'patients/medical_history.html', {
        'title': f'Historia Médica: {patient.get_full_name()}',
        'form': form,
        'patient': patient,
        'history': history
    })

@login_required
def vital_signs(request, patient_id):
    """
    Manage patient vital signs
    """
    from .forms import VitalSignsForm
    
    patient = get_object_or_404(Patient, id=patient_id, organization=request.user.profile.organization)
    
    if request.method == 'POST':
        form = VitalSignsForm(request.POST)
        if form.is_valid():
            vital_signs = form.save(commit=False)
            vital_signs.patient = patient
            vital_signs.recorded_by = request.user
            vital_signs.save()
            messages.success(request, 'Signos vitales registrados exitosamente.')
            return redirect('patients:vital_signs', patient_id=patient.id)
    else:
        form = VitalSignsForm()
    
    # Get all vital signs for this patient
    vital_signs_list = patient.vital_signs.order_by('-recorded_at')
    
    return render(request, 'patients/vital_signs.html', {
        'title': f'Signos Vitales: {patient.get_full_name()}',
        'form': form,
        'patient': patient,
        'vital_signs_list': vital_signs_list
    })

@login_required
def documents(request, patient_id):
    """
    Manage patient documents
    """
    from .forms import PatientDocumentForm
    
    patient = get_object_or_404(Patient, id=patient_id, organization=request.user.profile.organization)
    
    if request.method == 'POST':
        form = PatientDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Documento subido exitosamente.')
            return redirect('patients:documents', patient_id=patient.id)
    else:
        form = PatientDocumentForm()
    
    # Get all documents for this patient
    documents_list = patient.documents.order_by('-uploaded_at')
    
    return render(request, 'patients/documents.html', {
        'title': f'Documentos: {patient.get_full_name()}',
        'form': form,
        'patient': patient,
        'documents_list': documents_list
    })

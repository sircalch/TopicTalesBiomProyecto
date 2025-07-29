from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import (
    MedicalRecord, Consultation, VitalSigns, LabResult, 
    Prescription, MedicalDocument, MedicalAlert
)
from .forms import (
    MedicalRecordForm, ConsultationForm, VitalSignsForm, 
    LabResultForm, PrescriptionForm, MedicalDocumentForm, 
    MedicalAlertForm, MedicalRecordSearchForm
)
from patients.models import Patient
from accounts.models import User


@login_required  
def index(request):
    """
    Medical records dashboard and overview
    """
    organization = request.user.profile.organization
    
    # Get search form
    search_form = MedicalRecordSearchForm(request.GET, organization=organization)
    
    # Get recent consultations
    recent_consultations = Consultation.objects.filter(
        organization=organization
    ).select_related('patient', 'doctor').order_by('-consultation_date')[:10]
    
    # Statistics
    total_patients = Patient.objects.filter(organization=organization).count()
    total_consultations = Consultation.objects.filter(organization=organization).count()
    
    # Consultations this month
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    consultations_this_month = Consultation.objects.filter(
        organization=organization,
        consultation_date__gte=this_month_start
    ).count()
    
    # Active prescriptions
    active_prescriptions = Prescription.objects.filter(
        patient__organization=organization,
        status='active'
    ).count()
    
    # Pending lab results
    pending_lab_results = LabResult.objects.filter(
        patient__organization=organization,
        status='pending'
    ).count()
    
    # Active medical alerts
    active_alerts = MedicalAlert.objects.filter(
        patient__organization=organization,
        is_active=True
    ).count()
    
    context = {
        'title': 'Expedientes Médicos',
        'search_form': search_form,
        'recent_consultations': recent_consultations,
        'total_patients': total_patients,
        'total_consultations': total_consultations,
        'consultations_this_month': consultations_this_month,
        'active_prescriptions': active_prescriptions,
        'pending_lab_results': pending_lab_results,
        'active_alerts': active_alerts
    }
    
    return render(request, 'medical_records/index.html', context)


@login_required
def patient_records(request, patient_id):
    """
    Complete medical record for a specific patient
    """
    organization = request.user.profile.organization
    patient = get_object_or_404(Patient, id=patient_id, organization=organization)
    
    # Get or create medical record
    medical_record, created = MedicalRecord.objects.get_or_create(
        patient=patient,
        organization=organization,
        defaults={'created_by': request.user}
    )
    
    # Get consultations
    consultations = Consultation.objects.filter(
        patient=patient
    ).select_related('doctor').order_by('-consultation_date')[:20]
    
    # Get recent vital signs
    recent_vitals = VitalSigns.objects.filter(
        patient=patient
    ).order_by('-recorded_at')[:10]
    
    # Get lab results
    lab_results = LabResult.objects.filter(
        patient=patient
    ).order_by('-ordered_date')[:15]
    
    # Get active prescriptions
    active_prescriptions = Prescription.objects.filter(
        patient=patient,
        status='active'
    ).order_by('-prescribed_date')
    
    # Get medical documents
    documents = MedicalDocument.objects.filter(
        patient=patient,
        is_active=True
    ).order_by('-uploaded_at')[:10]
    
    # Get active medical alerts
    alerts = MedicalAlert.objects.filter(
        patient=patient,
        is_active=True
    ).order_by('-created_at')
    
    # Statistics
    total_consultations = consultations.count()
    last_consultation = consultations.first()
    
    context = {
        'title': f'Expediente: {patient.get_full_name()}',
        'patient': patient,
        'medical_record': medical_record,
        'consultations': consultations,
        'recent_vitals': recent_vitals,
        'lab_results': lab_results,
        'active_prescriptions': active_prescriptions,
        'documents': documents,
        'alerts': alerts,
        'total_consultations': total_consultations,
        'last_consultation': last_consultation
    }
    
    return render(request, 'medical_records/patient_records.html', context)


@login_required
def edit_medical_record(request, patient_id):
    """
    Edit patient's medical record
    """
    organization = request.user.profile.organization
    patient = get_object_or_404(Patient, id=patient_id, organization=organization)
    
    # Get or create medical record
    medical_record, created = MedicalRecord.objects.get_or_create(
        patient=patient,
        organization=organization,
        defaults={'created_by': request.user}
    )
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=medical_record)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expediente médico actualizado exitosamente.')
            return redirect('medical_records:patient_records', patient_id=patient.id)
    else:
        form = MedicalRecordForm(instance=medical_record)
    
    context = {
        'title': f'Editar Expediente: {patient.get_full_name()}',
        'patient': patient,
        'medical_record': medical_record,
        'form': form
    }
    
    return render(request, 'medical_records/edit_record.html', context)


@login_required
def create_consultation(request, patient_id):
    """
    Create a new medical consultation
    """
    organization = request.user.profile.organization
    patient = get_object_or_404(Patient, id=patient_id, organization=organization)
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.doctor = request.user
            consultation.organization = organization
            consultation.save()
            
            messages.success(request, 'Consulta médica registrada exitosamente.')
            return redirect('medical_records:consultation_detail', consultation_id=consultation.id)
    else:
        # Pre-populate with current date/time
        form = ConsultationForm(initial={'consultation_date': timezone.now()})
    
    context = {
        'title': f'Nueva Consulta: {patient.get_full_name()}',
        'patient': patient,
        'form': form
    }
    
    return render(request, 'medical_records/create_consultation.html', context)


@login_required
def consultations_list(request, patient_id):
    """
    List all consultations for a patient
    """
    organization = request.user.profile.organization
    patient = get_object_or_404(Patient, id=patient_id, organization=organization)
    
    consultations = Consultation.objects.filter(
        patient=patient
    ).select_related('doctor').order_by('-consultation_date')
    
    # Apply filters
    consultation_type = request.GET.get('type')
    if consultation_type:
        consultations = consultations.filter(consultation_type=consultation_type)
    
    doctor_filter = request.GET.get('doctor')
    if doctor_filter:
        consultations = consultations.filter(doctor_id=doctor_filter)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        consultations = consultations.filter(
            Q(chief_complaint__icontains=search_query) |
            Q(diagnosis_primary__icontains=search_query) |
            Q(treatment_plan__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(consultations, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get doctors for filter
    doctors = User.objects.filter(
        profile__organization=organization, 
        role='doctor', 
        is_active=True
    ).order_by('first_name', 'last_name')
    
    context = {
        'title': f'Consultas: {patient.get_full_name()}',
        'patient': patient,
        'consultations': page_obj,
        'doctors': doctors,
        'paginator': paginator,
        'page_obj': page_obj
    }
    
    return render(request, 'medical_records/consultations_list.html', context)


@login_required
def consultation_detail(request, consultation_id):
    """
    Detailed view of a medical consultation
    """
    organization = request.user.profile.organization
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        organization=organization
    )
    
    # Get related data
    vital_signs = consultation.vital_signs.all()
    lab_results = consultation.lab_results.all()
    prescriptions = consultation.prescriptions.all()
    documents = consultation.documents.all()
    
    context = {
        'title': f'Consulta: {consultation.patient.get_full_name()}',
        'consultation': consultation,
        'vital_signs': vital_signs,
        'lab_results': lab_results,
        'prescriptions': prescriptions,
        'documents': documents
    }
    
    return render(request, 'medical_records/consultation_detail.html', context)


@login_required
def edit_consultation(request, consultation_id):
    """
    Edit a medical consultation
    """
    organization = request.user.profile.organization
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        organization=organization
    )
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Consulta actualizada exitosamente.')
            return redirect('medical_records:consultation_detail', consultation_id=consultation.id)
    else:
        form = ConsultationForm(instance=consultation)
    
    context = {
        'title': f'Editar Consulta: {consultation.patient.get_full_name()}',
        'consultation': consultation,
        'form': form
    }
    
    return render(request, 'medical_records/edit_consultation.html', context)


@login_required
def add_vital_signs(request, consultation_id):
    """
    Add vital signs to a consultation
    """
    organization = request.user.profile.organization
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        organization=organization
    )
    
    if request.method == 'POST':
        form = VitalSignsForm(request.POST)
        if form.is_valid():
            vital_signs = form.save(commit=False)
            vital_signs.consultation = consultation
            vital_signs.patient = consultation.patient
            vital_signs.recorded_by = request.user
            vital_signs.save()
            
            messages.success(request, 'Signos vitales registrados exitosamente.')
            return redirect('medical_records:consultation_detail', consultation_id=consultation.id)
    else:
        form = VitalSignsForm()
    
    context = {
        'title': f'Agregar Signos Vitales: {consultation.patient.get_full_name()}',
        'consultation': consultation,
        'form': form
    }
    
    return render(request, 'medical_records/add_vital_signs.html', context)


@login_required
def add_lab_result(request, consultation_id):
    """
    Add laboratory result to a consultation
    """
    organization = request.user.profile.organization
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        organization=organization
    )
    
    if request.method == 'POST':
        form = LabResultForm(request.POST)
        if form.is_valid():
            lab_result = form.save(commit=False)
            lab_result.consultation = consultation
            lab_result.patient = consultation.patient
            lab_result.ordered_by = request.user
            lab_result.save()
            
            messages.success(request, 'Resultado de laboratorio registrado exitosamente.')
            return redirect('medical_records:consultation_detail', consultation_id=consultation.id)
    else:
        form = LabResultForm()
    
    context = {
        'title': f'Agregar Resultado de Laboratorio: {consultation.patient.get_full_name()}',
        'consultation': consultation,
        'form': form
    }
    
    return render(request, 'medical_records/add_lab_result.html', context)


@login_required
def add_prescription(request, consultation_id):
    """
    Add prescription to a consultation
    """
    organization = request.user.profile.organization
    consultation = get_object_or_404(
        Consultation, 
        id=consultation_id, 
        organization=organization
    )
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.consultation = consultation
            prescription.patient = consultation.patient
            prescription.prescribed_by = request.user
            prescription.save()
            
            messages.success(request, 'Prescripción agregada exitosamente.')
            return redirect('medical_records:consultation_detail', consultation_id=consultation.id)
    else:
        form = PrescriptionForm()
    
    context = {
        'title': f'Agregar Prescripción: {consultation.patient.get_full_name()}',
        'consultation': consultation,
        'form': form
    }
    
    return render(request, 'medical_records/add_prescription.html', context)


@login_required
def upload_document(request, patient_id):
    """
    Upload medical document for a patient
    """
    organization = request.user.profile.organization
    patient = get_object_or_404(Patient, id=patient_id, organization=organization)
    
    if request.method == 'POST':
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.patient = patient
            document.uploaded_by = request.user
            document.save()
            
            messages.success(request, 'Documento médico subido exitosamente.')
            return redirect('medical_records:patient_records', patient_id=patient.id)
    else:
        form = MedicalDocumentForm()
    
    context = {
        'title': f'Subir Documento: {patient.get_full_name()}',
        'patient': patient,
        'form': form
    }
    
    return render(request, 'medical_records/upload_document.html', context)


@login_required
def create_alert(request, patient_id):
    """
    Create medical alert for a patient
    """
    organization = request.user.profile.organization
    patient = get_object_or_404(Patient, id=patient_id, organization=organization)
    
    if request.method == 'POST':
        form = MedicalAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.patient = patient
            alert.created_by = request.user
            alert.save()
            
            messages.success(request, 'Alerta médica creada exitosamente.')
            return redirect('medical_records:patient_records', patient_id=patient.id)
    else:
        form = MedicalAlertForm()
    
    context = {
        'title': f'Crear Alerta: {patient.get_full_name()}',
        'patient': patient,
        'form': form
    }
    
    return render(request, 'medical_records/create_alert.html', context)


@login_required
def search_records(request):
    """
    Search medical records
    """
    organization = request.user.profile.organization
    
    form = MedicalRecordSearchForm(request.GET, organization=organization)
    results = []
    
    if form.is_valid() and any(form.cleaned_data.values()):
        # Build search query
        consultations = Consultation.objects.filter(
            organization=organization
        ).select_related('patient', 'doctor')
        
        if form.cleaned_data.get('search'):
            search_query = form.cleaned_data['search']
            consultations = consultations.filter(
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(chief_complaint__icontains=search_query) |
                Q(diagnosis_primary__icontains=search_query) |
                Q(medications_prescribed__icontains=search_query)
            )
        
        if form.cleaned_data.get('consultation_type'):
            consultations = consultations.filter(
                consultation_type=form.cleaned_data['consultation_type']
            )
        
        if form.cleaned_data.get('doctor'):
            consultations = consultations.filter(
                doctor=form.cleaned_data['doctor']
            )
        
        if form.cleaned_data.get('date_from'):
            consultations = consultations.filter(
                consultation_date__date__gte=form.cleaned_data['date_from']
            )
        
        if form.cleaned_data.get('date_to'):
            consultations = consultations.filter(
                consultation_date__date__lte=form.cleaned_data['date_to']
            )
        
        results = consultations.order_by('-consultation_date')[:100]
    
    context = {
        'title': 'Buscar Expedientes Médicos',
        'form': form,
        'results': results
    }
    
    return render(request, 'medical_records/search.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Appointment, AppointmentType, AppointmentNote, DoctorSchedule, AppointmentBlock
from .forms import (
    AppointmentForm, AppointmentTypeForm, AppointmentNoteForm, 
    DoctorScheduleForm, AppointmentBlockForm, AppointmentFilterForm,
    QuickAppointmentForm
)
from accounts.models import User
from patients.models import Patient


@login_required
def calendar_view(request):
    """
    Main calendar view with appointments display
    """
    organization = request.user.profile.organization
    
    # Get filter form
    filter_form = AppointmentFilterForm(request.GET, organization=organization)
    
    # Get doctors for quick filters
    doctors = User.objects.filter(
        profile__organization=organization, 
        role='doctor', 
        is_active=True
    ).order_by('first_name', 'last_name')
    
    # Get appointment types
    appointment_types = AppointmentType.objects.filter(
        organization=organization, 
        is_active=True
    ).order_by('name')
    
    # Statistics for today
    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(
        organization=organization,
        start_datetime__date=today
    ).count()
    
    context = {
        'title': 'Calendario de Citas',
        'filter_form': filter_form,
        'doctors': doctors,
        'appointment_types': appointment_types,
        'today_appointments': today_appointments
    }
    
    return render(request, 'appointments/calendar.html', context)


@login_required
def appointment_create(request):
    """
    Create a new appointment
    """
    organization = request.user.profile.organization
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, organization=organization)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.organization = organization
            appointment.created_by = request.user
            
            # Auto-calculate end_datetime
            appointment.end_datetime = appointment.start_datetime + timedelta(
                minutes=appointment.appointment_type.duration_minutes
            )
            
            appointment.save()
            messages.success(request, f'Cita creada exitosamente para {appointment.patient.get_full_name()}.')
            return redirect('appointments:detail', appointment_id=appointment.id)
    else:
        # Pre-populate with URL parameters if provided
        initial_data = {}
        if request.GET.get('doctor_id'):
            initial_data['doctor'] = request.GET.get('doctor_id')
        if request.GET.get('patient_id'):
            initial_data['patient'] = request.GET.get('patient_id')
        if request.GET.get('start_datetime'):
            initial_data['start_datetime'] = request.GET.get('start_datetime')
            
        form = AppointmentForm(initial=initial_data, organization=organization)
    
    return render(request, 'appointments/create.html', {
        'title': 'Nueva Cita',
        'form': form
    })


@login_required
def appointment_detail(request, appointment_id):
    """
    Show appointment details
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, organization=request.user.profile.organization)
    
    # Get consultation note if exists
    try:
        consultation_note = appointment.consultation_note
    except AppointmentNote.DoesNotExist:
        consultation_note = None
    
    context = {
        'title': f'Cita: {appointment.patient.get_full_name()}',
        'appointment': appointment,
        'consultation_note': consultation_note
    }
    
    return render(request, 'appointments/detail.html', context)


@login_required
def appointment_edit(request, appointment_id):
    """
    Edit appointment information
    """
    organization = request.user.profile.organization
    appointment = get_object_or_404(Appointment, id=appointment_id, organization=organization)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, organization=organization)
        if form.is_valid():
            appointment = form.save()
            # Recalculate end_datetime
            appointment.end_datetime = appointment.start_datetime + timedelta(
                minutes=appointment.appointment_type.duration_minutes
            )
            appointment.save()
            messages.success(request, f'Cita actualizada exitosamente.')
            return redirect('appointments:detail', appointment_id=appointment.id)
    else:
        form = AppointmentForm(instance=appointment, organization=organization)
    
    return render(request, 'appointments/edit.html', {
        'title': f'Editar Cita: {appointment.patient.get_full_name()}',
        'form': form,
        'appointment': appointment
    })


@login_required
def appointment_cancel(request, appointment_id):
    """
    Cancel an appointment
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, organization=request.user.profile.organization)
    
    if not appointment.can_be_cancelled:
        messages.error(request, 'Esta cita no puede ser cancelada.')
        return redirect('appointments:detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        appointment.status = 'cancelled'
        appointment.notes = f"{appointment.notes}\n\nCancelada: {cancellation_reason}" if appointment.notes else f"Cancelada: {cancellation_reason}"
        appointment.save()
        
        messages.success(request, 'Cita cancelada exitosamente.')
        return redirect('appointments:calendar')
    
    return render(request, 'appointments/cancel.html', {
        'title': f'Cancelar Cita: {appointment.patient.get_full_name()}',
        'appointment': appointment
    })


@login_required
def appointment_reschedule(request, appointment_id):
    """
    Reschedule an appointment to a new date/time
    """
    organization = request.user.profile.organization
    appointment = get_object_or_404(Appointment, id=appointment_id, organization=organization)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, organization=organization)
        if form.is_valid():
            old_datetime = appointment.start_datetime
            appointment = form.save()
            appointment.status = 'rescheduled'
            appointment.notes = f"{appointment.notes}\n\nReprogramada desde: {old_datetime.strftime('%d/%m/%Y %H:%M')}" if appointment.notes else f"Reprogramada desde: {old_datetime.strftime('%d/%m/%Y %H:%M')}"
            appointment.save()
            
            messages.success(request, 'Cita reprogramada exitosamente.')
            return redirect('appointments:detail', appointment_id=appointment.id)
    else:
        form = AppointmentForm(instance=appointment, organization=organization)
    
    return render(request, 'appointments/reschedule.html', {
        'title': f'Reprogramar Cita: {appointment.patient.get_full_name()}',
        'form': form,
        'appointment': appointment
    })


@login_required
def appointment_complete(request, appointment_id):
    """
    Mark appointment as completed and add consultation notes
    """
    appointment = get_object_or_404(Appointment, id=appointment_id, organization=request.user.profile.organization)
    
    # Get or create consultation note
    try:
        consultation_note = appointment.consultation_note
    except AppointmentNote.DoesNotExist:
        consultation_note = None
    
    if request.method == 'POST':
        if consultation_note:
            form = AppointmentNoteForm(request.POST, instance=consultation_note)
        else:
            form = AppointmentNoteForm(request.POST)
        
        if form.is_valid():
            note = form.save(commit=False)
            note.appointment = appointment
            note.created_by = request.user
            note.save()
            
            # Mark appointment as completed
            appointment.status = 'completed'
            appointment.save()
            
            messages.success(request, 'Cita completada y notas guardadas exitosamente.')
            return redirect('appointments:detail', appointment_id=appointment.id)
    else:
        form = AppointmentNoteForm(instance=consultation_note)
    
    return render(request, 'appointments/complete.html', {
        'title': f'Completar Cita: {appointment.patient.get_full_name()}',
        'form': form,
        'appointment': appointment,
        'consultation_note': consultation_note
    })


@login_required
def appointment_list(request):
    """
    List appointments with filtering and pagination
    """
    organization = request.user.profile.organization
    
    # Get all appointments for this organization
    appointments = Appointment.objects.filter(organization=organization).order_by('-start_datetime')
    
    # Apply filters
    filter_form = AppointmentFilterForm(request.GET, organization=organization)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('doctor'):
            appointments = appointments.filter(doctor=filter_form.cleaned_data['doctor'])
        if filter_form.cleaned_data.get('appointment_type'):
            appointments = appointments.filter(appointment_type=filter_form.cleaned_data['appointment_type'])
        if filter_form.cleaned_data.get('status'):
            appointments = appointments.filter(status=filter_form.cleaned_data['status'])
        if filter_form.cleaned_data.get('priority'):
            appointments = appointments.filter(priority=filter_form.cleaned_data['priority'])
        if filter_form.cleaned_data.get('date_from'):
            appointments = appointments.filter(start_datetime__date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data.get('date_to'):
            appointments = appointments.filter(start_datetime__date__lte=filter_form.cleaned_data['date_to'])
        if filter_form.cleaned_data.get('search'):
            search_query = filter_form.cleaned_data['search']
            appointments = appointments.filter(
                Q(patient__first_name__icontains=search_query) |
                Q(patient__last_name__icontains=search_query) |
                Q(reason__icontains=search_query) |
                Q(doctor__first_name__icontains=search_query) |
                Q(doctor__last_name__icontains=search_query)
            )
    
    # Pagination
    paginator = Paginator(appointments, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Lista de Citas',
        'appointments': page_obj,
        'filter_form': filter_form,
        'paginator': paginator,
        'page_obj': page_obj
    }
    
    return render(request, 'appointments/list.html', context)


@login_required
def calendar_events(request):
    """
    AJAX endpoint for calendar events
    """
    organization = request.user.profile.organization
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    doctor_id = request.GET.get('doctor_id')
    
    # Build query
    appointments = Appointment.objects.filter(organization=organization)
    
    if start_date:
        appointments = appointments.filter(start_datetime__gte=start_date)
    if end_date:
        appointments = appointments.filter(start_datetime__lt=end_date)
    if doctor_id:
        appointments = appointments.filter(doctor_id=doctor_id)
    
    # Convert to FullCalendar format
    events = []
    for appointment in appointments:
        events.append({
            'id': appointment.id,
            'title': f"{appointment.patient.get_full_name()} - {appointment.appointment_type.name}",
            'start': appointment.start_datetime.isoformat(),
            'end': appointment.end_datetime.isoformat(),
            'backgroundColor': appointment.appointment_type.color,
            'borderColor': appointment.appointment_type.color,
            'textColor': '#ffffff',
            'extendedProps': {
                'patient': appointment.patient.get_full_name(),
                'doctor': appointment.doctor.get_full_name(),
                'status': appointment.get_status_display(),
                'priority': appointment.get_priority_display(),
                'reason': appointment.reason[:50] + '...' if len(appointment.reason) > 50 else appointment.reason
            }
        })
    
    return JsonResponse({'events': events})


@login_required
def available_slots(request):
    """
    AJAX endpoint for available time slots
    """
    organization = request.user.profile.organization
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    appointment_type_id = request.GET.get('appointment_type_id')
    
    if not all([doctor_id, date_str, appointment_type_id]):
        return JsonResponse({'slots': []})
    
    try:
        doctor = User.objects.get(id=doctor_id, profile__organization=organization)
        appointment_type = AppointmentType.objects.get(id=appointment_type_id, organization=organization)
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (User.DoesNotExist, AppointmentType.DoesNotExist, ValueError):
        return JsonResponse({'slots': []})
    
    # Get doctor's schedule for the day
    day_of_week = selected_date.weekday()
    schedule = DoctorSchedule.objects.filter(
        doctor=doctor,
        day_of_week=day_of_week,
        is_active=True
    ).first()
    
    if not schedule:
        return JsonResponse({'slots': []})
    
    # Generate time slots
    slots = []
    current_time = datetime.combine(selected_date, schedule.start_time)
    end_time = datetime.combine(selected_date, schedule.end_time)
    slot_duration = timedelta(minutes=appointment_type.duration_minutes)
    
    while current_time + slot_duration <= end_time:
        # Check if slot is available
        conflicts = Appointment.objects.filter(
            doctor=doctor,
            start_datetime__lt=current_time + slot_duration,
            end_datetime__gt=current_time,
            status__in=['scheduled', 'confirmed', 'in_progress']
        ).exists()
        
        # Check for blocks
        blocks = AppointmentBlock.objects.filter(
            doctor=doctor,
            start_datetime__lt=current_time + slot_duration,
            end_datetime__gt=current_time
        ).exists()
        
        if not conflicts and not blocks:
            slots.append({
                'time': current_time.strftime('%H:%M'),
                'datetime': current_time.isoformat()
            })
        
        current_time += timedelta(minutes=30)  # 30-minute intervals
    
    return JsonResponse({'slots': slots})


@login_required
@require_http_methods(["POST"])
def quick_appointment(request):
    """
    AJAX endpoint for quick appointment creation from calendar
    """
    organization = request.user.profile.organization
    
    try:
        data = json.loads(request.body)
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            appointment_type_id=data['appointment_type_id'],
            start_datetime=datetime.fromisoformat(data['start_datetime']),
            reason=data['reason'],
            organization=organization,
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'appointment_id': appointment.id,
            'message': 'Cita creada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

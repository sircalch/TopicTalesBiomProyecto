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
    
    # Get patients for quick appointment modal
    patients = Patient.objects.filter(
        organization=organization,
        is_active=True
    ).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Calendario de Citas',
        'filter_form': filter_form,
        'doctors': doctors,
        'appointment_types': appointment_types,
        'patients': patients,
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
        print(f"POST data received: {request.POST}")  # Debug line
        form = AppointmentForm(request.POST, organization=organization)
        print(f"Form is valid: {form.is_valid()}")  # Debug line
        print(f"Form errors: {form.errors}")  # Debug line
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
            print(f"Form validation failed: {form.errors}")  # Debug line
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
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'error': 'Esta cita no puede ser cancelada.'
            }, status=400)
        messages.error(request, 'Esta cita no puede ser cancelada.')
        return redirect('appointments:detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        # Handle JSON requests from AJAX
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                cancellation_reason = data.get('cancellation_reason', 'Cancelada desde dashboard')
            except json.JSONDecodeError:
                cancellation_reason = 'Cancelada desde dashboard'
        else:
            cancellation_reason = request.POST.get('cancellation_reason', '')
        
        appointment.status = 'cancelled'
        appointment.notes = f"{appointment.notes}\n\nCancelada: {cancellation_reason}" if appointment.notes else f"Cancelada: {cancellation_reason}"
        appointment.save()
        
        # Return JSON response for AJAX requests
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Cita cancelada exitosamente.'
            })
        
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
        # Handle JSON requests from AJAX (quick complete without notes)
        if request.content_type == 'application/json':
            # Mark appointment as completed without detailed notes
            appointment.status = 'completed'
            appointment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Cita marcada como completada exitosamente.'
            })
        
        # Handle regular form submission
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
    
    print(f"Calendar events request - start: {start_date}, end: {end_date}, doctor: {doctor_id}")  # Debug
    
    # Build query
    appointments = Appointment.objects.filter(organization=organization)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            appointments = appointments.filter(start_datetime__gte=start_dt)
            print(f"Filtering by start_date >= {start_dt}")
        except ValueError:
            print(f"Invalid start_date format: {start_date}")
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            appointments = appointments.filter(start_datetime__lt=end_dt)
            print(f"Filtering by end_date < {end_dt}")
        except ValueError:
            print(f"Invalid end_date format: {end_date}")
    if doctor_id:
        appointments = appointments.filter(doctor_id=doctor_id)
    
    print(f"Found {appointments.count()} appointments")  # Debug
    
    # Convert to FullCalendar format
    events = []
    for appointment in appointments:
        event = {
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
        }
        events.append(event)
        print(f"Added event: {event['title']} at {event['start']}")  # Debug
    
    print(f"Returning {len(events)} events")  # Debug
    return JsonResponse(events, safe=False)


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
        print(f"Quick appointment data received: {data}")  # Debug line
        
        # Validate required fields
        required_fields = ['patient_id', 'doctor_id', 'appointment_type_id', 'start_datetime', 'reason']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Campo requerido faltante: {field}'
                }, status=400)
        
        # Parse datetime
        try:
            start_datetime = datetime.fromisoformat(data['start_datetime'].replace('Z', '+00:00'))
            if timezone.is_aware(start_datetime):
                start_datetime = timezone.localtime(start_datetime)
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': f'Formato de fecha inválido: {str(e)}'
            }, status=400)
        
        # Get related objects to verify they exist
        try:
            patient = Patient.objects.get(id=data['patient_id'], organization=organization)
            doctor = User.objects.get(id=data['doctor_id'], profile__organization=organization, role='doctor')
            appointment_type = AppointmentType.objects.get(id=data['appointment_type_id'], organization=organization)
        except (Patient.DoesNotExist, User.DoesNotExist, AppointmentType.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'message': f'Objeto no encontrado: {str(e)}'
            }, status=404)
        
        # Calculate end datetime
        end_datetime = start_datetime + timedelta(minutes=appointment_type.duration_minutes)
        
        # Check for conflicts
        conflicts = Appointment.objects.filter(
            doctor=doctor,
            organization=organization,
            start_datetime__lt=end_datetime,
            end_datetime__gt=start_datetime,
            status__in=['scheduled', 'confirmed', 'in_progress']
        )
        
        if conflicts.exists():
            return JsonResponse({
                'success': False,
                'message': 'El médico ya tiene una cita programada en este horario'
            }, status=400)
        
        # Create appointment
        appointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_type=appointment_type,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            reason=data['reason'].strip(),
            organization=organization,
            created_by=request.user
        )
        
        print(f"Quick appointment created successfully: ID {appointment.id}")  # Debug line
        
        return JsonResponse({
            'success': True,
            'appointment_id': appointment.id,
            'message': 'Cita creada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        print(f"Error creating quick appointment: {str(e)}")  # Debug line
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def update_appointment_time(request):
    """
    AJAX endpoint to update appointment time via drag & drop
    """
    organization = request.user.profile.organization
    
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        new_start = data.get('start_datetime')
        new_end = data.get('end_datetime')
        
        # Get appointment
        appointment = get_object_or_404(Appointment, id=appointment_id, organization=organization)
        
        # Parse new dates
        new_start_dt = datetime.fromisoformat(new_start.replace('Z', '+00:00'))
        if new_end:
            new_end_dt = datetime.fromisoformat(new_end.replace('Z', '+00:00'))
        else:
            # Calculate end time based on appointment type duration
            new_end_dt = new_start_dt + timedelta(minutes=appointment.appointment_type.duration_minutes)
        
        # Convert to local timezone if needed
        if timezone.is_aware(new_start_dt):
            new_start_dt = timezone.localtime(new_start_dt)
            new_end_dt = timezone.localtime(new_end_dt)
        
        # Check for conflicts
        conflicts = Appointment.objects.filter(
            doctor=appointment.doctor,
            organization=organization,
            start_datetime__lt=new_end_dt,
            end_datetime__gt=new_start_dt
        ).exclude(id=appointment.id)
        
        if conflicts.exists():
            return JsonResponse({
                'success': False,
                'message': 'Conflicto de horario con otra cita existente'
            })
        
        # Check doctor availability
        weekday = new_start_dt.weekday()
        doctor_schedule = DoctorSchedule.objects.filter(
            doctor=appointment.doctor,
            day_of_week=weekday,
            start_time__lte=new_start_dt.time(),
            end_time__gte=new_end_dt.time(),
            is_active=True
        ).exists()
        
        if not doctor_schedule:
            return JsonResponse({
                'success': False,
                'message': 'El médico no está disponible en este horario'
            })
        
        # Update appointment
        appointment.start_datetime = new_start_dt
        appointment.end_datetime = new_end_dt
        appointment.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cita actualizada exitosamente',
            'new_start': appointment.start_datetime.isoformat(),
            'new_end': appointment.end_datetime.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al actualizar la cita: {str(e)}'
        }, status=400)


@login_required
def appointment_details_ajax(request, appointment_id):
    """
    AJAX endpoint to get appointment details for modal display
    """
    organization = request.user.profile.organization
    appointment = get_object_or_404(Appointment, id=appointment_id, organization=organization)
    
    # Get consultation note if exists
    try:
        consultation_note = appointment.consultation_note
    except AppointmentNote.DoesNotExist:
        consultation_note = None
    
    # Prepare appointment data
    appointment_data = {
        'id': appointment.id,
        'patient_name': appointment.patient.get_full_name(),
        'patient_id': appointment.patient.patient_id,
        'doctor_name': appointment.doctor.get_full_name(),
        'appointment_type': appointment.appointment_type.name,
        'start_datetime': appointment.start_datetime.strftime('%d/%m/%Y %H:%M'),
        'end_datetime': appointment.end_datetime.strftime('%d/%m/%Y %H:%M'),
        'duration': appointment.duration,
        'status': appointment.get_status_display(),
        'status_class': {
            'scheduled': 'warning',
            'confirmed': 'info', 
            'in_progress': 'primary',
            'completed': 'success',
            'cancelled': 'danger',
            'no_show': 'secondary'
        }.get(appointment.status, 'secondary'),
        'priority': appointment.get_priority_display(),
        'reason': appointment.reason,
        'notes': appointment.notes,
        'patient_phone': appointment.patient_phone,
        'patient_email': appointment.patient_email,
        'can_be_cancelled': appointment.can_be_cancelled,
        'is_past': appointment.is_past,
        'amount_charged': float(appointment.amount_charged) if appointment.amount_charged else None,
        'payment_method': appointment.get_payment_method_display() if appointment.payment_method else None,
        'has_consultation_note': consultation_note is not None
    }
    
    return JsonResponse({
        'success': True,
        'appointment': appointment_data
    })


@login_required
def todays_appointments(request):
    """
    View for today's appointments
    """
    organization = request.user.profile.organization
    today = timezone.now().date()
    
    # Get today's appointments
    appointments = Appointment.objects.filter(
        organization=organization,
        start_datetime__date=today
    ).order_by('start_datetime').select_related('patient', 'doctor', 'appointment_type')
    
    # Apply filters if provided
    doctor_filter = request.GET.get('doctor')
    status_filter = request.GET.get('status')
    
    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    # Get statistics
    total_today = appointments.count()
    completed_today = appointments.filter(status='completed').count()
    pending_today = appointments.filter(status__in=['scheduled', 'confirmed']).count()
    cancelled_today = appointments.filter(status='cancelled').count()
    
    # Get doctors for filter
    doctors = User.objects.filter(
        profile__organization=organization,
        role='doctor',
        is_active=True
    ).order_by('first_name', 'last_name')
    
    context = {
        'title': 'Citas de Hoy',
        'appointments': appointments,
        'doctors': doctors,
        'today_date': today,
        'total_today': total_today,
        'completed_today': completed_today,
        'pending_today': pending_today,
        'cancelled_today': cancelled_today,
        'doctor_filter': doctor_filter,
        'status_filter': status_filter
    }
    
    return render(request, 'appointments/todays_appointments.html', context)


@login_required
def doctor_schedule_config(request):
    """
    View for configuring doctor schedules
    """
    organization = request.user.profile.organization
    
    # Get all doctors in the organization
    doctors = User.objects.filter(
        profile__organization=organization,
        role='doctor',
        is_active=True
    ).order_by('first_name', 'last_name')
    
    # Get existing schedules
    schedules = DoctorSchedule.objects.filter(
        doctor__profile__organization=organization
    ).select_related('doctor').order_by('doctor__first_name', 'day_of_week')
    
    # Group schedules by doctor
    doctor_schedules = {}
    for schedule in schedules:
        doctor_name = schedule.doctor.get_full_name()
        if doctor_name not in doctor_schedules:
            doctor_schedules[doctor_name] = []
        doctor_schedules[doctor_name].append(schedule)
    
    # Days of the week
    days_of_week = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo')
    ]
    
    context = {
        'title': 'Configurar Horarios',
        'doctors': doctors,
        'doctor_schedules': doctor_schedules,
        'days_of_week': days_of_week
    }
    
    return render(request, 'appointments/schedule_config.html', context)


@login_required
def create_schedule(request):
    """
    AJAX endpoint to create a new doctor schedule
    """
    print(f"create_schedule called with method: {request.method}")
    print(f"User: {request.user}")
    print(f"POST data: {request.POST}")
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': f'Método {request.method} no permitido. Use POST.'
        }, status=405)
    
    try:
        organization = request.user.profile.organization
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': 'Usuario no tiene organización asignada'
        }, status=400)
    
    try:
        doctor_id = request.POST.get('doctor_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        break_start = request.POST.get('break_start')
        break_end = request.POST.get('break_end')
        
        # Validate required fields
        if not all([doctor_id, day_of_week, start_time, end_time]):
            return JsonResponse({
                'success': False,
                'message': 'Faltan campos requeridos: médico, día, hora inicio y hora fin'
            }, status=400)
        
        # Get doctor
        try:
            doctor = User.objects.get(
                id=doctor_id, 
                profile__organization=organization, 
                role='doctor'
            )
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Médico no encontrado'
            }, status=404)
        
        # Parse times
        try:
            from datetime import datetime
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            break_start_obj = None
            break_end_obj = None
            if break_start and break_end:
                break_start_obj = datetime.strptime(break_start, '%H:%M').time()
                break_end_obj = datetime.strptime(break_end, '%H:%M').time()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de hora inválido. Use HH:MM'
            }, status=400)
        
        # Validate times
        if start_time_obj >= end_time_obj:
            return JsonResponse({
                'success': False,
                'message': 'La hora de inicio debe ser anterior a la hora de fin'
            }, status=400)
        
        if break_start_obj and break_end_obj:
            if break_start_obj >= break_end_obj:
                return JsonResponse({
                    'success': False,
                    'message': 'La hora de inicio del descanso debe ser anterior a la hora de fin'
                }, status=400)
            
            if break_start_obj < start_time_obj or break_end_obj > end_time_obj:
                return JsonResponse({
                    'success': False,
                    'message': 'El horario de descanso debe estar dentro del horario de trabajo'
                }, status=400)
        
        # Check for existing schedule
        existing_schedule = DoctorSchedule.objects.filter(
            doctor=doctor,
            day_of_week=int(day_of_week)
        ).first()
        
        if existing_schedule:
            return JsonResponse({
                'success': False,
                'message': f'Ya existe un horario para este médico en este día'
            }, status=400)
        
        # Create schedule
        schedule = DoctorSchedule.objects.create(
            doctor=doctor,
            organization=organization,
            day_of_week=int(day_of_week),
            start_time=start_time_obj,
            end_time=end_time_obj,
            break_start=break_start_obj,
            break_end=break_end_obj,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Horario creado exitosamente',
            'schedule_id': schedule.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)


@login_required
def update_schedule(request):
    """
    AJAX endpoint to update an existing doctor schedule
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': f'Método {request.method} no permitido. Use POST.'
        }, status=405)
    
    try:
        organization = request.user.profile.organization
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': 'Usuario no tiene organización asignada'
        }, status=400)
    
    try:
        schedule_id = request.POST.get('schedule_id')
        day_of_week = request.POST.get('day_of_week')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        break_start = request.POST.get('break_start')
        break_end = request.POST.get('break_end')
        
        # Validate required fields
        if not all([schedule_id, day_of_week, start_time, end_time]):
            return JsonResponse({
                'success': False,
                'message': 'Faltan campos requeridos'
            }, status=400)
        
        # Get schedule
        try:
            schedule = DoctorSchedule.objects.get(
                id=schedule_id,
                doctor__profile__organization=organization
            )
        except DoctorSchedule.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Horario no encontrado'
            }, status=404)
        
        # Parse times
        try:
            from datetime import datetime
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            break_start_obj = None
            break_end_obj = None
            if break_start and break_end:
                break_start_obj = datetime.strptime(break_start, '%H:%M').time()
                break_end_obj = datetime.strptime(break_end, '%H:%M').time()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de hora inválido. Use HH:MM'
            }, status=400)
        
        # Validate times
        if start_time_obj >= end_time_obj:
            return JsonResponse({
                'success': False,
                'message': 'La hora de inicio debe ser anterior a la hora de fin'
            }, status=400)
        
        if break_start_obj and break_end_obj:
            if break_start_obj >= break_end_obj:
                return JsonResponse({
                    'success': False,
                    'message': 'La hora de inicio del descanso debe ser anterior a la hora de fin'
                }, status=400)
            
            if break_start_obj < start_time_obj or break_end_obj > end_time_obj:
                return JsonResponse({
                    'success': False,
                    'message': 'El horario de descanso debe estar dentro del horario de trabajo'
                }, status=400)
        
        # Update schedule
        schedule.day_of_week = int(day_of_week)
        schedule.start_time = start_time_obj
        schedule.end_time = end_time_obj
        schedule.break_start = break_start_obj
        schedule.break_end = break_end_obj
        schedule.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Horario actualizado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)


@login_required
def delete_schedule(request, schedule_id):
    """
    AJAX endpoint to delete a doctor schedule
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': f'Método {request.method} no permitido. Use POST.'
        }, status=405)
    
    try:
        organization = request.user.profile.organization
    except AttributeError:
        return JsonResponse({
            'success': False,
            'message': 'Usuario no tiene organización asignada'
        }, status=400)
    
    try:
        # Get schedule
        try:
            schedule = DoctorSchedule.objects.get(
                id=schedule_id,
                doctor__profile__organization=organization
            )
        except DoctorSchedule.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Horario no encontrado'
            }, status=404)
        
        # Check if there are future appointments using this schedule
        from datetime import date, timedelta
        today = date.today()
        future_appointments = Appointment.objects.filter(
            doctor=schedule.doctor,
            start_datetime__date__gte=today,
            start_datetime__week_day=schedule.day_of_week + 1,  # Django uses 1=Sunday, 7=Saturday
            status__in=['scheduled', 'confirmed']
        ).count()
        
        if future_appointments > 0:
            return JsonResponse({
                'success': False,
                'message': f'No se puede eliminar este horario porque tiene {future_appointments} citas futuras programadas. Cancele las citas primero.'
            }, status=400)
        
        # Delete schedule
        doctor_name = schedule.doctor.get_full_name()
        day_name = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][schedule.day_of_week]
        schedule.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Horario de {doctor_name} para {day_name} eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)

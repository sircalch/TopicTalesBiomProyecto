from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from datetime import datetime, timedelta

from patients.models import Patient, VitalSigns
from appointments.models import Appointment
from accounts.models import User


@login_required
def index(request):
    """
    Main dashboard view with medical practice KPIs and summary information
    """
    # Get user's organization - handle case where profile doesn't exist
    try:
        organization = request.user.profile.organization
    except AttributeError:
        # If user doesn't have a profile, create a default one or redirect
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(request, "No tienes un perfil organizacional configurado. Contacta al administrador.")
        return redirect('accounts:profile')
    
    # Date ranges for comparisons
    today = timezone.now().date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Basic Stats
    total_patients = Patient.objects.filter(organization=organization, is_active=True).count()
    total_appointments_today = Appointment.objects.filter(
        organization=organization,
        start_datetime__date=today
    ).count()
    
    # Appointments this week
    appointments_this_week = Appointment.objects.filter(
        organization=organization,
        start_datetime__date__gte=this_week_start,
        start_datetime__date__lte=today
    ).count()
    
    # New patients this month
    new_patients_this_month = Patient.objects.filter(
        organization=organization,
        registration_date__date__gte=this_month_start
    ).count()
    
    # Upcoming appointments (next 7 days)
    upcoming_appointments = Appointment.objects.filter(
        organization=organization,
        start_datetime__date__gt=today,
        start_datetime__date__lte=today + timedelta(days=7),
        status__in=['scheduled', 'confirmed']
    ).select_related('patient', 'doctor', 'appointment_type')[:10]
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        organization=organization,
        start_datetime__date=today
    ).select_related('patient', 'doctor', 'appointment_type').order_by('start_datetime')
    
    # Recent patients (last 10 registered)
    recent_patients = Patient.objects.filter(
        organization=organization
    ).order_by('-registration_date')[:8]
    
    # Appointment status distribution for charts
    appointment_status_data = Appointment.objects.filter(
        organization=organization,
        start_datetime__date__gte=this_month_start
    ).values('status').annotate(count=Count('id'))
    
    # Monthly appointments trend (last 6 months)
    monthly_data = []
    for i in range(6):
        month_start = (this_month_start - timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        count = Appointment.objects.filter(
            organization=organization,
            start_datetime__date__gte=month_start,
            start_datetime__date__lte=month_end
        ).count()
        monthly_data.append({
            'month': month_start.strftime('%B'),
            'count': count
        })
    monthly_data.reverse()
    
    # Doctor performance (appointments this month)
    doctor_performance = User.objects.filter(
        role='doctor',
        profile__organization=organization
    ).annotate(
        appointments_count=Count(
            'doctor_appointments',
            filter=Q(doctor_appointments__start_datetime__date__gte=this_month_start)
        )
    ).order_by('-appointments_count')[:5]
    
    # Calculate completion rate for this month
    total_appointments_month = Appointment.objects.filter(
        organization=organization,
        start_datetime__date__gte=this_month_start
    ).count()
    
    completed_appointments_month = Appointment.objects.filter(
        organization=organization,
        start_datetime__date__gte=this_month_start,
        status='completed'
    ).count()
    
    completion_rate = (completed_appointments_month / total_appointments_month * 100) if total_appointments_month > 0 else 0
    
    # No-show rate
    no_show_appointments = Appointment.objects.filter(
        organization=organization,
        start_datetime__date__gte=this_month_start,
        status='no_show'
    ).count()
    
    no_show_rate = (no_show_appointments / total_appointments_month * 100) if total_appointments_month > 0 else 0
    
    # Calculate growth rates and additional metrics
    # Patient growth (this month vs last month)
    last_month_patients = Patient.objects.filter(
        organization=organization,
        registration_date__date__gte=last_month_start,
        registration_date__date__lt=this_month_start
    ).count()
    
    patient_growth = 0
    if last_month_patients > 0:
        patient_growth = ((new_patients_this_month - last_month_patients) / last_month_patients * 100)
    elif new_patients_this_month > 0:
        patient_growth = 100
    
    # Completed appointments today
    completed_today = Appointment.objects.filter(
        organization=organization,
        start_datetime__date=today,
        status='completed'
    ).count()
    
    # Weekly growth
    last_week_start = this_week_start - timedelta(days=7)
    last_week_end = this_week_start - timedelta(days=1)
    appointments_last_week = Appointment.objects.filter(
        organization=organization,
        start_datetime__date__gte=last_week_start,
        start_datetime__date__lte=last_week_end
    ).count()
    
    weekly_growth = 0
    if appointments_last_week > 0:
        weekly_growth = ((appointments_this_week - appointments_last_week) / appointments_last_week * 100)
    elif appointments_this_week > 0:
        weekly_growth = 100
    
    # Monthly new patients growth
    last_month_new_patients = Patient.objects.filter(
        organization=organization,
        registration_date__date__gte=last_month_start,
        registration_date__date__lt=this_month_start
    ).count()
    
    monthly_new_growth = 0
    if last_month_new_patients > 0:
        monthly_new_growth = ((new_patients_this_month - last_month_new_patients) / last_month_new_patients * 100)
    elif new_patients_this_month > 0:
        monthly_new_growth = 100
    
    # Active patients (patients with appointments in last 30 days)
    active_patients = Patient.objects.filter(
        organization=organization,
        appointments__start_datetime__date__gte=today - timedelta(days=30)
    ).distinct().count()
    
    # Total appointments (all time)
    total_appointments = Appointment.objects.filter(organization=organization).count()
    
    # Pending appointments (scheduled/confirmed today)
    pending_appointments = Appointment.objects.filter(
        organization=organization,
        start_datetime__date=today,
        status__in=['scheduled', 'confirmed']
    ).count()
    
    # Active specialties count (simplified)
    active_specialties = 3  # Psychology, Nutrition, General Medicine
    
    # Average satisfaction (mockup for now)
    avg_satisfaction = 4.8
    
    # Medical specialties mock data (will be replaced with real data when specialties are implemented)
    medical_specialties = [
        {
            'name': 'Psicología',
            'icon': 'bi-brain',
            'patient_count': total_patients // 3,
            'appointments_this_week': appointments_this_week // 3
        },
        {
            'name': 'Nutrición',
            'icon': 'bi-apple',
            'patient_count': total_patients // 3,
            'appointments_this_week': appointments_this_week // 3
        },
        {
            'name': 'Medicina General',
            'icon': 'bi-stethoscope',
            'patient_count': total_patients // 3,
            'appointments_this_week': appointments_this_week // 3
        }
    ]
    
    context = {
        'total_patients': total_patients,
        'total_appointments_today': total_appointments_today,
        'appointments_this_week': appointments_this_week,
        'new_patients_this_month': new_patients_this_month,
        'upcoming_appointments': upcoming_appointments,
        'today_appointments': today_appointments,
        'recent_patients': recent_patients,
        'appointment_status_data': list(appointment_status_data),
        'monthly_data': monthly_data,
        'doctor_performance': doctor_performance,
        'completion_rate': round(completion_rate, 1),
        'no_show_rate': round(no_show_rate, 1),
        'organization': organization,
        'subscription': getattr(organization, 'subscription', None),
        # New variables for template
        'patient_growth': round(patient_growth, 1),
        'completed_today': completed_today,
        'weekly_growth': round(weekly_growth, 1),
        'monthly_new_growth': round(monthly_new_growth, 1),
        'active_patients': active_patients,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'active_specialties': active_specialties,
        'avg_satisfaction': avg_satisfaction,
        'medical_specialties': medical_specialties,
        'reschedule_rate': round(7, 1),  # Mock data for now
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def quick_stats(request):
    """
    AJAX endpoint for real-time dashboard stats updates
    """
    from django.http import JsonResponse
    
    try:
        organization = request.user.profile.organization
    except AttributeError:
        return JsonResponse({'error': 'No profile found'}, status=400)
    today = timezone.now().date()
    
    stats = {
        'total_patients': Patient.objects.filter(organization=organization, is_active=True).count(),
        'appointments_today': Appointment.objects.filter(
            organization=organization,
            start_datetime__date=today
        ).count(),
        'pending_appointments': Appointment.objects.filter(
            organization=organization,
            start_datetime__date=today,
            status__in=['scheduled', 'confirmed']
        ).count(),
        'completed_today': Appointment.objects.filter(
            organization=organization,
            start_datetime__date=today,
            status='completed'
        ).count(),
    }
    
    return JsonResponse(stats)


@login_required
def dashboard_refresh(request):
    """
    Refresh dashboard data and return success response
    """
    # This endpoint just confirms the dashboard can be refreshed
    # The actual refresh happens on the frontend by reloading
    return JsonResponse({
        'success': True,
        'message': 'Dashboard data refreshed',
        'timestamp': timezone.now().isoformat()
    })

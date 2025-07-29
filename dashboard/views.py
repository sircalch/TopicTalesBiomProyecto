from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from patients.models import Patient, VitalSigns
from appointments.models import Appointment
from accounts.models import User


@login_required
def index(request):
    """
    Main dashboard view with medical practice KPIs and summary information
    """
    # Get user's organization
    organization = request.user.profile.organization
    
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
        'subscription': organization.subscription,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
def quick_stats(request):
    """
    AJAX endpoint for real-time dashboard stats updates
    """
    from django.http import JsonResponse
    
    organization = request.user.profile.organization
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

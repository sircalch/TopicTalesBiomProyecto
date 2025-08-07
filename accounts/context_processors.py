from django.db import models
from .models import SystemModule, ModulePermission, Organization, Subscription


def sidebar_modules(request):
    """
    Context processor to provide sidebar modules based on user permissions and subscription
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {'sidebar_modules': [], 'user_subscription': None}
    
    try:
        # Get user's organization
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return {'sidebar_modules': [], 'user_subscription': None}
        
        organization = user_profile.organization
        subscription = getattr(organization, 'subscription', None)
        
        if not subscription:
            return {'sidebar_modules': [], 'user_subscription': None}
        
        # Get all available modules for this user and subscription
        available_modules = SystemModule.objects.filter(
            is_active=True,
            parent_module__isnull=True  # Only top-level modules
        ).prefetch_related('submodules')
        
        # Filter modules based on user permissions and subscription
        user_modules = []
        for module in available_modules:
            # Check if module is available for current subscription plan
            if not module.is_available_for_plan(subscription.plan):
                continue
            
            # Check if module is available for current user
            if not module.is_available_for_user(request.user):
                continue
            
            # Check if organization has this module enabled
            try:
                module_permission = ModulePermission.objects.get(
                    organization=organization,
                    module=module
                )
                if not module_permission.is_enabled:
                    continue
            except ModulePermission.DoesNotExist:
                # If no specific permission exists, use default availability
                pass
            
            # Get submodules if any
            submodules = []
            for submodule in module.submodules.filter(is_active=True):
                if (submodule.is_available_for_plan(subscription.plan) and 
                    submodule.is_available_for_user(request.user)):
                    submodules.append(submodule)
            
            module_data = {
                'module': module,
                'submodules': submodules
            }
            user_modules.append(module_data)
        
        # Group modules by category
        grouped_modules = {}
        for module_data in user_modules:
            category = module_data['module'].category
            if category not in grouped_modules:
                grouped_modules[category] = []
            grouped_modules[category].append(module_data)
        
        # Add sidebar-specific context variables
        from patients.models import Patient
        from appointments.models import Appointment
        from .models import Notification
        from django.utils import timezone
        
        today = timezone.now().date()
        
        # Get real notification counts
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False,
            is_dismissed=False
        ).count()
        
        unread_messages = Notification.objects.filter(
            user=request.user,
            notification_type='message',
            is_read=False,
            is_dismissed=False
        ).count()
        
        sidebar_context = {
            'total_patients': Patient.objects.filter(organization=organization, is_active=True).count(),
            'todays_appointments': Appointment.objects.filter(
                organization=organization,
                start_datetime__date=today
            ).count(),
            'pending_notifications': unread_notifications,
            'unread_messages': unread_messages,
        }
        
        return {
            'sidebar_modules': grouped_modules,
            'user_subscription': subscription,
            'organization': organization,
            **sidebar_context
        }
        
    except Exception as e:
        # Log error in production
        print(f"Sidebar context processor error: {e}")
        return {
            'sidebar_modules': [], 
            'user_subscription': None,
            'total_patients': 0,
            'todays_appointments': 0,
            'pending_notifications': 0,
            'unread_messages': 0,
        }


def subscription_features(request):
    """
    Context processor to provide subscription feature flags
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {'subscription_features': {}}
    
    try:
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile:
            return {'subscription_features': {}}
        
        organization = user_profile.organization
        subscription = getattr(organization, 'subscription', None)
        
        if not subscription:
            return {'subscription_features': {}}
        
        # Define feature flags based on subscription plan
        features = {
            'can_access_advanced_reports': subscription.plan in ['MEDIUM', 'ADVANCED'],
            'can_access_all_specialties': subscription.plan == 'ADVANCED',
            'can_use_telemedicine': subscription.plan in ['MEDIUM', 'ADVANCED'],
            'can_manage_equipment': subscription.plan in ['MEDIUM', 'ADVANCED'],
            'can_access_billing': subscription.plan in ['MEDIUM', 'ADVANCED'],
            'can_export_data': subscription.plan in ['MEDIUM', 'ADVANCED'],
            'can_customize_modules': subscription.plan == 'ADVANCED',
            'has_priority_support': subscription.plan == 'ADVANCED',
            'max_patients': subscription.max_patients,
            'max_users': subscription.max_users,
            'current_patients': subscription.current_patients,
            'current_users': subscription.current_users,
            'days_remaining': subscription.days_remaining,
            'is_trial': subscription.is_trial,
            'plan_display': subscription.get_plan_display(),
        }
        
        return {'subscription_features': features}
        
    except Exception as e:
        print(f"Subscription features context processor error: {e}")
        return {
            'subscription_features': {
                'max_patients': 100,
                'current_patients': 0,
                'plan_display': 'Básico'
            }
        }


def language_context(request):
    """Add language context for templates"""
    # Get language from session or default to Spanish
    current_language = request.session.get('django_language', 'es')
    
    # Define translations (using underscore keys for template compatibility)
    translations = {
        'es': {
            'dashboard': 'Panel de Control',
            'patients': 'Pacientes',
            'appointments': 'Citas',
            'medical_records': 'Expedientes Médicos',
            'specialties': 'Especialidades',
            'equipment': 'Equipos',
            'reports': 'Reportes',
            'billing': 'Facturación',
            'settings': 'Configuración',
            'my_profile': 'Mi Perfil',
            'logout': 'Cerrar Sesión',
            'welcome': 'Bienvenido',
            'new_patient': 'Nuevo Paciente',
            'new_appointment': 'Nueva Cita',
            'view_calendar': 'Ver Calendario',
            'view_patients': 'Ver Pacientes',
            'refresh': 'Actualizar',
            'patient_management': 'Gestión de Pacientes',
            'export': 'Exportar',
            'excel': 'Excel',
            'pdf': 'PDF',
            'csv': 'CSV',
            'select_language': 'Seleccionar idioma',
            'patient_management_description': 'Administra y consulta la información de todos los pacientes registrados en el sistema.',
            'medical_practice_summary': 'Aquí tienes un resumen de tu práctica médica para hoy',
        },
        'en': {
            'dashboard': 'Dashboard',
            'patients': 'Patients',
            'appointments': 'Appointments',
            'medical_records': 'Medical Records',
            'specialties': 'Specialties',
            'equipment': 'Equipment',
            'reports': 'Reports',
            'billing': 'Billing',
            'settings': 'Settings',
            'my_profile': 'My Profile',
            'logout': 'Logout',
            'welcome': 'Welcome',
            'new_patient': 'New Patient',
            'new_appointment': 'New Appointment',
            'view_calendar': 'View Calendar',
            'view_patients': 'View Patients',
            'refresh': 'Refresh',
            'patient_management': 'Patient Management',
            'export': 'Export',
            'excel': 'Excel',
            'pdf': 'PDF',
            'csv': 'CSV',
            'select_language': 'Select Language',
            'patient_management_description': 'Manage and consult information for all patients registered in the system.',
            'medical_practice_summary': 'Here you have a summary of your medical practice for today',
        }
    }
    
    return {
        'current_language': current_language,
        'translations': translations.get(current_language, translations['es']),
        'available_languages': [
            {'code': 'es', 'name': 'Español'},
            {'code': 'en', 'name': 'English'}
        ]
    }
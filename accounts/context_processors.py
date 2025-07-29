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
        
        return {
            'sidebar_modules': grouped_modules,
            'user_subscription': subscription,
            'organization': organization
        }
        
    except Exception as e:
        # Log error in production
        return {'sidebar_modules': [], 'user_subscription': None}


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
        return {'subscription_features': {}}
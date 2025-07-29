from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, Subscription, UserProfile, SystemModule, ModulePermission, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Profesional', {
            'fields': ('role', 'phone_number', 'profile_picture', 'professional_license', 'specialty', 'is_active_professional')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Profesional', {
            'fields': ('role', 'phone_number', 'professional_license', 'specialty')
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization Admin"""
    list_display = ('name', 'legal_name', 'tax_id', 'director_name', 'created_at')
    search_fields = ('name', 'legal_name', 'tax_id', 'director_name')
    list_filter = ('created_at',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'legal_name', 'tax_id', 'logo')
        }),
        ('Contacto', {
            'fields': ('address', 'phone', 'email', 'website')
        }),
        ('Dirección Médica', {
            'fields': ('director_name', 'director_license')
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription Admin"""
    list_display = ('organization', 'plan', 'status', 'start_date', 'end_date', 'is_active', 'days_remaining')
    list_filter = ('plan', 'status', 'start_date')
    search_fields = ('organization__name', 'organization__legal_name')
    
    fieldsets = (
        ('Información de Suscripción', {
            'fields': ('organization', 'plan', 'status')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'trial_end_date')
        }),
        ('Límites de Uso', {
            'fields': ('max_patients', 'max_users', 'current_patients', 'current_users')
        }),
        ('Facturación', {
            'fields': ('monthly_price', 'currency')
        }),
    )
    
    readonly_fields = ('current_patients', 'current_users')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile Admin"""
    list_display = ('user', 'organization', 'department', 'position', 'hire_date')
    list_filter = ('organization', 'department', 'hire_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department', 'position')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'organization')
        }),
        ('Información Personal', {
            'fields': ('birth_date', 'emergency_contact', 'emergency_phone')
        }),
        ('Información Laboral', {
            'fields': ('department', 'position', 'hire_date', 'work_schedule')
        }),
        ('Preferencias', {
            'fields': ('language', 'timezone', 'email_notifications', 'sms_notifications')
        }),
    )


@admin.register(SystemModule)
class SystemModuleAdmin(admin.ModelAdmin):
    """System Module Admin"""
    list_display = ('display_name', 'name', 'category', 'min_plan_required', 'is_active', 'order')
    list_filter = ('category', 'min_plan_required', 'is_active', 'requires_medical_license')
    search_fields = ('name', 'display_name', 'description')
    list_editable = ('is_active', 'order')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'display_name', 'description', 'icon', 'url_name')
        }),
        ('Clasificación', {
            'fields': ('category', 'parent_module', 'order')
        }),
        ('Configuración', {
            'fields': ('is_active', 'requires_medical_license', 'min_plan_required')
        }),
        ('Permisos', {
            'fields': ('allowed_roles',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent_module')


class ModulePermissionInline(admin.TabularInline):
    """Module Permission Inline"""
    model = ModulePermission
    extra = 0
    fields = ('module', 'is_enabled', 'custom_settings')
    readonly_fields = ('module',)


@admin.register(ModulePermission)
class ModulePermissionAdmin(admin.ModelAdmin):
    """Module Permission Admin"""
    list_display = ('organization', 'module', 'is_enabled', 'updated_at')
    list_filter = ('is_enabled', 'module__category', 'organization')
    search_fields = ('organization__name', 'module__display_name', 'module__name')
    list_editable = ('is_enabled',)
    
    fieldsets = (
        ('Permiso', {
            'fields': ('organization', 'module', 'is_enabled')
        }),
        ('Configuración Personalizada', {
            'fields': ('custom_settings',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit Log Admin"""
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'description', 'model_name', 'object_id')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'description', 'ip_address', 'user_agent', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Customize admin site
admin.site.site_header = "TopicTales Biomédica - Administración"
admin.site.site_title = "TopicTales Biomédica"
admin.site.index_title = "Panel de Administración"

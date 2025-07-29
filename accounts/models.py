from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings

class User(AbstractUser):
    """
    Custom User model for TopicTales Biomédica
    Extends Django's AbstractUser with medical-specific fields
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('doctor', 'Médico'),
        ('receptionist', 'Recepcionista'),
        ('patient', 'Paciente'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='receptionist')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Formato: '+999999999'. Hasta 15 dígitos.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Professional Information (for medical staff)
    professional_license = models.CharField(max_length=50, blank=True, help_text="Cédula profesional")
    specialty = models.CharField(max_length=100, blank=True)
    is_active_professional = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_medical_staff(self):
        return self.role in ['doctor', 'admin']
    
    @property
    def is_administrative_staff(self):
        return self.role in ['admin', 'receptionist']
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


class Organization(models.Model):
    """
    Medical organization/clinic information
    """
    name = models.CharField(max_length=200, verbose_name="Nombre de la organización")
    legal_name = models.CharField(max_length=200, verbose_name="Razón social")
    tax_id = models.CharField(max_length=50, verbose_name="RFC/NIT", unique=True)
    address = models.TextField(verbose_name="Dirección")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Email")
    website = models.URLField(blank=True, verbose_name="Sitio web")
    logo = models.ImageField(upload_to='organizations/', blank=True, null=True)
    
    # Business Information
    director_name = models.CharField(max_length=200, verbose_name="Director médico")
    director_license = models.CharField(max_length=50, verbose_name="Cédula del director")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"


class Subscription(models.Model):
    """
    Subscription plan management for TopicTales Biomédica
    """
    PLAN_CHOICES = [
        ('BASIC', 'Plan Básico'),
        ('MEDIUM', 'Plan Medio'),
        ('ADVANCED', 'Plan Avanzado'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('suspended', 'Suspendido'),
        ('cancelled', 'Cancelado'),
    ]
    
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='BASIC')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Subscription dates
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    trial_end_date = models.DateTimeField(blank=True, null=True)
    
    # Usage limits
    max_patients = models.IntegerField(default=100)
    max_users = models.IntegerField(default=2)
    current_patients = models.IntegerField(default=0)
    current_users = models.IntegerField(default=1)
    
    # Billing
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='MXN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.organization.name} - {self.get_plan_display()}"
    
    @property
    def is_active(self):
        return self.status == 'active' and self.end_date > timezone.now()
    
    @property
    def is_trial(self):
        return self.trial_end_date and timezone.now() < self.trial_end_date
    
    @property
    def days_remaining(self):
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0
    
    def has_feature(self, feature_name):
        """
        Check if the current subscription plan has a specific feature
        """
        plan_features = settings.SUBSCRIPTION_PLANS.get(self.plan, {}).get('features', [])
        return feature_name in plan_features
    
    def can_add_patient(self):
        """
        Check if organization can add more patients
        """
        if self.max_patients == -1:  # Unlimited
            return True
        return self.current_patients < self.max_patients
    
    def can_add_user(self):
        """
        Check if organization can add more users
        """
        if self.max_users == -1:  # Unlimited
            return True
        return self.current_users < self.max_users
    
    # Template-friendly feature properties
    @property
    def has_medical_history(self):
        return self.has_feature('medical_history')
    
    @property
    def has_all_specialty_modules(self):
        return self.has_feature('all_specialty_modules')
    
    @property
    def has_equipment_management(self):
        return self.has_feature('equipment_management')
    
    @property
    def has_billing_module(self):
        return self.has_feature('billing_module')
    
    @property
    def has_advanced_reports(self):
        return self.has_feature('advanced_reports')
    
    @property
    def has_business_dashboard(self):
        return self.has_feature('business_dashboard')
    
    class Meta:
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    
    # Personal Information
    birth_date = models.DateField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Work Information
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField(blank=True, null=True)
    work_schedule = models.JSONField(default=dict, blank=True)  # Store schedule as JSON
    
    # Preferences
    language = models.CharField(max_length=10, default='es')
    timezone = models.CharField(max_length=50, default='America/Mexico_City')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.get_full_name()}"
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"


class SystemModule(models.Model):
    """
    System modules available in TopicTales Biomédica
    """
    CATEGORY_CHOICES = [
        ('core', 'Módulos Básicos'),
        ('medical', 'Especialidades Médicas'),
        ('admin', 'Administración'),
        ('reports', 'Reportes y Analytics'),
        ('communication', 'Comunicación'),
        ('integration', 'Integraciones'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre del módulo")
    display_name = models.CharField(max_length=100, verbose_name="Nombre para mostrar")
    description = models.TextField(verbose_name="Descripción")
    icon = models.CharField(max_length=50, default='fas fa-cog', verbose_name="Icono FontAwesome")
    url_name = models.CharField(max_length=100, blank=True, verbose_name="Nombre de URL")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='core')
    
    # Configuration
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    requires_medical_license = models.BooleanField(default=False, verbose_name="Requiere licencia médica")
    min_plan_required = models.CharField(max_length=20, choices=Subscription.PLAN_CHOICES, default='BASIC')
    
    # Display order and grouping
    order = models.IntegerField(default=0, verbose_name="Orden de visualización")
    parent_module = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='submodules')
    
    # Permissions
    allowed_roles = models.JSONField(default=list, verbose_name="Roles permitidos")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.display_name
    
    def is_available_for_plan(self, plan):
        """Check if module is available for a specific subscription plan"""
        plan_hierarchy = {'BASIC': 1, 'MEDIUM': 2, 'ADVANCED': 3}
        return plan_hierarchy.get(plan, 0) >= plan_hierarchy.get(self.min_plan_required, 0)
    
    def is_available_for_user(self, user):
        """Check if module is available for a specific user"""
        if not self.is_active:
            return False
        
        # Check role permissions
        if self.allowed_roles and user.role not in self.allowed_roles:
            return False
        
        # Check medical license requirement
        if self.requires_medical_license and not user.is_medical_staff:
            return False
        
        return True
    
    class Meta:
        verbose_name = "Módulo del Sistema"
        verbose_name_plural = "Módulos del Sistema"
        ordering = ['category', 'order', 'display_name']


class ModulePermission(models.Model):
    """
    Module permissions per organization
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='module_permissions')
    module = models.ForeignKey(SystemModule, on_delete=models.CASCADE, related_name='permissions')
    is_enabled = models.BooleanField(default=True, verbose_name="Habilitado")
    custom_settings = models.JSONField(default=dict, blank=True, verbose_name="Configuraciones personalizadas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.organization.name} - {self.module.display_name}"
    
    class Meta:
        verbose_name = "Permiso de Módulo"
        verbose_name_plural = "Permisos de Módulos"
        unique_together = ['organization', 'module']


class AuditLog(models.Model):
    """
    Audit log for tracking user actions in the medical system
    """
    ACTION_CHOICES = [
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('view', 'Ver'),
        ('login', 'Iniciar sesión'),
        ('logout', 'Cerrar sesión'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)  # Name of the model affected
    object_id = models.CharField(max_length=100, blank=True)  # ID of the object affected
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.timestamp}"
    
    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-timestamp']

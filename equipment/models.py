from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

class EquipmentCategory(models.Model):
    """Categorías de equipos médicos"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Categoría de Equipo"
        verbose_name_plural = "Categorías de Equipos"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Location(models.Model):
    """Ubicaciones donde se puede colocar el equipo"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    floor = models.CharField(max_length=50, blank=True, verbose_name="Piso")
    room_number = models.CharField(max_length=50, blank=True, verbose_name="Número de Habitación")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ['name']
    
    def __str__(self):
        if self.room_number:
            return f"{self.name} - Habitación {self.room_number}"
        return self.name

class Supplier(models.Model):
    """Proveedores de equipos médicos"""
    name = models.CharField(max_length=200, verbose_name="Nombre")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Persona de Contacto")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    address = models.TextField(blank=True, verbose_name="Dirección")
    website = models.URLField(blank=True, verbose_name="Sitio Web")
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Equipment(models.Model):
    """Equipos médicos del centro de salud"""
    STATUS_CHOICES = [
        ('operational', 'Operativo'),
        ('maintenance', 'En Mantenimiento'),
        ('repair', 'En Reparación'),
        ('out_of_service', 'Fuera de Servicio'),
        ('retired', 'Retirado'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excelente'),
        ('good', 'Bueno'),
        ('fair', 'Regular'),
        ('poor', 'Malo'),
        ('critical', 'Crítico'),
    ]
    
    # Información básica
    name = models.CharField(max_length=200, verbose_name="Nombre del Equipo")
    model = models.CharField(max_length=100, verbose_name="Modelo")
    brand = models.CharField(max_length=100, verbose_name="Marca")
    serial_number = models.CharField(max_length=100, unique=True, verbose_name="Número de Serie")
    asset_tag = models.CharField(max_length=50, unique=True, blank=True, verbose_name="Etiqueta de Activo")
    
    # Categorización
    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Proveedor")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name="Ubicación")
    
    # Estado y condición
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational', verbose_name="Estado")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good', verbose_name="Condición")
    
    # Información financiera
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Precio de Compra")
    purchase_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Compra")
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name="Vencimiento de Garantía")
    
    # Especificaciones técnicas
    specifications = models.JSONField(default=dict, blank=True, verbose_name="Especificaciones Técnicas")
    manual_url = models.URLField(blank=True, verbose_name="URL del Manual")
    
    # Información adicional
    description = models.TextField(blank=True, verbose_name="Descripción")
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    # Fechas de mantenimiento
    last_maintenance = models.DateField(null=True, blank=True, verbose_name="Último Mantenimiento")
    next_maintenance = models.DateField(null=True, blank=True, verbose_name="Próximo Mantenimiento")
    maintenance_frequency_days = models.PositiveIntegerField(default=90, verbose_name="Frecuencia de Mantenimiento (días)")
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.model} ({self.serial_number})"
    
    @property
    def is_warranty_valid(self):
        """Verifica si la garantía sigue vigente"""
        if self.warranty_expiry:
            return self.warranty_expiry >= date.today()
        return False
    
    @property
    def warranty_days_remaining(self):
        """Días restantes de garantía"""
        if self.warranty_expiry and self.is_warranty_valid:
            return (self.warranty_expiry - date.today()).days
        return 0
    
    @property
    def maintenance_due(self):
        """Verifica si el mantenimiento está vencido"""
        if self.next_maintenance:
            return self.next_maintenance <= date.today()
        return False
    
    @property
    def days_until_maintenance(self):
        """Días hasta el próximo mantenimiento"""
        if self.next_maintenance:
            return (self.next_maintenance - date.today()).days
        return None
    
    def calculate_next_maintenance(self):
        """Calcula la fecha del próximo mantenimiento"""
        if self.last_maintenance:
            return self.last_maintenance + timedelta(days=self.maintenance_frequency_days)
        elif self.purchase_date:
            return self.purchase_date + timedelta(days=self.maintenance_frequency_days)
        return None
    
    def save(self, *args, **kwargs):
        # Generar asset_tag automáticamente si no se proporciona
        if not self.asset_tag:
            count = Equipment.objects.count() + 1
            self.asset_tag = f"EQ-{count:05d}"
        
        # Calcular próximo mantenimiento automáticamente
        if not self.next_maintenance:
            self.next_maintenance = self.calculate_next_maintenance()
        
        super().save(*args, **kwargs)

class MaintenanceRecord(models.Model):
    """Registros de mantenimiento de equipos"""
    MAINTENANCE_TYPE_CHOICES = [
        ('preventive', 'Preventivo'),
        ('corrective', 'Correctivo'),
        ('emergency', 'Emergencia'),
        ('calibration', 'Calibración'),
        ('inspection', 'Inspección'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Programado'),
        ('in_progress', 'En Progreso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
        ('postponed', 'Pospuesto'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name="Equipo")
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES, verbose_name="Tipo de Mantenimiento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Estado")
    
    # Fechas
    scheduled_date = models.DateField(verbose_name="Fecha Programada")
    completed_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Finalización")
    
    # Detalles del mantenimiento
    description = models.TextField(verbose_name="Descripción del Trabajo")
    work_performed = models.TextField(blank=True, verbose_name="Trabajo Realizado")
    parts_replaced = models.TextField(blank=True, verbose_name="Partes Reemplazadas")
    
    # Personal
    technician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_work', verbose_name="Técnico")
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='supervised_maintenance', verbose_name="Supervisor")
    
    # Costos
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo de Mano de Obra")
    parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo de Partes")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo Total")
    
    # Información adicional
    notes = models.TextField(blank=True, verbose_name="Notas")
    next_maintenance_date = models.DateField(null=True, blank=True, verbose_name="Próximo Mantenimiento Recomendado")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Registro de Mantenimiento"
        verbose_name_plural = "Registros de Mantenimiento"
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"{self.equipment.name} - {self.get_maintenance_type_display()} ({self.scheduled_date})"
    
    def save(self, *args, **kwargs):
        # Calcular costo total
        self.total_cost = self.labor_cost + self.parts_cost
        
        # Si se completa el mantenimiento, actualizar fechas en el equipo
        if self.status == 'completed' and self.completed_date:
            self.equipment.last_maintenance = self.completed_date
            if self.next_maintenance_date:
                self.equipment.next_maintenance = self.next_maintenance_date
            else:
                self.equipment.next_maintenance = self.equipment.calculate_next_maintenance()
            self.equipment.save()
        
        super().save(*args, **kwargs)

class EquipmentUsageLog(models.Model):
    """Registro de uso de equipos"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='usage_logs', verbose_name="Equipo")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    
    start_time = models.DateTimeField(verbose_name="Inicio de Uso")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Fin de Uso")
    
    purpose = models.CharField(max_length=200, verbose_name="Propósito del Uso")
    patient_name = models.CharField(max_length=200, blank=True, verbose_name="Paciente (si aplica)")
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Registro de Uso"
        verbose_name_plural = "Registros de Uso"
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.equipment.name} - {self.user.get_full_name()} ({self.start_time.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def duration(self):
        """Duración del uso en minutos"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return delta.total_seconds() / 60
        return None

class CalibrationRecord(models.Model):
    """Registros de calibración de equipos"""
    STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('completed', 'Completada'),
        ('failed', 'Fallida'),
        ('cancelled', 'Cancelada'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='calibration_records', verbose_name="Equipo")
    
    # Fechas
    scheduled_date = models.DateField(verbose_name="Fecha Programada")
    performed_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Realización")
    next_calibration_date = models.DateField(null=True, blank=True, verbose_name="Próxima Calibración")
    
    # Estado y resultados
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Estado")
    passed = models.BooleanField(null=True, blank=True, verbose_name="Pasó la Calibración")
    
    # Detalles técnicos
    calibration_standards = models.TextField(blank=True, verbose_name="Estándares de Calibración")
    measurements_before = models.JSONField(default=dict, blank=True, verbose_name="Mediciones Antes")
    measurements_after = models.JSONField(default=dict, blank=True, verbose_name="Mediciones Después")
    adjustments_made = models.TextField(blank=True, verbose_name="Ajustes Realizados")
    
    # Personal y costos
    technician = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Técnico")
    external_company = models.CharField(max_length=200, blank=True, verbose_name="Empresa Externa")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo")
    
    # Certificación
    certificate_number = models.CharField(max_length=100, blank=True, verbose_name="Número de Certificado")
    certificate_file = models.FileField(upload_to='calibration_certificates/', blank=True, verbose_name="Archivo de Certificado")
    
    notes = models.TextField(blank=True, verbose_name="Notas")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Registro de Calibración"
        verbose_name_plural = "Registros de Calibración"
        ordering = ['-scheduled_date']
    
    def __str__(self):
        return f"Calibración {self.equipment.name} - {self.scheduled_date}"

class EquipmentAlert(models.Model):
    """Alertas y notificaciones relacionadas con equipos"""
    ALERT_TYPE_CHOICES = [
        ('maintenance_due', 'Mantenimiento Vencido'),
        ('calibration_due', 'Calibración Vencida'),
        ('warranty_expiring', 'Garantía por Vencer'),
        ('malfunction', 'Mal Funcionamiento'),
        ('out_of_service', 'Fuera de Servicio'),
        ('custom', 'Personalizada'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='alerts', verbose_name="Equipo")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES, verbose_name="Tipo de Alerta")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="Prioridad")
    
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    is_resolved = models.BooleanField(default=False, verbose_name="Resuelta")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Resolución")
    resolved_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Resuelto por")
    
    class Meta:
        verbose_name = "Alerta de Equipo"
        verbose_name_plural = "Alertas de Equipos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.equipment.name} - {self.title}"
    
    def resolve(self, user):
        """Marca la alerta como resuelta"""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.save()

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Report(models.Model):
    """Modelo para almacenar reportes generados"""
    REPORT_TYPES = [
        ('patients', 'Reporte de Pacientes'),
        ('appointments', 'Reporte de Citas'),
        ('financial', 'Reporte Financiero'),
        ('analytics', 'Análisis Avanzado'),
        ('medical', 'Reporte Médico'),
        ('custom', 'Reporte Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="Tipo de Reporte")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Estado")
    
    # Filtros y parámetros del reporte (JSON)
    filters = models.JSONField(default=dict, blank=True, verbose_name="Filtros")
    parameters = models.JSONField(default=dict, blank=True, verbose_name="Parámetros")
    
    # Fechas
    date_from = models.DateField(null=True, blank=True, verbose_name="Fecha Desde")
    date_to = models.DateField(null=True, blank=True, verbose_name="Fecha Hasta")
    
    # Usuario que creó el reporte
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    # Archivo del reporte generado
    file_path = models.FileField(upload_to='reports/', null=True, blank=True, verbose_name="Archivo")
    file_format = models.CharField(max_length=10, default='pdf', verbose_name="Formato")
    
    # Configuración de programación automática
    is_scheduled = models.BooleanField(default=False, verbose_name="Programado")
    schedule_frequency = models.CharField(max_length=20, blank=True, verbose_name="Frecuencia")
    next_run = models.DateTimeField(null=True, blank=True, verbose_name="Próxima Ejecución")
    
    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"
    
    @property
    def is_ready(self):
        """Verifica si el reporte está listo para descargar"""
        return self.status == 'completed' and self.file_path
    
    @property
    def file_size(self):
        """Obtiene el tamaño del archivo en bytes"""
        if self.file_path:
            try:
                return self.file_path.size
            except:
                return 0
        return 0

class ReportTemplate(models.Model):
    """Plantillas predefinidas para reportes"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    report_type = models.CharField(max_length=20, choices=Report.REPORT_TYPES, verbose_name="Tipo")
    
    # Configuración de la plantilla
    template_config = models.JSONField(default=dict, verbose_name="Configuración")
    default_filters = models.JSONField(default=dict, blank=True, verbose_name="Filtros por Defecto")
    
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_public = models.BooleanField(default=False, verbose_name="Público")
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Plantilla de Reporte"
        verbose_name_plural = "Plantillas de Reportes"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ReportShare(models.Model):
    """Compartir reportes con otros usuarios"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Compartido con")
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_reports', verbose_name="Compartido por")
    
    can_edit = models.BooleanField(default=False, verbose_name="Puede Editar")
    can_download = models.BooleanField(default=True, verbose_name="Puede Descargar")
    
    shared_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compartición")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira el")
    
    class Meta:
        verbose_name = "Reporte Compartido"
        verbose_name_plural = "Reportes Compartidos"
        unique_together = ['report', 'shared_with']
    
    def __str__(self):
        return f"{self.report.title} compartido con {self.shared_with.get_full_name()}"
    
    @property
    def is_expired(self):
        """Verifica si el compartir ha expirado"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
